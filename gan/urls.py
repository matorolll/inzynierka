from django.urls import path, include
from . import views
urlpatterns = [
    path("gan_control_panel/", views.gan_control_panel_view, name="gan_control_panel_view"),
    path("gan_control_panel/esrgan/", views.esrgan_site_view, name="esrgan_site_view"),
    
    path("ESRGAN_run/", views.ESRGAN_run, name="ESRGAN_run"),
    path('delete_all_gan_photos/', views.delete_all_gan_photos, name='delete_all_gan_photos'),

]