from django.db import models
from django.utils import timezone
from datetime import timedelta

class Pill(models.Model):
    container_id = models.IntegerField(unique=True) 
    name = models.CharField(max_length=100)
    count = models.IntegerField(default=0)
    interval_value = models.IntegerField(default=8)
    interval_unit = models.CharField(max_length=20, default='hour')
    last_taken = models.DateTimeField(null=True, blank=True)
    next_expected_intake = models.DateTimeField(null=True, blank=True)
    is_notified = models.BooleanField(default=False) 
    is_active = models.BooleanField(default=True) 

    def update_next_intake(self):
        now = timezone.now()
        self.last_taken = now
        if self.interval_unit == 'minute':
                self.next_expected_intake = now + timedelta(minutes=self.interval_value)
        elif self.interval_unit == 'hour':
                self.next_expected_intake = now + timedelta(hours=self.interval_value)
        elif self.interval_unit == 'day':
                self.next_expected_intake = now + timedelta(days=self.interval_value)
        self.is_notified = False
        self.save()

    def __str__(self):
        return f"Container {self.container_id}: {self.name}"

class History(models.Model):
    pill = models.ForeignKey(Pill, on_delete=models.SET_NULL, null=True)
    pill_name = models.CharField(max_length=200) 
    timestamp = models.DateTimeField(auto_now_add=True)
    count_after_intake = models.IntegerField()

    def __str__(self):
        return f"{self.pill_name} at {self.timestamp}"
    
class ExpoPushToken(models.Model):
    token = models.CharField(max_length=255, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.token