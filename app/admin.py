from django.contrib import admin
from .models import AptitudeQuestion, AcademyUpdate


@admin.register(AptitudeQuestion)
class AptitudeQuestionAdmin(admin.ModelAdmin):
    list_display = ('title', 'topic', 'difficulty', 'access_tier', 'correct_option', 'teacher', 'created_at')
    list_filter = ('topic', 'difficulty', 'access_tier', 'created_at')
    search_fields = ('title', 'question_text', 'explanation', 'teacher__username')
    ordering = ('-created_at',)


@admin.register(AcademyUpdate)
class AcademyUpdateAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'target_audience', 'is_pinned', 'teacher', 'created_at')
    list_filter = ('category', 'target_audience', 'is_pinned', 'created_at')
    search_fields = ('title', 'content', 'teacher__username')
    ordering = ('-is_pinned', '-created_at')
