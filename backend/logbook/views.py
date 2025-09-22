# Create your views here.
# from rest_framework import viewsets
# from .models import DriverLog, LogEntry
# from .serializers import DriverLogSerializer, LogEntrySerializer

# class DriverLogViewSet(viewsets.ModelViewSet):
#     queryset = DriverLog.objects.all()
#     serializer_class = DriverLogSerializer

# class LogEntryViewSet(viewsets.ModelViewSet):
#     queryset = LogEntry.objects.all()
#     serializer_class = LogEntrySerializer


import os
import requests
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
import random

ORS_API_KEY = os.getenv("ORS_API_KEY")  # load from environment variable


class DriverLogView(APIView):
    def get(self, request):
        # Mocked data 
        data = {
            "id": 1,
            "date": "2025-09-22",
            "driver_name": "John Doe",
            "tractor_number": "TX-123",
            "trailer_number": "TR-456",
            "total_miles": 300,
            "entries": [
                {"time": "08:00", "duty_status": "ON_DUTY", "location": "Chicago", "remarks": "Pre-trip"},
                {"time": "09:00", "duty_status": "DRIVING", "location": "I-90", "remarks": "Started driving"},
                {"time": "12:00", "duty_status": "OFF_DUTY", "location": "Rest Area", "remarks": "Lunch break"},
            ]
        }
        print("GET /logs → sending mocked log data")
        return Response(data, status=status.HTTP_200_OK)

    def post(self, request):
        print("POST /logs → received data:", request.data)
        return Response({"message": "Log received", "data": request.data}, status=status.HTTP_201_CREATED)


class TripPlannerView(APIView):
    def post(self, request):
        """
        Takes trip inputs and returns:
        - Route info (via OpenRouteService if available)
        - Generated daily log sheet entries (multi-day if needed)
        """
        data = request.data
        current_location = data.get("current_location", "Chicago")
        pickup_location = data.get("pickup_location", "Cleveland")
        dropoff_location = data.get("dropoff_location", "New York")
        cycle_used = int(data.get("cycle_used", 0))

        print("POST /trip →", data)

        # Default mocked route info
        distance_miles = random.randint(150, 2000)  # allow longer trips
        base_hours = random.randint(3, 10)

        # Fuel stops: one every 1000 miles
        num_fuel_stops = distance_miles // 1000
        fuel_stops = [
            f"Fuel Stop #{i+1} at ~{(i+1)*1000} miles" for i in range(num_fuel_stops)
        ]
        if not fuel_stops:
            fuel_stops = ["None required for this trip"]

        # Estimated hours (add pickup + dropoff = 2 hrs)
        est_hours = base_hours + 2

        route_info = {
            "from": current_location,
            "pickup": pickup_location,
            "dropoff": dropoff_location,
            "distance_miles": distance_miles,
            "fuel_stops": fuel_stops,
            "est_hours": est_hours
        }

        # Try calling OpenRouteService
        if ORS_API_KEY:
            try:
                url = "https://api.openrouteservice.org/v2/directions/driving-car"
                params = {
                    "api_key": ORS_API_KEY,
                    "start": "-87.6298,41.8781",  
                    "end": "-74.0060,40.7128",
                }
                res = requests.get(url, params=params)
                route_data = res.json()

                distance_km = route_data["features"][0]["properties"]["summary"]["distance"] / 1000
                duration_hr = route_data["features"][0]["properties"]["summary"]["duration"] / 3600

                distance_miles = round(distance_km * 0.621371, 2)

                # Recalculate fuel stops with actual distance
                num_fuel_stops = int(distance_miles) // 1000
                fuel_stops = [
                    f"Fuel Stop #{i+1} at ~{(i+1)*1000} miles" for i in range(num_fuel_stops)
                ]
                if not fuel_stops:
                    fuel_stops = ["None required for this trip"]

                est_hours = round(duration_hr, 2) + 2

                route_info = {
                    "from": current_location,
                    "pickup": pickup_location,
                    "dropoff": dropoff_location,
                    "distance_miles": distance_miles,
                    "fuel_stops": fuel_stops,
                    "est_hours": est_hours,
                }

            except Exception as e:
                print("ORS API error → fallback to mocked route:", e)

        # === Generate Log Entries (multi-day if long trip) ===
        hours_remaining = route_info["est_hours"]
        day = 1
        entries = []

        while hours_remaining > 0:
            daily_hours = min(11, hours_remaining)  # Max 11 hrs driving per day
            entries.append({
                "day": day,
                "logs": [
                    {"time": "08:00", "duty_status": "ON_DUTY", "location": pickup_location if day == 1 else "Hotel", "remarks": "Start of day"},
                    {"time": "09:00", "duty_status": "DRIVING", "location": "On the road", "remarks": f"Driving... Day {day}"},
                    {"time": "12:00", "duty_status": "OFF_DUTY", "location": "Rest Area", "remarks": "Lunch Break"},
                    {"time": "13:00", "duty_status": "DRIVING", "location": "On the road", "remarks": "Continue trip"},
                    {"time": f"{8+int(daily_hours)}:00", "duty_status": "OFF_DUTY", "location": "Hotel", "remarks": "End of driving day"},
                ]
            })
            hours_remaining -= daily_hours
            day += 1

        response_data = {
            "driver": "John Doe",
            "cycle_used": cycle_used,
            "route_info": route_info,
            "entries": entries
        }

        return Response(response_data, status=status.HTTP_200_OK)
