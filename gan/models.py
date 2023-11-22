from django.db import models
import os

class ganPhoto(models.Model):
    title = models.CharField(max_length=255)
    image = models.ImageField(upload_to='gan_photos/')

    def __str__(self):
        return self.title
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        if self.image:
            if os.path.isfile(self.image.path):
                os.remove(self.image.path)

        super().delete(*args, **kwargs)
