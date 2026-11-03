from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import User
from .forms import (
    UserLoginForm,
    ZenkenStudentSignUpForm,
    NonZenkenStudentSignUpForm,
    TeacherSignUpForm,
)


def home_view(request):
    """Public landing page highlighting the 3 account options."""
    if request.user.is_authenticated:
        return redirect('account:dashboard')
    return render(request, 'account/home.html')


def register_select_view(request):
    """Selection page to choose which account type to register."""
    if request.user.is_authenticated:
        return redirect('account:dashboard')
    return render(request, 'account/register_select.html')


def zenken_register_view(request):
    """Registration for Zenken Enrolled Students."""
    if request.user.is_authenticated:
        return redirect('account:dashboard')

    if request.method == 'POST':
        form = ZenkenStudentSignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(
                request,
                f"Welcome {user.first_name}! Your Zenken Student Account has been created successfully."
            )
            return redirect('app:zenken_dashboard')
    else:
        form = ZenkenStudentSignUpForm()

    return render(request, 'account/register.html', {
        'form': form,
        'role_title': 'Zenken Enrolled Student Registration',
        'role_badge': 'Zenken Student',
        'badge_class': 'bg-primary',
        'description': 'For students officially registered with Zenken India training & placement program.',
    })


def non_zenken_register_view(request):
    """Registration for Students Not Enrolled in Zenken."""
    if request.user.is_authenticated:
        return redirect('account:dashboard')

    if request.method == 'POST':
        form = NonZenkenStudentSignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(
                request,
                f"Welcome {user.first_name}! Your Student Account has been created successfully."
            )
            return redirect('app:non_zenken_dashboard')
    else:
        form = NonZenkenStudentSignUpForm()

    return render(request, 'account/register.html', {
        'form': form,
        'role_title': 'Non-Zenken Student Registration',
        'role_badge': 'Standard Student',
        'badge_class': 'bg-info text-dark',
        'description': 'For external students preparing for aptitude, competitive exams, and campus placements.',
    })


def teacher_register_view(request):
    """Registration for Teachers / Instructors."""
    if request.user.is_authenticated:
        return redirect('account:dashboard')

    if request.method == 'POST':
        form = TeacherSignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(
                request,
                f"Welcome Professor {user.first_name}! Your Teacher Account is now ready to upload aptitude tests and academy updates."
            )
            return redirect('app:teacher_dashboard')
    else:
        form = TeacherSignUpForm()

    return render(request, 'account/register.html', {
        'form': form,
        'role_title': 'Teacher & Faculty Registration',
        'role_badge': 'Teacher / Faculty',
        'badge_class': 'bg-success',
        'description': 'For academy instructors uploading quantitative aptitude questions and posting notices.',
    })


def user_login_view(request):
    """Custom login view with dynamic role-based redirect."""
    if request.user.is_authenticated:
        return redirect('account:dashboard')

    if request.method == 'POST':
        form = UserLoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f"Welcome back, {user.first_name or user.username}!")
            return redirect('account:dashboard')
        else:
            messages.error(request, "Invalid username or password. Please try again.")
    else:
        form = UserLoginForm()

    return render(request, 'account/login.html', {'form': form})


@login_required
def dashboard_dispatcher_view(request):
    """Redirects the authenticated user to their role-specific dashboard."""
    user = request.user
    if user.is_teacher:
        return redirect('app:teacher_dashboard')
    elif user.is_zenken_student:
        return redirect('app:zenken_dashboard')
    elif user.is_non_zenken_student:
        return redirect('app:non_zenken_dashboard')
    else:
        # Fallback for superuser or uncategorized accounts
        return redirect('app:teacher_dashboard')


@login_required
def user_logout_view(request):
    """Logs out the user and redirects to the landing page."""
    logout(request)
    messages.info(request, "You have been successfully logged out.")
    return redirect('account:home')
