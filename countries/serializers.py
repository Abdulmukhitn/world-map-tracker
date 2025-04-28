from rest_framework import serializers
from .models import Country, Visit

class CountrySerializer(serializers.ModelSerializer):
    class Meta:
        model = Country
        fields = ['name', 'iso_code']

class VisitSerializer(serializers.ModelSerializer):
    country = CountrySerializer()
    
    class Meta:
        model = Visit
        fields = ['country', 'status', 'created_at']  # Changed visited_date to created_at