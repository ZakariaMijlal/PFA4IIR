from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView

# Home page view
def home(request):
    return render(request, '/home.html')  # Home page template
