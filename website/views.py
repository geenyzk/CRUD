from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import user_passes_test
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.models import User
from django.urls import reverse
from django.db.models import Q
from django.utils import timezone
from datetime import timedelta
from .forms import CreateUserForm, LoginForm, AdminCreateUserForm, RecordForm
from .models import Record


def home(request):
    # lightweight stats + recent content for homepage
    total_users = User.objects.count()
    total_records = Record.objects.count()
    recent_records = list(Record.objects.select_related('created_by')[:6])
    latest_record = recent_records[0] if recent_records else None
    context = {
        'total_users': total_users,
        'total_records': total_records,
        'recent_records': recent_records,
        'latest_record': latest_record,
    }
    return render(request, 'pages/index.html', context)


def privacy(request):
    return render(request, 'pages/privacy.html')


def terms(request):
    return render(request, 'pages/terms.html')
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
        {
            "label": "New Users (7d)",
            "value": new_users_week,
            "icon": "user-plus",
            "accent": "from-emerald-500/80 to-emerald-400/60",
        },
        {
            "label": "Active (24h)",
            "value": active_24h,
            "icon": "bolt",
            "accent": "from-amber-500/80 to-orange-400/60",
        },
        {
            "label": "Days Since You Joined",
            "value": days_since_join,
            "icon": "calendar",
            "accent": "from-sky-500/80 to-indigo-500/70",
        },
        {
            "label": "Total Users",
            "value": total_users,
            "icon": "users",
            "accent": "from-violet-500/80 to-purple-500/70",
        },
    ]

    recent = []
    if request.user.last_login:
        recent.append({"title": "Logged in", "when": request.user.last_login, "status": "Success"})
    recent.append({"title": "Joined CRUD", "when": request.user.date_joined, "status": "Member"})

    quick_actions = []
    latest_records = []
    if request.user.is_staff:
        quick_actions = [
            {
                "label": "Add Record",
                "url": reverse('record_create'),
                "classes": "inline-flex items-center justify-center gap-2 rounded-xl bg-gradient-to-r from-sky-500 to-indigo-500 px-4 py-2 text-sm font-semibold text-white shadow-[0_18px_36px_-24px_rgba(59,130,246,0.7)] transition hover:from-sky-400 hover:to-indigo-400",
            },
            {
                "label": "Manage Records",
                "url": reverse('records_list'),
                "classes": "inline-flex items-center justify-center gap-2 rounded-xl border border-white/20 px-4 py-2 text-sm font-semibold text-white/85 transition hover:border-white/35 hover:bg-white/10",
            },
            {
                "label": "Manage Users",
                "url": reverse('admin_users'),
                "classes": "inline-flex items-center justify-center gap-2 rounded-xl border border-white/20 px-4 py-2 text-sm font-semibold text-white/85 transition hover:border-white/35 hover:bg-white/10",
            },
        ]
        latest_records = list(Record.objects.select_related('created_by')[:5])

    context = {
        "stats": stats,
        "recent": recent,
        "quick_actions": quick_actions,
        "latest_records": latest_records,
    }
    return render(request, 'pages/dashboard.html', context)


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
    query = request.GET.get('q', '').strip()
    records_qs = Record.objects.select_related('created_by')
    if query:
        records_qs = records_qs.filter(
            Q(title__icontains=query)
            | Q(description__icontains=query)
            | Q(created_by__username__icontains=query)
        )

    records = list(records_qs)
    total_records = Record.objects.count()

    context = {
        "records": records,
        "query": query,
        "matches": len(records),
        "total_records": total_records,
    }
    return render(request, 'pages/records_list.html', context)


@staff_member_required(login_url='login')
def record_create(request):
    form = RecordForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        rec = form.save(commit=False)
        rec.created_by = request.user
        rec.save()
        messages.success(request, 'Record created.')
        return redirect('records_list')
    return render(request, 'pages/record_form.html', {"form": form, "is_edit": False, "record": None})


@staff_member_required(login_url='login')
def record_detail(request, pk: int):
    record = get_object_or_404(Record.objects.select_related('created_by'), pk=pk)
    return render(request, 'pages/record_detail.html', {"record": record})


@staff_member_required(login_url='login')
def record_update(request, pk: int):
    record = get_object_or_404(Record, pk=pk)
    form = RecordForm(request.POST or None, instance=record)
    if request.method == 'POST':
        if form.is_valid():
            form.save()
            messages.success(request, 'Record updated.')
            return redirect('record_detail', pk=record.pk)
        messages.error(request, 'Please fix the errors below to update this record.')
    return render(request, 'pages/record_form.html', {"form": form, "record": record, "is_edit": True})


@staff_member_required(login_url='login')
def record_delete(request, pk: int):
    record = get_object_or_404(Record, pk=pk)
    if request.method == 'POST':
        title = record.title
        record.delete()
        messages.success(request, f"Deleted record '{title}'.")
        return redirect('records_list')
    cancel_url = request.GET.get('next') or reverse('record_detail', kwargs={'pk': record.pk})
    return render(request, 'pages/record_confirm_delete.html', {"record": record, "cancel_url": cancel_url})


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
