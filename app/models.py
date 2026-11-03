from django.db import models
from django.conf import settings
from django.utils import timezone
from datetime import timedelta


class AptitudeQuestion(models.Model):
    SUBJECT_CHOICES = [
        ('APTITUDE', 'Quantitative Aptitude'),
        ('JAPANESE', 'Japanese Language (Zenken Exclusive)'),
    ]

    TOPIC_CHOICES = [
        # Quantitative Aptitude Topics (aligned with docx resource banks)
        ('ARITHMETIC', 'Arithmetic: Comprehensive Practice'),
        ('PERCENTAGE', 'Arithmetic: Percentages & Fractions'),
        ('PROFIT_LOSS', 'Arithmetic: Profit, Loss & Discount'),
        ('TIME_WORK', 'Arithmetic: Time & Work / Pipes & Cisterns'),
        ('SPEED_DISTANCE', 'Arithmetic: Time, Speed & Distance / Trains'),
        ('RATIO_PROPORTION', 'Arithmetic: Ratio, Proportion & Mixtures'),
        ('AVERAGES', 'Arithmetic: Averages & Allegations'),
        ('NUMBER_SYSTEM', 'Number System, HCF, LCM & Numeracy'),
        ('ALGEBRA', 'Algebra: Linear, Quadratic Equations & Logarithms'),
        ('GEOMETRY', 'Geometry, Trigonometry & Mensuration'),
        ('MODERN_MATH', 'Modern Math: Permutations, Combinations & Probability'),
        ('DATA_INTERPRETATION', 'Data Interpretation (Tables, Bar, Line & Pie Charts)'),
        ('LOGICAL_REASONING', 'Logical Reasoning & Analytical Aptitude'),
        ('OTHER_APTITUDE', 'General Aptitude'),
        # Japanese Language Topics (Exclusive to Zenken Scholars)
        ('JP_KANJI', 'Japanese: Kanji & Reading (漢字)'),
        ('JP_VOCAB', 'Japanese: Vocabulary & Meanings (語彙)'),
        ('JP_GRAMMAR', 'Japanese: JLPT Grammar (文法)'),
        ('JP_READING', 'Japanese: Reading Comprehension (読解)'),
        ('JP_CULTURE', 'Japanese: Corporate Culture & Business Etiquette (ビジネスマナー)'),
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
    subject = models.CharField(
        max_length=20,
        choices=SUBJECT_CHOICES,
        default='APTITUDE',
        help_text="Aptitude (Open/Zenken) or Japanese (Zenken Exclusive)",
    )
    title = models.CharField(
        max_length=200,
        help_text="Short title or concept (e.g. Work Equivalence / JLPT N4 Kanji)",
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
        help_text="Step-by-step mathematical reasoning or language explanation",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        if self.subject == 'JAPANESE':
            self.access_tier = 'ZENKEN_ONLY'
        super().save(*args, **kwargs)

    def __str__(self):
        return f"[{self.get_topic_display()}] {self.title}"


class Quiz(models.Model):
    QUIZ_TYPE_CHOICES = [
        ('APTITUDE', 'Quantitative Aptitude Quiz'),
        ('JAPANESE', 'Japanese Language Quiz (Zenken Exclusive)'),
    ]

    AUDIENCE_CHOICES = [
        ('ALL', 'All Students (Open & Zenken)'),
        ('ZENKEN_ONLY', 'Zenken Enrolled Students Only'),
        ('NON_ZENKEN_ONLY', 'Non-Zenken Students Only'),
    ]

    teacher = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='created_quizzes',
    )
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    quiz_type = models.CharField(
        max_length=20,
        choices=QUIZ_TYPE_CHOICES,
        default='APTITUDE',
    )
    target_audience = models.CharField(
        max_length=20,
        choices=AUDIENCE_CHOICES,
        default='ALL',
    )
    duration_minutes = models.PositiveIntegerField(
        default=20,
        help_text="Duration in minutes (e.g. 20 mins for 20 questions)",
    )
    pass_percentage = models.PositiveIntegerField(
        default=50,
        help_text="Passing score percentage",
    )
    scheduled_start_time = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Scheduled live start date & time",
    )
    scheduled_end_time = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Scheduled closing date & time",
    )
    is_published = models.BooleanField(
        default=True,
        help_text="Make this quiz active/posted for students to attempt",
    )
    questions = models.ManyToManyField(
        AptitudeQuestion,
        related_name='quizzes',
        blank=True,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        if self.quiz_type == 'JAPANESE':
            self.target_audience = 'ZENKEN_ONLY'
        super().save(*args, **kwargs)

    @property
    def is_live(self):
        now = timezone.now()
        if not self.is_published:
            return False
        if self.scheduled_start_time and now < self.scheduled_start_time:
            return False
        if self.scheduled_end_time and now > self.scheduled_end_time:
            return False
        return True

    def __str__(self):
        return f"{self.title} ({self.get_quiz_type_display()})"


class QuizAttempt(models.Model):
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='quiz_attempts',
    )
    quiz = models.ForeignKey(
        Quiz,
        on_delete=models.CASCADE,
        related_name='attempts',
    )
    score = models.PositiveIntegerField(default=0)
    total_questions = models.PositiveIntegerField(default=20)
    percentage = models.FloatField(default=0.0)
    passed = models.BooleanField(default=False)
    time_taken_seconds = models.PositiveIntegerField(default=0)
    tab_switch_violations = models.PositiveIntegerField(default=0)
    completed_at = models.DateTimeField(auto_now_add=True)
    answers_data = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ['-completed_at']

    def __str__(self):
        return f"{self.student.username} - {self.quiz.title} ({self.score}/{self.total_questions} - {self.percentage:.1f}%)"


class QuestionPracticeLog(models.Model):
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='practice_logs',
    )
    question = models.ForeignKey(
        AptitudeQuestion,
        on_delete=models.CASCADE,
        related_name='practice_logs',
    )
    chosen_option = models.CharField(max_length=1)
    is_correct = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.student.username} practiced {self.question.title}: {'Correct' if self.is_correct else 'Wrong'}"


class UserActivityStreak(models.Model):
    """Tracks daily activity streaks and leaderboard points for students."""
    student = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='activity_streak',
    )
    current_streak = models.PositiveIntegerField(default=0)
    longest_streak = models.PositiveIntegerField(default=0)
    total_points = models.PositiveIntegerField(default=0)
    quizzes_completed = models.PositiveIntegerField(default=0)
    practice_completed = models.PositiveIntegerField(default=0)
    last_active_date = models.DateField(null=True, blank=True)

    def record_activity(self, points=10, is_quiz=False):
        today = timezone.localdate()
        if self.last_active_date == today:
            pass  # Already logged today for streak
        elif self.last_active_date == today - timedelta(days=1):
            self.current_streak += 1
            if self.current_streak > self.longest_streak:
                self.longest_streak = self.current_streak
        else:
            self.current_streak = 1
            if self.longest_streak == 0:
                self.longest_streak = 1

        self.last_active_date = today
        self.total_points += points
        if is_quiz:
            self.quizzes_completed += 1
        else:
            self.practice_completed += 1
        self.save()

    def __str__(self):
        return f"{self.student.username} Streak: {self.current_streak} days ({self.total_points} pts)"


class WeeklyNewsletter(models.Model):
    """Weekly placement newsletter covering preparation strategies and market requirements."""
    title = models.CharField(max_length=220)
    issue_number = models.PositiveIntegerField(default=1)
    content = models.TextField(help_text="Main newsletter overview & editorial")
    placement_strategies = models.TextField(help_text="Actionable placement & test strategies")
    job_market_requirements = models.TextField(help_text="Current industry trends & technical demands")
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='authored_newsletters',
    )
    published_date = models.DateField(auto_now_add=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-issue_number', '-published_date']

    def __str__(self):
        return f"Issue #{self.issue_number}: {self.title}"


class Opportunity(models.Model):
    """Job, Internship, and Placement opportunities links."""
    TYPE_CHOICES = [
        ('FULL_TIME', 'Full-Time Job Opportunity'),
        ('INTERNSHIP', 'Internship Program'),
        ('JAPAN_DRIVE', 'Zenken Japan Recruitment Drive'),
        ('HACKATHON', 'Competitive Hackathon / Hiring Challenge'),
    ]

    company_name = models.CharField(max_length=150)
    role_title = models.CharField(max_length=150)
    opportunity_type = models.CharField(max_length=30, choices=TYPE_CHOICES, default='FULL_TIME')
    apply_url = models.URLField(help_text="Direct link for students to apply")
    eligibility = models.CharField(max_length=200, help_text="e.g. 2026 Batch B.E / B.Tech (All Branches)")
    location = models.CharField(max_length=150, default="Bangalore / Tokyo / Remote")
    deadline = models.DateField(null=True, blank=True)
    description = models.TextField(blank=True)
    posted_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='posted_opportunities',
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.company_name} - {self.role_title}"


class StudyMaterial(models.Model):
    """Student documents and materials uploaded by teachers."""
    SUBJECT_CHOICES = [
        ('APTITUDE', 'Quantitative Aptitude'),
        ('JAPANESE', 'Japanese Language'),
        ('REASONING', 'Logical Reasoning'),
        ('PLACEMENT', 'Placement Preparation & Interview Guides'),
    ]
    AUDIENCE_CHOICES = [
        ('ALL', 'All Students'),
        ('ZENKEN_ONLY', 'Zenken Enrolled Students Only'),
        ('NON_ZENKEN_ONLY', 'Non-Zenken Students Only'),
    ]

    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    file = models.FileField(upload_to='study_materials/', blank=True, null=True)
    file_url = models.URLField(blank=True, help_text="Direct link if hosting on Google Drive / external URL")
    subject = models.CharField(max_length=30, choices=SUBJECT_CHOICES, default='APTITUDE')
    target_audience = models.CharField(max_length=20, choices=AUDIENCE_CHOICES, default='ALL')
    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='uploaded_materials',
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"[{self.get_subject_display()}] {self.title}"


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
