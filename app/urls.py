from django.urls import path
from . import views

app_name = 'app'

urlpatterns = [
    # Dashboards
    path('dashboard/teacher/', views.teacher_dashboard, name='teacher_dashboard'),
    path('dashboard/zenken-student/', views.zenken_dashboard, name='zenken_dashboard'),
    path('dashboard/student/', views.non_zenken_dashboard, name='non_zenken_dashboard'),

    # Teacher Student Activity Review
    path('teacher/student-activities/', views.student_activities_view, name='student_activities'),
    path('teacher/student-activities/<int:pk>/', views.student_attempt_detail_view, name='student_attempt_detail'),

    # Leaderboard & Streak Board
    path('leaderboard/', views.leaderboard_view, name='leaderboard'),

    # Topic-Wise Practice Room
    path('practice/topics/', views.topic_practice_rooms_view, name='topic_practice_rooms'),
    path('practice/topics/<str:topic_code>/', views.topic_room_practice_view, name='topic_room_practice'),

    # Practice Arena (General & Specific Sets)
    path('practice-arena/', views.practice_arena_view, name='practice_arena'),

    # Strictly 20-Question Quizzes (Scheduling, Posting, Taking with Anti-Cheat)
    path('quizzes/', views.quiz_list_view, name='quiz_list'),
    path('quizzes/create/', views.quiz_create_view, name='quiz_create'),
    path('quizzes/<int:pk>/', views.quiz_detail_view, name='quiz_detail'),
    path('quizzes/<int:pk>/edit/', views.quiz_edit_view, name='quiz_edit'),
    path('quizzes/<int:pk>/delete/', views.quiz_delete_view, name='quiz_delete'),
    path('quizzes/<int:pk>/take/', views.quiz_take_view, name='quiz_take'),
    path('quizzes/result/<int:pk>/', views.quiz_attempt_result_view, name='quiz_attempt_result'),

    # Weekly Placement Newsletter
    path('newsletter/', views.newsletter_list_view, name='newsletter_list'),
    path('newsletter/<int:pk>/', views.newsletter_detail_view, name='newsletter_detail'),
    path('newsletter/create/', views.newsletter_create_view, name='newsletter_create'),

    # Placement Opportunities
    path('opportunities/', views.opportunity_list_view, name='opportunity_list'),
    path('opportunities/create/', views.opportunity_create_view, name='opportunity_create'),

    # Study Materials & Document Upload
    path('materials/', views.material_list_view, name='material_list'),
    path('materials/upload/', views.material_upload_view, name='material_upload'),

    # Questions CRUD
    path('questions/', views.question_list_view, name='question_list'),
    path('questions/create/', views.question_create_view, name='question_create'),
    path('questions/<int:pk>/', views.question_detail_view, name='question_detail'),
    path('questions/<int:pk>/edit/', views.question_edit_view, name='question_edit'),
    path('questions/<int:pk>/delete/', views.question_delete_view, name='question_delete'),

    # Voice Dictation & Smart Options Generator API
    path('api/auto-generate-options/', views.auto_generate_options_api, name='api_auto_generate_options'),

    # Interactive AI Tutor Chatbot (Groq API)
    path('api/chat/', views.chat_bot_api, name='api_chat_bot'),
    path('assistant/', views.assistant_page_view, name='assistant_page'),

    # Academy Updates
    path('updates/', views.update_list_view, name='update_list'),
    path('updates/create/', views.update_create_view, name='update_create'),
    path('updates/<int:pk>/edit/', views.update_edit_view, name='update_edit'),
    path('updates/<int:pk>/delete/', views.update_delete_view, name='update_delete'),
]
