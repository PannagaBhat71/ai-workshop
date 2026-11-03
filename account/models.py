from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    class Role(models.TextChoices):
        ZENKEN_STUDENT = 'ZENKEN_STUDENT', 'Zenken Enrolled Student'
        NON_ZENKEN_STUDENT = 'NON_ZENKEN_STUDENT', 'Non-Zenken Student'
        TEACHER = 'TEACHER', 'Teacher'

    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.NON_ZENKEN_STUDENT,
        help_text="Account role: Zenken student, Non-Zenken student, or Teacher",
    )
    phone_number = models.CharField(max_length=20, blank=True)

    @property
    def is_teacher(self):
        return self.role == self.Role.TEACHER or self.is_superuser

    @property
    def is_zenken_student(self):
        return self.role == self.Role.ZENKEN_STUDENT

    @property
    def is_non_zenken_student(self):
        return self.role == self.Role.NON_ZENKEN_STUDENT

    @property
    def profile(self):
        if self.role == self.Role.ZENKEN_STUDENT and hasattr(self, 'zenken_profile'):
            return self.zenken_profile
        elif self.role == self.Role.NON_ZENKEN_STUDENT and hasattr(self, 'non_zenken_profile'):
            return self.non_zenken_profile
        elif self.role == self.Role.TEACHER and hasattr(self, 'teacher_profile'):
            return self.teacher_profile
        return None

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"


class ZenkenStudentProfile(models.Model):
    JAPANESE_LEVEL_CHOICES = [
        ('BEGINNER', 'Beginner / Zero level'),
        ('N5', 'JLPT N5 (Elementary)'),
        ('N4', 'JLPT N4 (Pre-Intermediate)'),
        ('N3', 'JLPT N3 (Intermediate)'),
        ('N2', 'JLPT N2 (Pre-Advanced)'),
        ('N1', 'JLPT N1 (Advanced)'),
    ]

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='zenken_profile',
    )
    zenken_id = models.CharField(
        max_length=50,
        unique=True,
        help_text="Official Zenken Registration ID (e.g., ZK-2026-101)",
    )
    batch_name = models.CharField(
        max_length=100,
        help_text="Enrolled Zenken Batch / Program Name",
    )
    japanese_level = models.CharField(
        max_length=20,
        choices=JAPANESE_LEVEL_CHOICES,
        default='BEGINNER',
    )
    college_name = models.CharField(max_length=150)
    enrolled_date = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"Zenken Profile: {self.user.username} [{self.zenken_id}]"


class NonZenkenStudentProfile(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='non_zenken_profile',
    )
    institution_name = models.CharField(
        max_length=150,
        help_text="Current College / University / Institute",
    )
    target_exam_or_goal = models.CharField(
        max_length=150,
        help_text="Target Goal (e.g. Campus Placement, Aptitude Prep, GATE)",
    )
    graduation_year = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="Expected Year of Graduation",
    )

    def __str__(self):
        return f"Non-Zenken Profile: {self.user.username} ({self.institution_name})"


class TeacherProfile(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='teacher_profile',
    )
    employee_id = models.CharField(
        max_length=50,
        unique=True,
        help_text="Teacher / Staff ID",
    )
    department = models.CharField(
        max_length=100,
        default="Quantitative Aptitude & Placement Training",
    )
    qualification = models.CharField(max_length=150, blank=True)
    bio = models.TextField(blank=True, help_text="Short bio or subject background")

    def __str__(self):
        return f"Teacher: {self.user.username} - {self.department}"
