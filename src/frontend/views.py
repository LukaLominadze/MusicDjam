from django.shortcuts import redirect, render
from django.http import HttpResponse
from django.conf import settings
import os

def explore(request):
    if not request.user.is_authenticated:
        return redirect('login')
    return render(request, 'index.html')

def login(request):
    return render(request, 'login.html')

def register(request):
    return render(request, 'register.html')

def profile(request):
    if not request.user.is_authenticated:
        return redirect('login')
    return render(request, 'profile.html')

def serve_template(filename):
    def view(request):
        template_path = os.path.join(settings.BASE_DIR, 'templates', filename)
        with open(template_path, 'r') as f:
            content = f.read()
        return HttpResponse(content, content_type='text/html')
    return view

def artist_detail(request, artist_id):
    if not request.user.is_authenticated:
        return redirect('login')
    return render(request, 'artist_detail.html', {'artist_id': artist_id})

def album_detail(request, album_id):
    if not request.user.is_authenticated:
        return redirect('login')
    return render(request, 'album_detail.html', {'album_id': album_id})

def playlist_detail(request, playlist_id):
    if not request.user.is_authenticated:
        return redirect('login')
    return render(request, 'playlist_detail.html', {'playlist_id': playlist_id})
