from django.urls import path, include
from . import views
urlpatterns = [
    path("gan_control_panel/", views.gan_control_panel_view, name="gan_control_panel_view"),

    path("gan_control_panel/esrgan/", views.esrgan_view, name="esrgan_view"),
    path("ESRGAN_run/", views.esrgan_run, name="esrgan_run"),
    path('esrgan_delete_all_photos/', views.esrgan_delete_all_photos, name='esrgan_delete_all_photos'),

    path("gan_control_panel/text_to_image/", views.tti_view, name="tti_view"),
    path("tti_run/", views.tti_run, name="tti_run"),
    path('tti_delete_all_photos/', views.tti_delete_all_photos, name='tti_delete_all_photos'),

    path("gan_control_panel/image_to_image/", views.iti_view, name="iti_view"),
    path("iti_run/", views.iti_run, name="iti_run"),
    path('iti_delete_all_photos/', views.iti_delete_all_photos, name='iti_delete_all_photos'),

]