from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.utils.html import format_html
from PIL import Image



# Create your models here.
class Video(models.Model):
    """Recorded Video"""

    # Ref: https://docs.djangoproject.com/en/3.1/ref/models/fields/#filefield
    file = models.FileField(upload_to="videos/", blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)


class OutputVideo(models.Model):
    # ... Other fields ...
    video_file = models.FileField(upload_to='tracked_videos')

class CountLog(models.Model):
    timestamp = models.DateTimeField(auto_now_add=True)
    filename = models.CharField(max_length=255, null=True)
    total_count = models.PositiveIntegerField(null=True)
    up_count = models.PositiveIntegerField(null=True)
    down_count = models.PositiveIntegerField(null=True)
    class_counts = models.JSONField(default=dict)
    class_counter = models.JSONField(default=dict)
    
    def __str__(self):
        return f"CountLog - {self.timestamp}"

class VehicleLog(models.Model):
    timestamp = models.DateTimeField(auto_now_add=True)
    filename = models.CharField(max_length=255, null=True)
    total_count = models.PositiveIntegerField(null=True)
    up_count = models.PositiveIntegerField(null=True)
    down_count = models.PositiveIntegerField(null=True)
    class_counts = models.JSONField(default=dict)
    class_counter = models.JSONField(default=dict)
    
    @property
    def log_date(self):
        return self.timestamp.date()
    
    def __str__(self):
        return f"VehicleLog - {self.timestamp}"
   
class PlateLog(models.Model):
    timestamp = models.DateTimeField(default=timezone.now)
    filename = models.CharField(max_length=255, null=True)
    plate_number = models.CharField(max_length=255, null=True)
    plate_image = models.ImageField(upload_to='plate_images/', null=True)
    frame_image = models.ImageField(upload_to='frame_images/', null=True)

    def __str__(self):
        return f"PlateLog for {self.timestamp}"
    
    def display_plate_image(self):

        if self.plate_image:
            # Open the image using Pillow
            image = Image.open(self.plate_image.path)
            
            # Resize the image while maintaining the aspect ratio
            max_width = 200  # Set the maximum width for display
            width_percent = (max_width / float(image.size[0]))
            new_height = int(float(image.size[1]) * float(width_percent))
            #resized_image = image.resize((max_width, new_height), Image.ANTIALIAS)
            
            # Use format_html to ensure HTML is not escaped
            return format_html('<img src="{}" width="{}" height="{}" />', self.plate_image.url, max_width, new_height)
        else:
            return format_html('<img src="{}" width="{}" height="{}" />', '/static/placeholder.png', 200, 200)
    
    def display_frame_image(self):

        if self.frame_image:
            # Open the image using Pillow
            image = Image.open(self.plate_image.path)
            
            # Resize the image while maintaining the aspect ratio
            max_width = 200  # Set the maximum width for display
            width_percent = (max_width / float(image.size[0]))
            new_height = int(float(image.size[1]) * float(width_percent))
            #resized_image = image.resize((max_width, new_height), Image.ANTIALIAS)

            # Use format_html to ensure HTML is not escaped
            return format_html('<img src="{}" width="{}" height="{}" />', self.frame_image.url, max_width, new_height)
        else:
            return format_html('<img src="{}" width="{}" height="{}" />', '/static/placeholder.png', 200, 200)

    display_plate_image.short_description = "Plate Image"
    display_frame_image.short_description = "Frame Image"
