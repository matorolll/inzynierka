from django.urls import path, include
from . import views
urlpatterns = [
    path("gan_control_panel/", views.gan_control_panel, name="gan_control_panel"),
    path("ESRGAN_run/", views.ESRGAN_run, name="ESRGAN_run")
]