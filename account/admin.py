from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, ZenkenStudentProfile, NonZenkenStudentProfile, TeacherProfile


class ZenkenStudentProfileInline(admin.StackedInline):
    model = ZenkenStudentProfile
    can_delete = False
    verbose_name_plural = 'Zenken Student Profile'
    fk_name = 'user'


class NonZenkenStudentProfileInline(admin.StackedInline):
    model = NonZenkenStudentProfile
    can_delete = False
    verbose_name_plural = 'Non-Zenken Student Profile'
    fk_name = 'user'


class TeacherProfileInline(admin.StackedInline):
    model = TeacherProfile
    can_delete = False
    verbose_name_plural = 'Teacher Profile'
    fk_name = 'user'


@admin.register(User)
class CustomUserAdmin(BaseUserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'role', 'is_staff')
    list_filter = ('role', 'is_staff', 'is_superuser', 'is_active')
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Role & Contact Info', {
            'fields': ('role', 'phone_number'),
        }),
    )
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ('Role & Contact Info', {
            'fields': ('role', 'phone_number'),
        }),
    )
    inlines = (
        ZenkenStudentProfileInline,
        NonZenkenStudentProfileInline,
        TeacherProfileInline,
    )


@admin.register(ZenkenStudentProfile)
class ZenkenStudentProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'zenken_id', 'batch_name', 'japanese_level', 'college_name', 'enrolled_date')
    search_fields = ('user__username', 'zenken_id', 'college_name', 'batch_name')
    list_filter = ('japanese_level',)


@admin.register(NonZenkenStudentProfile)
class NonZenkenStudentProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'institution_name', 'target_exam_or_goal', 'graduation_year')
    search_fields = ('user__username', 'institution_name', 'target_exam_or_goal')
    list_filter = ('graduation_year',)


@admin.register(TeacherProfile)
class TeacherProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'employee_id', 'department', 'qualification')
    search_fields = ('user__username', 'employee_id', 'department')
