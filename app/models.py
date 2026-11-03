from django.db import models
from django.conf import settings


class AptitudeQuestion(models.Model):
    TOPIC_CHOICES = [
        ('PERCENTAGE', 'Percentages & Fractions'),
        ('PROFIT_LOSS', 'Profit, Loss & Discount'),
        ('TIME_WORK', 'Time and Work / Pipes & Cisterns'),
        ('SPEED_DISTANCE', 'Time, Speed & Distance / Trains / Boats'),
        ('RATIO_PROPORTION', 'Ratio, Proportion & Mixtures'),
        ('NUMBER_SYSTEM', 'Number System & Divisibility'),
        ('PROBABILITY_PERM', 'Permutations, Combinations & Probability'),
        ('SIMPLE_COMPOUND_INT', 'Simple & Compound Interest'),
        ('AVERAGES', 'Averages & Allegations'),
        ('DATA_INTERPRETATION', 'Data Interpretation (Charts & Tables)'),
        ('LOGICAL_REASONING', 'Logical Reasoning & Analytical Aptitude'),
        ('OTHER', 'General Aptitude'),
    ]

    DIFFICULTY_CHOICES = [
        ('EASY', 'Easy'),
        ('MEDIUM', 'Medium'),
        ('HARD', 'Hard / Advanced'),
    ]

    CORRECT_OPTION_CHOICES = [
        ('A', 'Option A'),
        ('B', 'Option B'),
        ('C', 'Option C'),
        ('D', 'Option D'),
    ]

    ACCESS_CHOICES = [
        ('ALL', 'Open to All Students (Zenken & Non-Zenken)'),
        ('ZENKEN_ONLY', 'Zenken Enrolled Students Only (Exclusive)'),
    ]

    teacher = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='aptitude_questions',
    )
    title = models.CharField(
        max_length=200,
        help_text="Short title or concept (e.g. Work Equivalence Problem)",
    )
    topic = models.CharField(
        max_length=50,
        choices=TOPIC_CHOICES,
        default='PERCENTAGE',
    )
    difficulty = models.CharField(
        max_length=20,
        choices=DIFFICULTY_CHOICES,
        default='MEDIUM',
    )
    access_tier = models.CharField(
        max_length=20,
        choices=ACCESS_CHOICES,
        default='ALL',
        help_text="Choose who can view and practice this question",
    )
    question_text = models.TextField(
        help_text="Enter the full problem statement",
    )
    option_a = models.CharField(max_length=255, verbose_name="Option A")
    option_b = models.CharField(max_length=255, verbose_name="Option B")
    option_c = models.CharField(max_length=255, verbose_name="Option C")
    option_d = models.CharField(max_length=255, verbose_name="Option D")
    correct_option = models.CharField(
        max_length=1,
        choices=CORRECT_OPTION_CHOICES,
        help_text="Select the correct answer option",
    )
    explanation = models.TextField(
        blank=True,
        help_text="Step-by-step mathematical explanation / shortcut formula",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"[{self.get_topic_display()}] {self.title} ({self.get_difficulty_display()})"


class AcademyUpdate(models.Model):
    CATEGORY_CHOICES = [
        ('GENERAL', 'General Academy Announcement'),
        ('WORKSHOP', 'Workshop / Masterclass Alert'),
        ('SCHEDULE', 'Class & Mock Test Schedule'),
        ('PLACEMENT', 'Placement / Interview Drive Update'),
        ('ZENKEN_EXCLUSIVE', 'Zenken Exclusive Notice / Japan Drive'),
    ]

    AUDIENCE_CHOICES = [
        ('ALL', 'All Students & Teachers'),
        ('ZENKEN_ONLY', 'Zenken Enrolled Students Only'),
        ('NON_ZENKEN_ONLY', 'Non-Zenken Students Only'),
    ]

    teacher = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='academy_updates',
    )
    title = models.CharField(max_length=200)
    category = models.CharField(
        max_length=50,
        choices=CATEGORY_CHOICES,
        default='GENERAL',
    )
    target_audience = models.CharField(
        max_length=20,
        choices=AUDIENCE_CHOICES,
        default='ALL',
        help_text="Select target audience for this update",
    )
    content = models.TextField(
        help_text="Full update description or announcement details",
    )
    is_pinned = models.BooleanField(
        default=False,
        help_text="Pin this notice at the top of the updates feed",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-is_pinned', '-created_at']

    def __str__(self):
        return f"[{self.get_category_display()}] {self.title}"
