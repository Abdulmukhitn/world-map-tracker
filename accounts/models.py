from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

class Profile(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='profile'
    )
    avatar = models.ImageField(
        upload_to='profile_photos/',
        default='profile_photos/default-avatar.png'
    )
    bio = models.TextField(max_length=500, blank=True)
    location = models.CharField(max_length=100, blank=True)
    birth_date = models.DateField(null=True, blank=True)
    website = models.URLField(max_length=200, blank=True)
    social_links = models.JSONField(default=dict, blank=True)
    travel_preferences = models.JSONField(default=dict, blank=True)
    travel_style = models.CharField(max_length=50, blank=True)

    class Meta:
        app_label = 'accounts'

    def __str__(self):
        return f"{self.user.username}'s profile"

@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)
    else:
        # Get or create to handle any existing users without profiles
        Profile.objects.get_or_create(user=instance)
