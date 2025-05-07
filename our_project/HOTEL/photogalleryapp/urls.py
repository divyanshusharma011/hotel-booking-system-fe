from django.urls import path
from . import views

urlpatterns = [
    path('', views.photo_gallery, name='photo_gallery'),


    path('video-quotes/', views.video_quotes_page, name='video_quotes'),


]
