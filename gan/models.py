from django.db import models

class ganPhoto(models.Model):
    title = models.CharField(max_length=255)
    image = models.ImageField(upload_to='gan_photos/')

    def __str__(self):
        return self.title
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)