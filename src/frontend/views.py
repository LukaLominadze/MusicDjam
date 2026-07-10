from django.shortcuts import redirect, render

# Create your views here.

def explore(request):
    if not request.user.is_authenticated:
        return redirect('login')
    return render(request, 'index.html')

def login(request):
    return render(request, 'login.html')

def register(request):
    return render(request, 'register.html')
