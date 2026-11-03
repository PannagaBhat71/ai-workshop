from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import User, TeacherProfile
from .forms import (
    UserLoginForm,
    ZenkenStudentSignUpForm,
    NonZenkenStudentSignUpForm,
)


def home_view(request):
    """Public landing page for scemquiz.arena."""
    if request.user.is_authenticated:
        return redirect('account:dashboard')
    return render(request, 'account/home.html')


def register_select_view(request):
    """Selection page strictly for students (Teachers log in directly with faculty pass)."""
    if request.user.is_authenticated:
        return redirect('account:dashboard')
    return render(request, 'account/register_select.html')


def zenken_register_view(request):
    """Registration for Zenken Enrolled Students (@sahyadri.edu.in required)."""
    if request.user.is_authenticated:
        return redirect('account:dashboard')

    if request.method == 'POST':
        form = ZenkenStudentSignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(
                request,
                f"Welcome {user.first_name}! Your Zenken Scholar account ({user.email}) is active."
            )
            return redirect('app:zenken_dashboard')
    else:
        form = ZenkenStudentSignUpForm()

    return render(request, 'account/register.html', {
        'form': form,
        'role_title': 'Zenken Scholar Registration',
        'role_badge': 'Zenken Enrolled Track',
        'badge_class': 'badge-zenken-exclusive',
        'description': 'For Sahyadri students officially enrolled in Zenken Japan Career Track. Requires @sahyadri.edu.in email.',
    })


def non_zenken_register_view(request):
    """Registration for Non-Zenken Students (@sahyadri.edu.in required)."""
    if request.user.is_authenticated:
        return redirect('account:dashboard')

    if request.method == 'POST':
        form = NonZenkenStudentSignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(
                request,
                f"Welcome {user.first_name}! Your Student account ({user.email}) is active."
            )
            return redirect('app:non_zenken_dashboard')
    else:
        form = NonZenkenStudentSignUpForm()

    return render(request, 'account/register.html', {
        'form': form,
        'role_title': 'Student Registration (Open Track)',
        'role_badge': 'Standard Student',
        'badge_class': 'bg-info text-dark',
        'description': 'For Sahyadri students preparing for campus placements and aptitude assessments. Requires @sahyadri.edu.in email.',
    })


def user_login_view(request):
    """
    Login view:
    - If any teacher enters their name and writes '2654' as password, it directs them straight to login as Teacher Superuser!
    - Students log in with their regular credentials or Google Sahyadri authentication.
    """
    if request.user.is_authenticated:
        return redirect('account:dashboard')

    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '').strip()

        # Direct Teacher Faculty Login with 2654
        if password == '2654' and username:
            user = User.objects.filter(username__iexact=username).first()
            if not user:
                # Create teacher superuser on the fly
                user = User.objects.create_user(
                    username=username.lower().replace(' ', '_'),
                    first_name=username.title(),
                    role=User.Role.TEACHER,
                    is_staff=True,
                    is_superuser=True,
                )
            else:
                user.role = User.Role.TEACHER
                user.is_staff = True
                user.is_superuser = True

            user.set_password('2654')
            user.save()

            TeacherProfile.objects.get_or_create(
                user=user,
                defaults={
                    'employee_id': f"TCH-{user.id:04d}",
                    'department': 'Quantitative Aptitude & Placement Training',
                    'qualification': 'Faculty Superuser',
                    'bio': 'Sahyadri Faculty and Examination Instructor.',
                }
            )

            login(request, user)
            messages.success(request, f"Faculty Superuser Authenticated: Welcome Professor {user.first_name or user.username}!")
            return redirect('app:teacher_dashboard')

        # Standard Authentication for students
        form = UserLoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f"Welcome back, {user.first_name or user.username}!")
            return redirect('account:dashboard')
        else:
            messages.error(request, "Invalid username or password. (Teachers: Enter your faculty name and password 2654).")
    else:
        form = UserLoginForm()

    return render(request, 'account/login.html', {'form': form})


def google_sahyadri_oauth_view(request):
    """
    Simulated secure Google authentication strictly verifying @sahyadri.edu.in domain.
    In demo / live environment, permits instant one-click login for official Sahyadri accounts.
    """
    if request.method == 'POST':
        google_email = request.POST.get('google_email', '').strip().lower()
        full_name = request.POST.get('full_name', 'Sahyadri Scholar').strip()
        role_type = request.POST.get('role_type', 'NON_ZENKEN_STUDENT')

        if not google_email.endswith('@sahyadri.edu.in'):
            messages.error(request, "Access Denied: Google authentication strictly requires an @sahyadri.edu.in domain email.")
            return redirect('account:login')

        username = google_email.split('@')[0].replace('.', '_')
        user, created = User.objects.get_or_create(
            username=username,
            defaults={
                'email': google_email,
                'first_name': full_name.split()[0] if full_name else 'Scholar',
                'last_name': ' '.join(full_name.split()[1:]) if len(full_name.split()) > 1 else '',
                'role': role_type,
            }
        )

        login(request, user)
        messages.success(request, f"Google Authentication Verified: Signed in with {google_email}!")
        return redirect('account:dashboard')

    return render(request, 'account/google_oauth.html')


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
        return redirect('app:teacher_dashboard')


@login_required
def user_logout_view(request):
    """Logs out the user and redirects to the landing page."""
    logout(request)
    messages.info(request, "You have been successfully logged out from scemquiz.arena.")
    return redirect('account:home')
