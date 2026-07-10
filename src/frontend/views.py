from django.shortcuts import redirect, render

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
