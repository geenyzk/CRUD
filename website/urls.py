from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('privacy', views.privacy, name='privacy'),
    path('terms', views.terms, name='terms'),
    path('login', views.login, name='login'),
    path('register', views.register, name='register'),
    path('logout', views.logout, name='logout'),
    path('dashboard', views.dashboard, name='dashboard'),
    # Staff-only management
    path('manage/users', views.admin_users, name='admin_users'),
    path('manage/users/create', views.admin_user_create, name='admin_user_create'),
    path('manage/users/<int:user_id>/toggle-staff', views.toggle_staff, name='toggle_staff'),
    path('manage/users/<int:user_id>/toggle-superuser', views.toggle_superuser, name='toggle_superuser'),
    path('manage/records', views.records_list, name='records_list'),
    path('manage/records/create', views.record_create, name='record_create'),
    path('manage/records/<int:pk>', views.record_detail, name='record_detail'),
    path('manage/records/<int:pk>/edit', views.record_update, name='record_update'),
    path('manage/records/<int:pk>/delete', views.record_delete, name='record_delete'),
]
