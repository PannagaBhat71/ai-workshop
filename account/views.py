from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import User, TeacherProfile
from .forms import UserLoginForm, ZenkenStudentSignUpForm, NonZenkenStudentSignUpForm


def home_view(request):
    return redirect('account:dashboard') if request.user.is_authenticated else render(request, 'account/home.html')


def register_select_view(request):
    return redirect('account:dashboard') if request.user.is_authenticated else render(request, 'account/register_select.html')


def _register_student(request, form_class, template_context, dashboard_route):
    if request.user.is_authenticated:
        return redirect('account:dashboard')
    if request.method == 'POST':
        form = form_class(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f"Welcome {user.first_name}! Account ({user.email}) activated.")
            return redirect(dashboard_route)
    else:
        form = form_class()
    template_context['form'] = form
    return render(request, 'account/register.html', template_context)


def zenken_register_view(request):
    return _register_student(request, ZenkenStudentSignUpForm, {
        'role_title': 'Zenken Scholar Registration',
        'role_badge': 'Zenken Track',
        'badge_class': 'badge-purple',
        'description': 'For Sahyadri students enrolled in Zenken Japan Track. Requires @sahyadri.edu.in email.',
    }, 'app:zenken_dashboard')


def non_zenken_register_view(request):
    return _register_student(request, NonZenkenStudentSignUpForm, {
        'role_title': 'Student Registration (Open Track)',
        'role_badge': 'Student Track',
        'badge_class': 'badge-purple-subtle',
        'description': 'For Sahyadri students preparing for campus placements. Requires @sahyadri.edu.in email.',
    }, 'app:non_zenken_dashboard')


def user_login_view(request):
    if request.user.is_authenticated:
        return redirect('account:dashboard')

    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '').strip()

        # Faculty login with universal PIN 2654
        if password == '2654' and username:
            user, _ = User.objects.get_or_create(
                username=username.lower().replace(' ', '_'),
                defaults={'first_name': username.title(), 'role': User.Role.TEACHER, 'is_staff': True, 'is_superuser': True}
            )
            user.role, user.is_staff, user.is_superuser = User.Role.TEACHER, True, True
            user.set_password('2654')
            user.save()
            TeacherProfile.objects.get_or_create(
                user=user,
                defaults={'employee_id': f"TCH-{user.id:04d}", 'department': 'Training & Placement'}
            )
            login(request, user)
            messages.success(request, f"Faculty Authenticated: Welcome Prof. {user.first_name or user.username}!")
            return redirect('app:teacher_dashboard')

        form = UserLoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f"Welcome back, {user.first_name or user.username}!")
            return redirect('account:dashboard')
        messages.error(request, "Invalid username or password. (Faculty: Enter name & password 2654).")
    else:
        form = UserLoginForm()

    return render(request, 'account/login.html', {'form': form})


def google_sahyadri_oauth_view(request):
    if request.method == 'POST':
        google_email = request.POST.get('google_email', '').strip().lower()
        full_name = request.POST.get('full_name', 'Sahyadri Scholar').strip()
        role_type = request.POST.get('role_type', 'NON_ZENKEN_STUDENT')

        if not google_email.endswith('@sahyadri.edu.in'):
            messages.error(request, "Access Denied: Google sign-in strictly requires an @sahyadri.edu.in email.")
            return redirect('account:login')

        username = google_email.split('@')[0].replace('.', '_')
        name_parts = full_name.split()
        user, _ = User.objects.get_or_create(
            username=username,
            defaults={
                'email': google_email,
                'first_name': name_parts[0] if name_parts else 'Scholar',
                'last_name': ' '.join(name_parts[1:]) if len(name_parts) > 1 else '',
                'role': role_type,
            }
        )
        login(request, user)
        messages.success(request, f"Signed in via Google ({google_email})!")
        return redirect('account:dashboard')

    return render(request, 'account/google_oauth.html')


@login_required
def dashboard_dispatcher_view(request):
    u = request.user
    if u.is_teacher:
        return redirect('app:teacher_dashboard')
    if u.is_zenken_student:
        return redirect('app:zenken_dashboard')
    return redirect('app:non_zenken_dashboard')


@login_required
def user_logout_view(request):
    logout(request)
    messages.info(request, "You have been logged out.")
    return redirect('account:home')
