# from django.urls import path, include
# from rest_framework.routers import DefaultRouter
# from .views import DriverLogViewSet, LogEntryViewSet

# router = DefaultRouter()
# router.register(r'logs', DriverLogViewSet)
# router.register(r'entries', LogEntryViewSet)

# urlpatterns = [
#     path('', include(router.urls))
# ]

from django.urls import path
from .views import DriverLogView, TripPlannerView

urlpatterns = [
    path('logs/', DriverLogView.as_view()),
    path('trip/', TripPlannerView.as_view()), 
]
