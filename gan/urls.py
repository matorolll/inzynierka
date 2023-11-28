from django.urls import path, include
from . import views
urlpatterns = [
    path("gan_control_panel/", views.gan_control_panel_view, name="gan_control_panel_view"),

    path("gan_control_panel/esrgan/", views.esrgan_site_view, name="esrgan_site_view"),
    path("ESRGAN_run/", views.ESRGAN_run, name="ESRGAN_run"),
    path('delete_all_esrgan_photos/', views.delete_all_esrgan_photos, name='delete_all_esrgan_photos'),

    path("gan_control_panel/text_to_image/", views.text_to_image_site_view, name="text_to_image_site_view"),
    path("TEXTTOIMAGE_run/", views.TEXTTOIMAGE_run, name="TEXTTOIMAGE_run"),
    path('delete_all_tti_photos/', views.delete_all_tti_photos, name='delete_all_tti_photos'),


]