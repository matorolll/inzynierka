from django.urls import path, include
from . import views
urlpatterns = [
    path("gan_control_panel/", views.gan_control_panel, name="gan_control_panel"),
    path("ESRGAN_run/", views.ESRGAN_run, name="ESRGAN_run"),
    path('delete_all_gan_photos/', views.delete_all_gan_photos, name='delete_all_gan_photos'),

]