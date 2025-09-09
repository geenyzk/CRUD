from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import user_passes_test
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
from .forms import CreateUserForm, LoginForm, AdminCreateUserForm, RecordForm
from .models import Record


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
    now = timezone.now()
    week_ago = now - timedelta(days=7)
    day_ago = now - timedelta(days=1)

    total_users = User.objects.count()
    new_users_week = User.objects.filter(date_joined__gte=week_ago).count()
    active_24h = User.objects.filter(last_login__gte=day_ago).count()
    days_since_join = (now.date() - request.user.date_joined.date()).days

    stats = [
        {"label": "New Users (7d)", "value": new_users_week, "icon": "fa-user-plus", "variant": "success"},
        {"label": "Active (24h)", "value": active_24h, "icon": "fa-bolt", "variant": "warning"},
        {"label": "Days Since You Joined", "value": days_since_join, "icon": "fa-calendar-day", "variant": "info"},
        {"label": "Total Users", "value": total_users, "icon": "fa-users", "variant": "primary"},
    ]

    recent = []
    if request.user.last_login:
        recent.append({"title": "Logged in", "when": request.user.last_login, "status": "Success"})
    recent.append({"title": "Joined CRUD", "when": request.user.date_joined, "status": "Member"})

    return render(request, 'pages/dashboard.html', {"stats": stats, "recent": recent})


# ----- Staff-only management views -----

@staff_member_required(login_url='login')
def admin_users(request):
    users = User.objects.order_by('-date_joined')[:50]
    return render(request, 'pages/admin_users.html', {"users": users})


@staff_member_required(login_url='login')
def admin_user_create(request):
    form = AdminCreateUserForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = form.save(commit=False)
        if not request.user.is_superuser:
            user.is_superuser = False
        user.save()
        messages.success(request, f"User '{user.username}' created.")
        return redirect('admin_users')
    return render(request, 'pages/admin_user_create.html', {"form": form})


@staff_member_required(login_url='login')
def records_list(request):
    records = Record.objects.select_related('created_by').all()
    return render(request, 'pages/records_list.html', {"records": records})


@staff_member_required(login_url='login')
def record_create(request):
    form = RecordForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        rec = form.save(commit=False)
        rec.created_by = request.user
        rec.save()
        messages.success(request, 'Record created.')
        return redirect('records_list')
    return render(request, 'pages/record_create.html', {"form": form})


# ----- Role toggle actions -----

@user_passes_test(lambda u: u.is_superuser, login_url='login')
def toggle_staff(request, user_id: int):
    if request.method != 'POST':
        return redirect('admin_users')
    try:
        target = User.objects.get(pk=user_id)
    except User.DoesNotExist:
        messages.error(request, 'User not found.')
        return redirect('admin_users')

    if target == request.user:
        messages.error(request, "You can't change your own staff status here.")
        return redirect('admin_users')

    target.is_staff = not target.is_staff
    target.save()
    messages.success(request, f"{'Granted' if target.is_staff else 'Removed'} admin (staff) for {target.username}.")
    return redirect('admin_users')


@user_passes_test(lambda u: u.is_superuser, login_url='login')
def toggle_superuser(request, user_id: int):
    if request.method != 'POST':
        return redirect('admin_users')
    try:
        target = User.objects.get(pk=user_id)
    except User.DoesNotExist:
        messages.error(request, 'User not found.')
        return redirect('admin_users')

    if target == request.user and target.is_superuser:
        # Prevent removing superuser from self via UI to avoid lockout
        messages.error(request, "You can't remove your own superuser status here.")
        return redirect('admin_users')

    if target.is_superuser:
        # Prevent removing the last superuser in the system
        total_supers = User.objects.filter(is_superuser=True).count()
        if total_supers <= 1:
            messages.error(request, 'Cannot remove the last superuser.')
            return redirect('admin_users')
        target.is_superuser = False
        # Also drop staff if not desired, but keep current staff state
    else:
        target.is_superuser = True
        target.is_staff = True  # superusers should be staff as well
    target.save()
    messages.success(request, f"{('Granted' if target.is_superuser else 'Removed')} superuser for {target.username}.")
    return redirect('admin_users')
