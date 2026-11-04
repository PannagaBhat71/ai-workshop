from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import ZenkenStudentProfile, NonZenkenStudentProfile

User = get_user_model()


class StyledFormMixin:
    """Inject standard Bootstrap classes into form widgets."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for _, field in self.fields.items():
            if isinstance(field.widget, (forms.CheckboxInput, forms.RadioSelect)):
                field.widget.attrs.setdefault('class', 'form-check-input')
            elif isinstance(field.widget, forms.Select):
                field.widget.attrs.setdefault('class', 'form-select')
            else:
                field.widget.attrs.setdefault('class', 'form-control')


class UserLoginForm(StyledFormMixin, AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({'placeholder': 'Username or faculty name', 'autofocus': True})
        self.fields['password'].widget.attrs.update({'placeholder': 'Password (2654 for teachers)'})


class BaseStudentSignUpForm(StyledFormMixin, UserCreationForm):
    first_name = forms.CharField(max_length=30, required=True, widget=forms.TextInput(attrs={'placeholder': 'First Name'}))
    last_name = forms.CharField(max_length=30, required=True, widget=forms.TextInput(attrs={'placeholder': 'Last Name'}))
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={'placeholder': 'name.branch26@sahyadri.edu.in'}),
        help_text="Must be your official Sahyadri College email (@sahyadri.edu.in)."
    )
    phone_number = forms.CharField(max_length=20, required=False, widget=forms.TextInput(attrs={'placeholder': '+91 98765 43210'}))

    def clean_email(self):
        email = self.cleaned_data.get('email', '').strip().lower()
        if not email.endswith('@sahyadri.edu.in'):
            raise forms.ValidationError("Official college email required: Email must strictly end with @sahyadri.edu.in")
        return email


class ZenkenStudentSignUpForm(BaseStudentSignUpForm):
    zenken_id = forms.CharField(
        max_length=50, required=True, label="Zenken Student ID",
        widget=forms.TextInput(attrs={'placeholder': 'e.g. ZK-2026-IND-042'}),
        help_text="Your official enrolled ID provided by Zenken."
    )
    batch_name = forms.CharField(
        max_length=100, required=True, label="Batch / Program",
        initial="Batch 2026 - Japan IT Placement Track",
        widget=forms.TextInput(attrs={'placeholder': 'e.g. Batch 2026 - Japan IT Placement Track'})
    )
    japanese_level = forms.ChoiceField(choices=ZenkenStudentProfile.JAPANESE_LEVEL_CHOICES, required=True, label="Current Japanese Level")
    college_name = forms.CharField(
        max_length=150, required=True, label="College / Institute Name",
        initial="Sahyadri College of Engineering & Management",
        widget=forms.TextInput(attrs={'placeholder': 'Sahyadri College of Engineering & Management'})
    )

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'phone_number', 'zenken_id', 'batch_name', 'japanese_level', 'college_name')

    def clean_zenken_id(self):
        zenken_id = self.cleaned_data.get('zenken_id', '').strip()
        if ZenkenStudentProfile.objects.filter(zenken_id__iexact=zenken_id).exists():
            raise forms.ValidationError("This Zenken Student ID is already registered.")
        return zenken_id

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = User.Role.ZENKEN_STUDENT
        user.first_name, user.last_name = self.cleaned_data['first_name'], self.cleaned_data['last_name']
        user.email, user.phone_number = self.cleaned_data['email'], self.cleaned_data.get('phone_number', '')
        if commit:
            user.save()
            ZenkenStudentProfile.objects.create(
                user=user,
                zenken_id=self.cleaned_data['zenken_id'],
                batch_name=self.cleaned_data['batch_name'],
                japanese_level=self.cleaned_data['japanese_level'],
                college_name=self.cleaned_data['college_name'],
            )
        return user


class NonZenkenStudentSignUpForm(BaseStudentSignUpForm):
    institution_name = forms.CharField(
        max_length=150, required=True, label="College / Institution",
        initial="Sahyadri College of Engineering & Management",
        widget=forms.TextInput(attrs={'placeholder': 'Sahyadri College of Engineering & Management'})
    )
    target_exam_or_goal = forms.CharField(
        max_length=150, required=True, label="Target Exam / Goal",
        widget=forms.TextInput(attrs={'placeholder': 'e.g. IT Campus Placement, Quantitative Aptitude, CAT'})
    )
    graduation_year = forms.IntegerField(required=False, label="Graduation Year", initial=2026, widget=forms.NumberInput(attrs={'placeholder': '2026'}))

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'phone_number', 'institution_name', 'target_exam_or_goal', 'graduation_year')

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = User.Role.NON_ZENKEN_STUDENT
        user.first_name, user.last_name = self.cleaned_data['first_name'], self.cleaned_data['last_name']
        user.email, user.phone_number = self.cleaned_data['email'], self.cleaned_data.get('phone_number', '')
        if commit:
            user.save()
            NonZenkenStudentProfile.objects.create(
                user=user,
                institution_name=self.cleaned_data['institution_name'],
                target_exam_or_goal=self.cleaned_data['target_exam_or_goal'],
                graduation_year=self.cleaned_data.get('graduation_year'),
            )
        return user
