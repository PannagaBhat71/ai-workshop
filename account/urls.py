from django.urls import path
from django.shortcuts import redirect
from . import views

app_name = 'account'

urlpatterns = [
    path('', views.home_view, name='home'),
    path('register/', views.register_select_view, name='register_select'),
    path('register/zenken-student/', views.zenken_register_view, name='register_zenken'),
    path('register/non-zenken-student/', views.non_zenken_register_view, name='register_non_zenken'),
    # Teacher registration redirect directly to login
    path('register/teacher/', lambda request: redirect('account:login'), name='register_teacher'),
    path('login/', views.user_login_view, name='login'),
    path('login/google-sahyadri/', views.google_sahyadri_oauth_view, name='google_oauth'),
    path('logout/', views.user_logout_view, name='logout'),
    path('dashboard/', views.dashboard_dispatcher_view, name='dashboard'),
]
