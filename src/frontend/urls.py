from django.urls import path
from . import views

urlpatterns = [
    path('', views.explore, name='explore'),
    path('login', views.login, name='login'),
    path('register', views.register, name='register'),
    path('profile', views.profile, name='profile'),
    path('profile/<uuid:user_id>/', views.profile, name='profile_user'),
    path('music_card.html', views.serve_template('music_card.html'), name='music_card_template'),
    path('artist_card.html', views.serve_template('artist_card.html'), name='artist_card_template'),
    path('album_card.html', views.serve_template('album_card.html'), name='album_card_template'),
    path('playlist_card.html', views.serve_template('playlist_card.html'), name='playlist_card_template'),
    path('user_card.html', views.serve_template('user_card.html'), name='user_card_template'),
    path('artist/<int:artist_id>/', views.artist_detail, name='artist_detail'),
    path('album/<int:album_id>/', views.album_detail, name='album_detail'),
    path('playlist/<int:playlist_id>/', views.playlist_detail, name='playlist_detail'),
    path('artist/add/', views.artist_add, name='artist_add'),
    path('artist/<int:artist_id>/edit/', views.artist_edit, name='artist_edit'),
    path('album/add/', views.album_add, name='album_add'),
    path('album/<int:album_id>/edit/', views.album_edit, name='album_edit'),
    path('music/add/', views.music_add, name='music_add'),
    path('music/<int:music_id>/edit/', views.music_edit, name='music_edit'),
    path('playlist/add/', views.playlist_add, name='playlist_add'),
    path('playlist/<int:playlist_id>/edit/', views.playlist_edit, name='playlist_edit'),
]
