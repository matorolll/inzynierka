from django.db import models
import os

class ganPhoto(models.Model):
    title = models.CharField(max_length=255)
    image = models.ImageField(upload_to='gan_photos/')

    def __str__(self):
        return self.title
    
    def save(self, *args, **kwargs):
        if not self.id:
            existing_ids = ganPhoto.objects.values_list('id', flat=True)
            if existing_ids:
                self.id = max(existing_ids) + 1
            else:
                self.id = 1
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        if self.image:
            if os.path.isfile(self.image.path):
                os.remove(self.image.path)

        super().delete(*args, **kwargs)


class texttoimagePhoto(models.Model):
    title = models.CharField(max_length=255)
    prompt = models.CharField(max_length=255)
    image = models.ImageField(upload_to='gan_photos/openai/')

    def __str__(self):
        return self.title
    
    def save(self, *args, **kwargs):
        if not self.id:
            existing_ids = texttoimagePhoto.objects.values_list('id', flat=True)
            if existing_ids:
                self.id = max(existing_ids) + 1
            else:
                self.id = 1
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        if self.image:
            if os.path.isfile(self.image.path):
                os.remove(self.image.path)

        super().delete(*args, **kwargs)