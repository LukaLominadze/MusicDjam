# api/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.explore, name='explore'),
    path('login', views.login, name='login'),
    path('register', views.register, name='register'),
    path('profile', views.profile, name='profile'),
]
