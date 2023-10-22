from django.urls import path, include
from . import views
urlpatterns = [
    path("", views.index, name="index"),
    path("home/", views.home, name="home"),
    path("portfolio/", views.portfolio, name="portfolio"),

    path("session/wedding", views.weddingSession, name="weddingSession"),
    path("session/newborn", views.newbornSession, name="newbornSession"),
    path("session/family", views.familySession, name="familySession"),


    #path("sessions/", views.sessions, name="sessions"),


    path("pricing/", views.pricing, name="pricing"),
    path("profile/", views.profile, name="profile"),


    path("sign_up/", views.sign_up, name="sign_up"),
    path("logout/", views.log_out, name="logout"),


    path("control_panel/", views.control_panel, name="control_panel"),
    path("control_panel/create_session/", views.create_session, name="create_session"),
    path("control_panel/view_sessions/", views.view_sessions, name="view_sessions"),
    path("control_panel/delete_sessions/", views.delete_sessions, name="delete_sessions"),
    path("control_panel/delete_session/<str:name>", views.delete_session, name="delete_session"),

    path("control_panel/photos_sessions/", views.photos_sessions, name="photos_sessions"),




    path('session/<str:name>/', views.view_session, name='view_session'),
    path('update_photo_select/<int:photo_id>/', views.update_photo_select, name='update_photo_select'),
    path('update_photo_select_multiple/', views.update_photo_select_multiple, name='update_photo_select_multiple'),

    path('download_to_zip/<str:name>/', views.download_photos_zip, name='download_photos_zip'),
    path('download_to_file/<str:name>/', views.download_photos_folder, name='download_photos_folder'),



    path('', include("django.contrib.auth.urls")),
]