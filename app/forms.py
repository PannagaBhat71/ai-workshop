from django import forms
from .models import AptitudeQuestion, AcademyUpdate, Quiz, WeeklyNewsletter, Opportunity, StudyMaterial
from account.forms import StyledFormMixin


class AptitudeQuestionForm(StyledFormMixin, forms.ModelForm):
    class Meta:
        model = AptitudeQuestion
        fields = [
            'subject',
            'title',
            'topic',
            'difficulty',
            'access_tier',
            'question_text',
            'option_a',
            'option_b',
            'option_c',
            'option_d',
            'correct_option',
            'explanation',
        ]
        widgets = {
            'subject': forms.Select(attrs={'id': 'id_subject', 'class': 'form-select'}),
            'title': forms.TextInput(attrs={'placeholder': 'e.g. Work and Days Ratio / JLPT N4 Kanji Meaning', 'id': 'id_title'}),
            'question_text': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Type or dictate the full problem statement here...', 'id': 'id_question_text'}),
            'option_a': forms.TextInput(attrs={'placeholder': 'Option A value / answer', 'id': 'id_option_a'}),
            'option_b': forms.TextInput(attrs={'placeholder': 'Option B value / answer', 'id': 'id_option_b'}),
            'option_c': forms.TextInput(attrs={'placeholder': 'Option C value / answer', 'id': 'id_option_c'}),
            'option_d': forms.TextInput(attrs={'placeholder': 'Option D value / answer', 'id': 'id_option_d'}),
            'correct_option': forms.Select(attrs={'id': 'id_correct_option'}),
            'explanation': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Step-by-step reasoning or formula...', 'id': 'id_explanation'}),
        }


class AcademyUpdateForm(StyledFormMixin, forms.ModelForm):
    class Meta:
        model = AcademyUpdate
        fields = [
            'title',
            'category',
            'target_audience',
            'is_pinned',
            'content',
        ]
        widgets = {
            'title': forms.TextInput(attrs={'placeholder': 'e.g. Upcoming Quantitative Aptitude Mock Test - Series 4'}),
            'content': forms.Textarea(attrs={'rows': 5, 'placeholder': 'Write the full announcement, guidelines, schedule, or instructions...'}),
        }


class QuizForm(StyledFormMixin, forms.ModelForm):
    class Meta:
        model = Quiz
        fields = [
            'title',
            'description',
            'quiz_type',
            'target_audience',
            'duration_minutes',
            'pass_percentage',
            'scheduled_start_time',
            'scheduled_end_time',
            'is_published',
            'questions',
        ]
        widgets = {
            'title': forms.TextInput(attrs={'placeholder': 'e.g. Master Aptitude Speed Test #1 / JLPT N4 Challenge'}),
            'description': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Instructions, syllabus, and rules for test takers...'}),
            'scheduled_start_time': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'scheduled_end_time': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'questions': forms.SelectMultiple(attrs={'class': 'form-select', 'size': '8'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['questions'].queryset = AptitudeQuestion.objects.all().order_by('subject', 'topic')
        self.fields['questions'].help_text = "Select questions for this quiz (Test will strictly enforce 20 questions during the assessment)."


class WeeklyNewsletterForm(StyledFormMixin, forms.ModelForm):
    class Meta:
        model = WeeklyNewsletter
        fields = [
            'title',
            'issue_number',
            'placement_strategies',
            'job_market_requirements',
            'content',
        ]
        widgets = {
            'title': forms.TextInput(attrs={'placeholder': 'e.g. Placement Playbook: Mastering Dynamic Programming & Japanese Aptitude'}),
            'content': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Editorial overview, week in review, and college milestones...'}),
            'placement_strategies': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Speed math tricks, group discussion tips, resume highlights...'}),
            'job_market_requirements': forms.Textarea(attrs={'rows': 4, 'placeholder': 'In-demand frameworks, IT hiring patterns, salary trends...'}),
        }


class OpportunityForm(StyledFormMixin, forms.ModelForm):
    class Meta:
        model = Opportunity
        fields = [
            'company_name',
            'role_title',
            'opportunity_type',
            'apply_url',
            'eligibility',
            'location',
            'deadline',
            'description',
        ]
        widgets = {
            'company_name': forms.TextInput(attrs={'placeholder': 'e.g. Rakuten Group / Infosys / Sony Tokyo'}),
            'role_title': forms.TextInput(attrs={'placeholder': 'e.g. Associate Software Engineer / IT Placement Track'}),
            'apply_url': forms.URLInput(attrs={'placeholder': 'https://careers.company.com/apply/...'}),
            'eligibility': forms.TextInput(attrs={'placeholder': 'e.g. 2026 Batch B.E / B.Tech (CSE, ISE, ECE) - Min 65% aggregate'}),
            'location': forms.TextInput(attrs={'placeholder': 'e.g. Tokyo, Japan / Bangalore / Hybrid'}),
            'deadline': forms.DateInput(attrs={'type': 'date'}),
            'description': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Role description, tech stack requirements, and test stages...'}),
        }


class StudyMaterialForm(StyledFormMixin, forms.ModelForm):
    class Meta:
        model = StudyMaterial
        fields = [
            'title',
            'subject',
            'target_audience',
            'file',
            'file_url',
            'description',
        ]
        widgets = {
            'title': forms.TextInput(attrs={'placeholder': 'e.g. Quantitative Aptitude Formula Handbook & Cheat Sheet'}),
            'file_url': forms.URLInput(attrs={'placeholder': 'https://drive.google.com/file/... (optional if uploading file)'}),
            'description': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Overview of the study notes, formulas, and syllabus covered...'}),
        }
