from rest_framework import serializers
from .models import (
    Country, Visit, TravelPlan, TravelJournal, 
    CountryInfo, Achievement, TravelGroup, TravelTip, TravelPhoto
)

class CountrySerializer(serializers.ModelSerializer):
    class Meta:
        model = Country
        fields = ['id', 'name', 'iso_code', 'continent', 'region']

class TravelPhotoSerializer(serializers.ModelSerializer):
    class Meta:
        model = TravelPhoto
        fields = ['id', 'image', 'caption', 'location', 'taken_date', 'created_at']
    
    def validate_image(self, value):
        """Validate image size and format"""
        if value.size > 10 * 1024 * 1024:  # 10MB limit
            raise serializers.ValidationError("Image size cannot exceed 10MB")
        return value

class VisitSerializer(serializers.ModelSerializer):
    country_details = CountrySerializer(source='country', read_only=True)
    
    class Meta:
        model = Visit
        fields = ['id', 'user', 'country', 'status', 'created_at', 'country_details']
        read_only_fields = ['user']

class TravelPlanSerializer(serializers.ModelSerializer):
    country = CountrySerializer()
    
    class Meta:
        model = TravelPlan
        fields = ['id', 'country', 'planned_date', 'budget', 'notes', 'created_at']

class TravelJournalSerializer(serializers.ModelSerializer):
    country = CountrySerializer()
    photos = TravelPhotoSerializer(many=True, read_only=True)
    
    class Meta:
        model = TravelJournal
        fields = ['id', 'country', 'visit_date', 'title', 'content', 'photos', 'rating', 'created_at']
    
    def validate_rating(self, value):
        """Ensure rating is between 1 and 5"""
        if not 1 <= value <= 5:
            raise serializers.ValidationError("Rating must be between 1 and 5")
        return value

class CountryInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = CountryInfo
        fields = ['capital', 'population', 'languages', 'currency', 'best_time_to_visit', 'visa_requirements']

class AchievementSerializer(serializers.ModelSerializer):
    class Meta:
        model = Achievement
        fields = ['id', 'name', 'description', 'icon', 'requirement_count', 'achievement_type']

class TravelGroupSerializer(serializers.ModelSerializer):
    members = serializers.StringRelatedField(many=True)
    planned_destinations = CountrySerializer(many=True)
    
    class Meta:
        model = TravelGroup
        fields = ['id', 'name', 'members', 'description', 'planned_destinations', 'created_at']

class TravelTipSerializer(serializers.ModelSerializer):
    upvotes_count = serializers.SerializerMethodField()
    
    class Meta:
        model = TravelTip
        fields = ['id', 'country', 'category', 'content', 'upvotes_count']
    
    def get_upvotes_count(self, obj):
        return obj.upvotes.count()