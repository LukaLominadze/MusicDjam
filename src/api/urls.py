# api/urls.py
from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import RegisterView

urlpatterns = [
    # Leave empty for now, or add a placeholder view
    path('auth/register/', RegisterView.as_view(), name='register'),
    path('auth/login/', TokenObtainPairView.as_view(), name='login'),
    path('auth/token/refresh', TokenRefreshView.as_view(), name='token_refresh'),
]
