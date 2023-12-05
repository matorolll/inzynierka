from django.db import models
import os

class esrganPhoto(models.Model):
    title = models.CharField(max_length=255)
    image = models.ImageField(upload_to='gan_photos/esrgan/')

    def __str__(self):
        return self.title
    
    def save(self, *args, **kwargs):
        if not self.id:
            existing_ids = esrganPhoto.objects.values_list('id', flat=True)
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
    image = models.ImageField(upload_to='gan_photos/texttoimage/')

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


class imagetoimagePhoto(models.Model):
    title = models.CharField(max_length=255)
    prompt = models.CharField(max_length=255)
    image = models.ImageField(upload_to='gan_photos/imagetoimage/')

    def __str__(self):
        return self.title
    
    def save(self, *args, **kwargs):
        if not self.id:
            existing_ids = imagetoimagePhoto.objects.values_list('id', flat=True)
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


class inpaintPhoto(models.Model):
    title = models.CharField(max_length=255)
    prompt = models.CharField(max_length=255)
    image = models.ImageField(upload_to='gan_photos/inpaint/')

    def __str__(self):
        return self.title
    
    def save(self, *args, **kwargs):
        if not self.id:
            existing_ids = inpaintPhoto.objects.values_list('id', flat=True)
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