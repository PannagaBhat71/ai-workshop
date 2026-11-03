from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import ZenkenStudentProfile, NonZenkenStudentProfile, TeacherProfile

User = get_user_model()


class StyledFormMixin:
    """Helper mixin to inject bootstrap classes into form widgets."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if isinstance(field.widget, (forms.CheckboxInput, forms.RadioSelect)):
                field.widget.attrs.setdefault('class', 'form-check-input')
            elif isinstance(field.widget, forms.Select):
                field.widget.attrs.setdefault('class', 'form-select')
            else:
                field.widget.attrs.setdefault('class', 'form-control')


class UserLoginForm(StyledFormMixin, AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({
            'placeholder': 'Enter your username',
            'autofocus': True,
        })
        self.fields['password'].widget.attrs.update({
            'placeholder': 'Enter your password',
        })


class ZenkenStudentSignUpForm(StyledFormMixin, UserCreationForm):
    first_name = forms.CharField(max_length=30, required=True, widget=forms.TextInput(attrs={'placeholder': 'First Name'}))
    last_name = forms.CharField(max_length=30, required=True, widget=forms.TextInput(attrs={'placeholder': 'Last Name'}))
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={'placeholder': 'student@example.com'}))
    phone_number = forms.CharField(max_length=20, required=False, widget=forms.TextInput(attrs={'placeholder': '+91 98765 43210'}))

    # Zenken profile fields
    zenken_id = forms.CharField(
        max_length=50,
        required=True,
        label="Zenken Student ID",
        widget=forms.TextInput(attrs={'placeholder': 'e.g. ZK-2026-IND-042'}),
        help_text="Your official enrolled ID provided by Zenken."
    )
    batch_name = forms.CharField(
        max_length=100,
        required=True,
        label="Batch / Program",
        widget=forms.TextInput(attrs={'placeholder': 'e.g. Batch 2026 - Japan IT Placement Track'}),
    )
    japanese_level = forms.ChoiceField(
        choices=ZenkenStudentProfile.JAPANESE_LEVEL_CHOICES,
        required=True,
        label="Current Japanese Level",
    )
    college_name = forms.CharField(
        max_length=150,
        required=True,
        label="College / Institute Name",
        widget=forms.TextInput(attrs={'placeholder': 'e.g. National Institute of Engineering'}),
    )

    class Meta(UserCreationForm.Meta):
        model = User
        fields = (
            'username',
            'first_name',
            'last_name',
            'email',
            'phone_number',
            'zenken_id',
            'batch_name',
            'japanese_level',
            'college_name',
        )

    def clean_zenken_id(self):
        zenken_id = self.cleaned_data.get('zenken_id', '').strip()
        if ZenkenStudentProfile.objects.filter(zenken_id__iexact=zenken_id).exists():
            raise forms.ValidationError("This Zenken Student ID is already registered.")
        return zenken_id

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = User.Role.ZENKEN_STUDENT
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.email = self.cleaned_data['email']
        user.phone_number = self.cleaned_data.get('phone_number', '')
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


class NonZenkenStudentSignUpForm(StyledFormMixin, UserCreationForm):
    first_name = forms.CharField(max_length=30, required=True, widget=forms.TextInput(attrs={'placeholder': 'First Name'}))
    last_name = forms.CharField(max_length=30, required=True, widget=forms.TextInput(attrs={'placeholder': 'Last Name'}))
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={'placeholder': 'student@example.com'}))
    phone_number = forms.CharField(max_length=20, required=False, widget=forms.TextInput(attrs={'placeholder': '+91 98765 43210'}))

    # Non-Zenken profile fields
    institution_name = forms.CharField(
        max_length=150,
        required=True,
        label="College / University",
        widget=forms.TextInput(attrs={'placeholder': 'e.g. Bangalore Institute of Technology'}),
    )
    target_exam_or_goal = forms.CharField(
        max_length=150,
        required=True,
        label="Target Exam / Goal",
        widget=forms.TextInput(attrs={'placeholder': 'e.g. IT Campus Placement, Quantitative Aptitude, CAT'}),
    )
    graduation_year = forms.IntegerField(
        required=False,
        label="Graduation Year",
        widget=forms.NumberInput(attrs={'placeholder': '2026'}),
    )

    class Meta(UserCreationForm.Meta):
        model = User
        fields = (
            'username',
            'first_name',
            'last_name',
            'email',
            'phone_number',
            'institution_name',
            'target_exam_or_goal',
            'graduation_year',
        )

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = User.Role.NON_ZENKEN_STUDENT
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.email = self.cleaned_data['email']
        user.phone_number = self.cleaned_data.get('phone_number', '')
        if commit:
            user.save()
            NonZenkenStudentProfile.objects.create(
                user=user,
                institution_name=self.cleaned_data['institution_name'],
                target_exam_or_goal=self.cleaned_data['target_exam_or_goal'],
                graduation_year=self.cleaned_data.get('graduation_year'),
            )
        return user


class TeacherSignUpForm(StyledFormMixin, UserCreationForm):
    first_name = forms.CharField(max_length=30, required=True, widget=forms.TextInput(attrs={'placeholder': 'First Name'}))
    last_name = forms.CharField(max_length=30, required=True, widget=forms.TextInput(attrs={'placeholder': 'Last Name'}))
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={'placeholder': 'teacher@zenken-academy.com'}))
    phone_number = forms.CharField(max_length=20, required=False, widget=forms.TextInput(attrs={'placeholder': '+91 98765 43210'}))

    # Teacher profile fields
    employee_id = forms.CharField(
        max_length=50,
        required=True,
        label="Teacher / Employee ID",
        widget=forms.TextInput(attrs={'placeholder': 'e.g. TCH-QA-2026'}),
    )
    department = forms.CharField(
        max_length=100,
        required=True,
        label="Department / Subject",
        initial="Quantitative Aptitude & Placement Training",
        widget=forms.TextInput(attrs={'placeholder': 'e.g. Quantitative Aptitude & Reasoning'}),
    )
    qualification = forms.CharField(
        max_length=150,
        required=False,
        label="Highest Qualification",
        widget=forms.TextInput(attrs={'placeholder': 'e.g. M.Tech / M.Sc Mathematics / CAT 99.8%ile'}),
    )
    bio = forms.CharField(
        required=False,
        label="Bio / Subject Summary",
        widget=forms.Textarea(attrs={'rows': 3, 'placeholder': 'Brief intro about your teaching focus and aptitude syllabus...'}),
    )

    class Meta(UserCreationForm.Meta):
        model = User
        fields = (
            'username',
            'first_name',
            'last_name',
            'email',
            'phone_number',
            'employee_id',
            'department',
            'qualification',
            'bio',
        )

    def clean_employee_id(self):
        employee_id = self.cleaned_data.get('employee_id', '').strip()
        if TeacherProfile.objects.filter(employee_id__iexact=employee_id).exists():
            raise forms.ValidationError("This Employee ID is already registered.")
        return employee_id

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = User.Role.TEACHER
        user.is_staff = True  # Allows teachers staff access if desired
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.email = self.cleaned_data['email']
        user.phone_number = self.cleaned_data.get('phone_number', '')
        if commit:
            user.save()
            TeacherProfile.objects.create(
                user=user,
                employee_id=self.cleaned_data['employee_id'],
                department=self.cleaned_data['department'],
                qualification=self.cleaned_data.get('qualification', ''),
                bio=self.cleaned_data.get('bio', ''),
            )
        return user

