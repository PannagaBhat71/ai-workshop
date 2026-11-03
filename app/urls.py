from django.urls import path
from . import views

app_name = 'app'

urlpatterns = [
    # Dashboards
    path('dashboard/teacher/', views.teacher_dashboard, name='teacher_dashboard'),
    path('dashboard/zenken-student/', views.zenken_dashboard, name='zenken_dashboard'),
    path('dashboard/student/', views.non_zenken_dashboard, name='non_zenken_dashboard'),

    # Questions
    path('questions/', views.question_list_view, name='question_list'),
    path('questions/create/', views.question_create_view, name='question_create'),
    path('questions/<int:pk>/', views.question_detail_view, name='question_detail'),
    path('questions/<int:pk>/edit/', views.question_edit_view, name='question_edit'),
    path('questions/<int:pk>/delete/', views.question_delete_view, name='question_delete'),

    # Academy Updates
    path('updates/', views.update_list_view, name='update_list'),
    path('updates/create/', views.update_create_view, name='update_create'),
    path('updates/<int:pk>/edit/', views.update_edit_view, name='update_edit'),
    path('updates/<int:pk>/delete/', views.update_delete_view, name='update_delete'),
]

