from django import forms
from .models import AptitudeQuestion, AcademyUpdate
from account.forms import StyledFormMixin


class AptitudeQuestionForm(StyledFormMixin, forms.ModelForm):
    class Meta:
        model = AptitudeQuestion
        fields = [
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
            'title': forms.TextInput(attrs={'placeholder': 'e.g. Work and Days Ratio Problem'}),
            'question_text': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Type the full aptitude problem statement here...'}),
            'option_a': forms.TextInput(attrs={'placeholder': 'Option A value / answer'}),
            'option_b': forms.TextInput(attrs={'placeholder': 'Option B value / answer'}),
            'option_c': forms.TextInput(attrs={'placeholder': 'Option C value / answer'}),
            'option_d': forms.TextInput(attrs={'placeholder': 'Option D value / answer'}),
            'explanation': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Provide step-by-step mathematical reasoning, shortcut tricks, and the final logic...'}),
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

