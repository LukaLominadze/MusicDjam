from django.shortcuts import redirect, render
from django.http import HttpResponse
from django.conf import settings
import os

def explore(request):
    if not request.user.is_authenticated:
        return redirect('login')
    return render(request, 'index.html', {
        'user_id': request.user.id,
        'is_staff': request.user.is_staff,
    })

def login(request):
    return render(request, 'login.html')

def register(request):
    return render(request, 'register.html')

def profile(request, user_id=None):
    if not request.user.is_authenticated:
        return redirect('login')
    return render(request, 'profile.html', {
        'user_id': user_id or request.user.id,
        'is_staff': request.user.is_staff,
    })

def serve_template(filename):
    def view(request):
        template_path = os.path.join(settings.BASE_DIR, 'templates', filename)
        with open(template_path, 'r') as f:
            content = f.read()
        return HttpResponse(content, content_type='text/html')
    return view

def _entity_context(request):
    return {
        'user_id': request.user.id,
        'is_staff': request.user.is_staff,
    }

def artist_detail(request, artist_id):
    if not request.user.is_authenticated:
        return redirect('login')
    ctx = _entity_context(request)
    ctx['artist_id'] = artist_id
    return render(request, 'artist_detail.html', ctx)

def album_detail(request, album_id):
    if not request.user.is_authenticated:
        return redirect('login')
    ctx = _entity_context(request)
    ctx['album_id'] = album_id
    return render(request, 'album_detail.html', ctx)

def playlist_detail(request, playlist_id):
    if not request.user.is_authenticated:
        return redirect('login')
    ctx = _entity_context(request)
    ctx['playlist_id'] = playlist_id
    return render(request, 'playlist_detail.html', ctx)

def artist_add(request):
    if not request.user.is_authenticated:
        return redirect('login')
    return render(request, 'artist_form.html', _entity_context(request))

def artist_edit(request, artist_id):
    if not request.user.is_authenticated:
        return redirect('login')
    ctx = _entity_context(request)
    ctx['artist_id'] = artist_id
    return render(request, 'artist_form.html', ctx)

def album_add(request):
    if not request.user.is_authenticated:
        return redirect('login')
    return render(request, 'album_form.html', _entity_context(request))

def album_edit(request, album_id):
    if not request.user.is_authenticated:
        return redirect('login')
    ctx = _entity_context(request)
    ctx['album_id'] = album_id
    return render(request, 'album_form.html', ctx)

def music_add(request):
    if not request.user.is_authenticated:
        return redirect('login')
    return render(request, 'music_form.html', _entity_context(request))

def music_edit(request, music_id):
    if not request.user.is_authenticated:
        return redirect('login')
    ctx = _entity_context(request)
    ctx['music_id'] = music_id
    return render(request, 'music_form.html', ctx)

def playlist_add(request):
    if not request.user.is_authenticated:
        return redirect('login')
    return render(request, 'playlist_form.html', _entity_context(request))

def playlist_edit(request, playlist_id):
    if not request.user.is_authenticated:
        return redirect('login')
    ctx = _entity_context(request)
    ctx['playlist_id'] = playlist_id
    return render(request, 'playlist_form.html', ctx)
