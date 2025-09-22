# from django.contrib import admin
# from django.urls import path, include

# urlpatterns = [
#     path('admin/', admin.site.urls),
#     path('', include('logbook.urls'))
# ]


from django.urls import path
from logbook.views import TripPlannerView
from django.http import JsonResponse

# Simple root/home view to confirm API is running
def home(request):
    return JsonResponse({"message": "Driver Logbook API is running!"})

urlpatterns = [
    path('', home, name='home'),         # Root path returns a JSON message
    path('trip/', TripPlannerView.as_view(), name='trip'),  # Trip planner API
]
