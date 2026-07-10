# api/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.explore, name='explore'),
    path('login', views.login, name='login'),
    path('register', views.register, name='register'),
    path('profile', views.profile, name='profile'),
    path('music_card.html', views.serve_template('music_card.html'), name='music_card_template'),
    path('artist_card.html', views.serve_template('artist_card.html'), name='artist_card_template'),
    path('album_card.html', views.serve_template('album_card.html'), name='album_card_template'),
    path('playlist_card.html', views.serve_template('playlist_card.html'), name='playlist_card_template'),
    path('artist/<int:artist_id>/', views.artist_detail, name='artist_detail'),
    path('album/<int:album_id>/', views.album_detail, name='album_detail'),
    path('playlist/<int:playlist_id>/', views.playlist_detail, name='playlist_detail'),
]
