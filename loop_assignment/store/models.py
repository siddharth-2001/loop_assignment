from django.db import models

# Create your models here.

class Store(models.Model):
    
    store_id = models.CharField(max_length=100, primary_key=True)
    created_at = models.DateTimeField()

    def __str__(self):
        
        return f"{self.store_id}"
    
    class Meta:
        indexes =[
             models.Index(fields=['store_id'])
        ]
    

class StoreStatus(models.Model):
    status_id = models.CharField(max_length=200, primary_key=True)
    store = models.ForeignKey(Store, on_delete=models.CASCADE)
    timestamp_utc = models.DateTimeField()
    status = models.CharField(max_length=10)  # Assuming "active" or "inactive"

    def __str__(self):
        return f"{self.store} - {self.timestamp_utc} - {self.status}"  
    
    class Meta:
        indexes = [
            models.Index(fields=['store'])
        ]
    

class BusinessHours(models.Model):
    hours_id = models.CharField(max_length=200, primary_key=True)
    store = models.ForeignKey(Store, on_delete=models.CASCADE)
    day_of_week = models.PositiveIntegerField()  # 0=Monday, 1=Tuesday, ..., 6=Sunday
    start_time_local = models.TimeField()
    end_time_local = models.TimeField()

    def __str__(self):
        return f"{self.store} - {self.day_of_week} - {self.start_time_local} to {self.end_time_local}"
    
    class Meta:
        indexes = [
            models.Index(fields=['store'])
        ]

class Timezone(models.Model):
    store = models.OneToOneField(Store, on_delete=models.CASCADE, primary_key=True)
    timezone_str = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.store} - {self.timezone_str}"
    
    class Meta:
        indexes = [
            models.Index(fields=['store'])
        ]