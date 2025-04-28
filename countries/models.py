from django.db import models
from django.contrib.auth.models import User

class Country(models.Model):
    name = models.CharField(max_length=100)
    iso_code = models.CharField(max_length=3, unique=True)
    
    class Meta:
        verbose_name_plural = "Countries"
        ordering = ['name']
    
    def __str__(self):
        return f"{self.name} ({self.iso_code})"

class Visit(models.Model):
    STATUS_CHOICES = [
        ('visited', 'Visited'),
        ('want_to_visit', 'Want to Visit'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='visits')
    country = models.ForeignKey(Country, on_delete=models.CASCADE, related_name='visits')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['user', 'country']
        ordering = ['-updated_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.country.name} ({self.status})"