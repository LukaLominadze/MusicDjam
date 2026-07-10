# api/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView
from .views import RegisterView, LoginView, UserProfileViewSet, ArtistViewSet, AlbumViewSet, MusicViewSet, PlaylistViewSet

router = DefaultRouter()

router.register('profile', UserProfileViewSet, basename='user-profile')
router.register('artist', ArtistViewSet, basename='artist')
router.register('album', AlbumViewSet, basename='album')
router.register('music', MusicViewSet, basename='music')
router.register('playlist', PlaylistViewSet, basename='playlist')

urlpatterns = [
    # Leave empty for now, or add a placeholder view
    path('auth/register/', RegisterView.as_view(), name='register'),
    path('auth/login/', LoginView.as_view(), name='login'),
    path('auth/token/refresh', TokenRefreshView.as_view(), name='token_refresh'), 
    path('', include(router.urls)),
]
