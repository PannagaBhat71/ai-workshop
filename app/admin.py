from django.contrib import admin
from .models import (
    AptitudeQuestion,
    AcademyUpdate,
    Quiz,
    QuizAttempt,
    QuestionPracticeLog,
    UserActivityStreak,
    WeeklyNewsletter,
    Opportunity,
    StudyMaterial,
)


@admin.register(AptitudeQuestion)
class AptitudeQuestionAdmin(admin.ModelAdmin):
    list_display = ('title', 'subject', 'topic', 'difficulty', 'access_tier', 'correct_option', 'teacher', 'created_at')
    list_filter = ('subject', 'topic', 'difficulty', 'access_tier', 'created_at')
    search_fields = ('title', 'question_text', 'explanation', 'teacher__username')
    ordering = ('-created_at',)


@admin.register(Quiz)
class QuizAdmin(admin.ModelAdmin):
    list_display = ('title', 'quiz_type', 'target_audience', 'duration_minutes', 'pass_percentage', 'is_published', 'teacher', 'created_at')
    list_filter = ('quiz_type', 'target_audience', 'is_published', 'created_at')
    search_fields = ('title', 'description', 'teacher__username')
    filter_horizontal = ('questions',)


@admin.register(QuizAttempt)
class QuizAttemptAdmin(admin.ModelAdmin):
    list_display = ('student', 'quiz', 'score', 'total_questions', 'percentage', 'passed', 'tab_switch_violations', 'completed_at')
    list_filter = ('passed', 'quiz', 'completed_at')
    search_fields = ('student__username', 'quiz__title')


@admin.register(UserActivityStreak)
class UserActivityStreakAdmin(admin.ModelAdmin):
    list_display = ('student', 'current_streak', 'longest_streak', 'total_points', 'quizzes_completed', 'practice_completed', 'last_active_date')
    search_fields = ('student__username',)
    ordering = ('-total_points', '-current_streak')


@admin.register(WeeklyNewsletter)
class WeeklyNewsletterAdmin(admin.ModelAdmin):
    list_display = ('issue_number', 'title', 'author', 'published_date')
    search_fields = ('title', 'content', 'placement_strategies')
    ordering = ('-issue_number',)


@admin.register(Opportunity)
class OpportunityAdmin(admin.ModelAdmin):
    list_display = ('company_name', 'role_title', 'opportunity_type', 'location', 'deadline', 'posted_by', 'created_at')
    list_filter = ('opportunity_type', 'deadline')
    search_fields = ('company_name', 'role_title', 'eligibility')


@admin.register(StudyMaterial)
class StudyMaterialAdmin(admin.ModelAdmin):
    list_display = ('title', 'subject', 'target_audience', 'uploaded_by', 'created_at')
    list_filter = ('subject', 'target_audience')
    search_fields = ('title', 'description')


@admin.register(QuestionPracticeLog)
class QuestionPracticeLogAdmin(admin.ModelAdmin):
    list_display = ('student', 'question', 'chosen_option', 'is_correct', 'timestamp')
    list_filter = ('is_correct', 'timestamp')
    search_fields = ('student__username', 'question__title')


@admin.register(AcademyUpdate)
class AcademyUpdateAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'target_audience', 'is_pinned', 'teacher', 'created_at')
    list_filter = ('category', 'target_audience', 'is_pinned', 'created_at')
    search_fields = ('title', 'content', 'teacher__username')
    ordering = ('-is_pinned', '-created_at')
