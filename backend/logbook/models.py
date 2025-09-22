# Create your models here.
from django.db import models

class DriverLog(models.Model):
    date = models.DateField()
    driver_name = models.CharField(max_length=100)
    tractor_number = models.CharField(max_length=50, blank=True)
    trailer_number = models.CharField(max_length=50, blank=True)
    total_miles = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.driver_name} - {self.date}"
    

class LogEntry(models.Model):
    log = models.ForeignKey(DriverLog, related_name="entries", on_delete=models.CASCADE)
    time = models.TimeField()
    duty_status = models.CharField(max_length=20, choices=[
        ("OFF_DUTY", "Off Duty"),
        ("SLEEPER", "Sleeper Berth"),
        ("DRIVING", "Driving"),
        ("ON_DUTY", "On Duty (not driving)")
    ])
    location = models.CharField(max_length=100)
    remarks = models.TextField(blank=True)

