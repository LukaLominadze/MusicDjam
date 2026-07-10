# api/urls.py
from django.urls import path
from . import views

urlpatterns = [
    # Leave empty for now, or add a placeholder view
    path('', views.explore, name='explore'),
    path('login', views.login, name='login'),
    path('register', views.register, name='register')
]
