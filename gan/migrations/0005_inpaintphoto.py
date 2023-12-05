# Generated by Django 4.2.4 on 2023-12-05 12:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gan', '0004_imagetoimagephoto'),
    ]

    operations = [
        migrations.CreateModel(
            name='inpaintPhoto',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255)),
                ('prompt', models.CharField(max_length=255)),
                ('image', models.ImageField(upload_to='gan_photos/inpaint/')),
            ],
        ),
    ]
