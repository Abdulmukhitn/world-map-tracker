from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

class Country(models.Model):
    name = models.CharField(max_length=100)
    iso_code = models.CharField(max_length=3, unique=True)
    continent = models.CharField(
        max_length=50,
        choices=[
            ('AF', 'Africa'),
            ('AS', 'Asia'),
            ('EU', 'Europe'),
            ('NA', 'North America'),
            ('SA', 'South America'),
            ('OC', 'Oceania'),
            ('AN', 'Antarctica')
        ],
        default='EU'  # Adding default value
    )
    region = models.CharField(max_length=100, default='Unknown')  # Adding default value
    
    class Meta:
        verbose_name_plural = "countries"
        ordering = ['name']
    
    def __str__(self):
        return self.name

class Visit(models.Model):
    STATUS_CHOICES = [
        ('visited', 'Visited'),
        ('want_to_visit', 'Want to Visit'),
    ]
    
    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='visits'
    )
    country = models.ForeignKey(
        Country, 
        on_delete=models.CASCADE, 
        related_name='visits'
    )
    status = models.CharField(
        max_length=20, 
        choices=STATUS_CHOICES,
        db_index=True  # Add index for better query performance
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['user', 'country']
        ordering = ['-updated_at']
        indexes = [
            models.Index(fields=['user', 'status']),  # Add composite index
        ]
    
    def clean(self):
        if self.status not in dict(self.STATUS_CHOICES):
            raise ValidationError({
                'status': f'Invalid status. Must be one of: {", ".join(dict(self.STATUS_CHOICES).keys())}'
            })
    
    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.user.username} - {self.country.name} ({self.status})"

class TravelPlan(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    country = models.ForeignKey(Country, on_delete=models.CASCADE)
    planned_date = models.DateField()
    budget = models.DecimalField(max_digits=10, decimal_places=2)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)


    def __str__(self):
        return f"{self.user.username} - {self.country.name} (Planned for {self.planned_date})"
    class Meta:
        unique_together = ['user', 'country']
        ordering = ['planned_date']
        indexes = [
            models.Index(fields=['user', 'planned_date']),  # Add composite index
        ]

class TravelPhoto(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='travel_photos/')
    caption = models.CharField(max_length=200, blank=True)
    location = models.CharField(max_length=100, blank=True)
    taken_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Photo by {self.user.username} - {self.created_at.date()}"

class TravelJournal(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    country = models.ForeignKey(Country, on_delete=models.CASCADE)
    visit_date = models.DateField()
    title = models.CharField(max_length=200)
    content = models.TextField()
    photos = models.ManyToManyField(TravelPhoto, blank=True, related_name='journal_entries')
    rating = models.IntegerField(choices=[(i, i) for i in range(1, 6)])
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.title} - {self.country.name}"

class CountryInfo(models.Model):
    country = models.OneToOneField(Country, on_delete=models.CASCADE)
    capital = models.CharField(max_length=100)
    population = models.IntegerField()
    languages = models.JSONField()
    currency = models.CharField(max_length=50)
    best_time_to_visit = models.CharField(max_length=200)
    visa_requirements = models.TextField()

class Achievement(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    icon = models.ImageField(upload_to='achievements/')
    requirement_count = models.IntegerField()
    achievement_type = models.CharField(max_length=50, choices=[
        ('countries_visited', 'Countries Visited'),
        ('continents_visited', 'Continents Visited'),
        ('photos_shared', 'Photos Shared')
    ])

class TravelGroup(models.Model):
    name = models.CharField(max_length=100)
    members = models.ManyToManyField(User, related_name='travel_groups')
    description = models.TextField()
    planned_destinations = models.ManyToManyField(Country)
    created_at = models.DateTimeField(auto_now_add=True)

class TravelTip(models.Model):
    country = models.ForeignKey(Country, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    category = models.CharField(max_length=50, choices=[
        ('accommodation', 'Accommodation'),
        ('transportation', 'Transportation'),
        ('food', 'Food & Dining'),
        ('activities', 'Activities'),
        ('safety', 'Safety')
    ])
    content = models.TextField()
    upvotes = models.ManyToManyField(User, related_name='upvoted_tips')