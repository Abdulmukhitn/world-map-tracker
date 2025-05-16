from django.core.management.base import BaseCommand
from django.conf import settings
from PIL import Image, ImageDraw, ImageFont
import os

class Command(BaseCommand):
    help = 'Generates a default avatar image'

    def handle(self, *args, **kwargs):
        # Create a new image with a blue background
        size = (200, 200)
        img = Image.new('RGB', size, color='#3d8bfd')
        draw = ImageDraw.Draw(img)
        
        # Draw a circle
        draw.ellipse([40, 40, 160, 160], fill='#ffffff')
        
        # Draw a simplified person icon
        draw.ellipse([80, 60, 120, 100], fill='#3d8bfd')  # Head
        draw.rectangle([70, 105, 130, 150], fill='#3d8bfd')  # Body
        
        # Save the image
        avatar_path = os.path.join(settings.MEDIA_ROOT, 'profile_photos', 'default-avatar.png')
        os.makedirs(os.path.dirname(avatar_path), exist_ok=True)
        img.save(avatar_path, 'PNG')
        
        self.stdout.write(self.style.SUCCESS(f'Successfully created default avatar at {avatar_path}'))