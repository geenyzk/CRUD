from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib import messages
from .forms import CreateUserForm, LoginForm


def home(request):
    return render(request, 'pages/index.html')  # or the template you want
def register(request):
    form = CreateUserForm()
    if request.method == 'POST':
        form = CreateUserForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Account created successfully! You can now log in.')
            return redirect('login')
    context = {'form': form}
    return render(request, 'pages/register.html', context)

def login(request):
    form = LoginForm(request, data=request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            user = form.get_user()
            auth_login(request, user)
            messages.success(request, f"Welcome back, {user.username}!")
            return redirect('home')  # Change to your landing/dashboard/home route
        else:
            messages.error(request, 'Invalid username or password.')

    return render(request, 'pages/login.html', {'form': form})

def logout(request):
    auth_logout(request)
    messages.info(request, 'You have been logged out.')
    return redirect('login')

@login_required(login_url="login")
def dashboard(request):
    return render(request, 'pages/dashboadrd.html')