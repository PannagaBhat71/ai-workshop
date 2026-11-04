from django import forms
from .models import AptitudeQuestion, AcademyUpdate, Quiz, WeeklyNewsletter, Opportunity, StudyMaterial
from account.forms import StyledFormMixin


class AptitudeQuestionForm(StyledFormMixin, forms.ModelForm):
    class Meta:
        model = AptitudeQuestion
        fields = ['subject', 'title', 'topic', 'difficulty', 'access_tier', 'question_text', 'option_a', 'option_b', 'option_c', 'option_d', 'correct_option', 'explanation']
        widgets = {
            'subject': forms.Select(attrs={'id': 'id_subject'}),
            'title': forms.TextInput(attrs={'placeholder': 'e.g. Work and Days Ratio / JLPT N4 Kanji Meaning', 'id': 'id_title'}),
            'question_text': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Type or dictate problem statement...', 'id': 'id_question_text'}),
            'option_a': forms.TextInput(attrs={'placeholder': 'Option A value', 'id': 'id_option_a'}),
            'option_b': forms.TextInput(attrs={'placeholder': 'Option B value', 'id': 'id_option_b'}),
            'option_c': forms.TextInput(attrs={'placeholder': 'Option C value', 'id': 'id_option_c'}),
            'option_d': forms.TextInput(attrs={'placeholder': 'Option D value', 'id': 'id_option_d'}),
            'correct_option': forms.Select(attrs={'id': 'id_correct_option'}),
            'explanation': forms.Textarea(attrs={'rows': 2, 'placeholder': 'Step-by-step reasoning or formula...', 'id': 'id_explanation'}),
        }


class AcademyUpdateForm(StyledFormMixin, forms.ModelForm):
    class Meta:
        model = AcademyUpdate
        fields = ['title', 'category', 'target_audience', 'content']
        widgets = {
            'title': forms.TextInput(attrs={'placeholder': 'e.g. Upcoming Mock Test Series 4'}),
            'content': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Full announcement details...'}),
        }


class QuizForm(StyledFormMixin, forms.ModelForm):
    class Meta:
        model = Quiz
        fields = ['title', 'description', 'quiz_type', 'target_audience', 'duration_minutes', 'pass_percentage', 'scheduled_start_time', 'scheduled_end_time', 'is_published', 'questions']
        widgets = {
            'title': forms.TextInput(attrs={'placeholder': 'e.g. Master Aptitude Speed Test #1'}),
            'description': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Instructions and syllabus...'}),
            'scheduled_start_time': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'scheduled_end_time': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'questions': forms.SelectMultiple(attrs={'class': 'form-select', 'size': '6'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['questions'].queryset = AptitudeQuestion.objects.all().order_by('subject', 'topic')
        self.fields['questions'].help_text = "Select questions (Strictly 20 questions enforced during the live quiz)."


class WeeklyNewsletterForm(StyledFormMixin, forms.ModelForm):
    class Meta:
        model = WeeklyNewsletter
        fields = ['title', 'issue_number', 'placement_strategies', 'job_market_requirements', 'content']
        widgets = {
            'title': forms.TextInput(attrs={'placeholder': 'e.g. Placement Playbook: Mastering Dynamic Programming'}),
            'content': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Editorial overview...'}),
            'placement_strategies': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Speed math tricks, interview rounds...'}),
            'job_market_requirements': forms.Textarea(attrs={'rows': 3, 'placeholder': 'In-demand skills, hiring trends...'}),
        }


class OpportunityForm(StyledFormMixin, forms.ModelForm):
    class Meta:
        model = Opportunity
        fields = ['company_name', 'role_title', 'opportunity_type', 'apply_url', 'eligibility', 'location', 'deadline', 'description']
        widgets = {
            'company_name': forms.TextInput(attrs={'placeholder': 'e.g. Rakuten / Infosys / Sony'}),
            'role_title': forms.TextInput(attrs={'placeholder': 'e.g. Software Development Engineer - 2026 Batch'}),
            'apply_url': forms.URLInput(attrs={'placeholder': 'https://careers.company.com/apply'}),
            'deadline': forms.DateInput(attrs={'type': 'date'}),
            'description': forms.Textarea(attrs={'rows': 3}),
        }


class StudyMaterialForm(StyledFormMixin, forms.ModelForm):
    class Meta:
        model = StudyMaterial
        fields = ['title', 'subject', 'target_audience', 'file', 'file_url', 'description']
        widgets = {
            'title': forms.TextInput(attrs={'placeholder': 'e.g. Quantitative Aptitude Formula Cheat Sheet PDF'}),
            'file_url': forms.URLInput(attrs={'placeholder': 'https://drive.google.com/...'}),
            'description': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Material overview...'}),
        }
