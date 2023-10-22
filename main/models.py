from django.db import models

class Session(models.Model):
    name = models.CharField(max_length=100, unique=True) 
    password = models.CharField(max_length=100, default="password")

    def __str__(self):
        return self.name

from PIL import Image
import os

class Photo(models.Model):
    title = models.CharField(max_length=255)
    image = models.ImageField(upload_to='photos/')
    session = models.ForeignKey(Session, on_delete=models.CASCADE,null=True)
    selected_to_edit = models.BooleanField(default=False)
    thumbnail = models.ImageField(upload_to='thumbnails/', blank=True, null=True)
    thumbnail_medium = models.ImageField(upload_to='thumbnails_medium/', blank=True, null=True)

    def __str__(self):
        return self.title
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        
        if not self.thumbnail:
            image = Image.open(self.image.path)
            thumbnail_size = (100, 100)
            image.thumbnail(thumbnail_size)

            thumbnail_directory = "media/thumbnails/"
            os.makedirs(thumbnail_directory, exist_ok=True)

            thumbnail_path = f"{thumbnail_directory}{self.image.name.split('/')[-1]}"
            image.save(thumbnail_path)
            self.thumbnail = f"thumbnails/{self.image.name.split('/')[-1]}"
            super().save(*args, **kwargs)

        if not self.thumbnail_medium:
            image = Image.open(self.image.path)
            image.thumbnail((image.width // 7, image.height // 7))

            medium_thumbnail_directory = "media/thumbnails_medium/"
            os.makedirs(medium_thumbnail_directory, exist_ok=True)

            thumbnail_path = f"{medium_thumbnail_directory}{self.image.name.split('/')[-1]}"
            image.save(thumbnail_path)
            self.thumbnail_medium = f"thumbnails_medium/{self.image.name.split('/')[-1]}"
            super().save(*args, **kwargs)


    def delete(self, *args, **kwargs):
        if self.image:
            if os.path.isfile(self.image.path):
                os.remove(self.image.path)
        if self.thumbnail:
            if os.path.isfile(self.thumbnail.path):
                os.remove(self.thumbnail.path)

        if self.thumbnail_medium:
            if os.path.isfile(self.thumbnail_medium.path):
                os.remove(self.thumbnail_medium.path)

        super().delete(*args, **kwargs)

