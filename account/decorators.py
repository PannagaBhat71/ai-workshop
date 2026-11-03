from functools import wraps
from django.contrib import messages
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required


def role_required(allowed_roles):
    """
    Decorator to restrict view access to specific user roles.
    allowed_roles: list of role strings (e.g. ['TEACHER', 'ZENKEN_STUDENT'])
    """
    def decorator(view_func):
        @wraps(view_func)
        @login_required
        def _wrapped_view(request, *args, **kwargs):
            if request.user.is_superuser or request.user.role in allowed_roles:
                return view_func(request, *args, **kwargs)
            messages.error(request, "Access denied: Your account does not have permission to view this page.")
            return redirect('account:dashboard')
        return _wrapped_view
    return decorator


def teacher_required(view_func):
    """Restricts access to Teachers and Superusers."""
    return role_required(['TEACHER'])(view_func)


def zenken_student_required(view_func):
    """Restricts access to Zenken enrolled students."""
    return role_required(['ZENKEN_STUDENT'])(view_func)


def student_required(view_func):
    """Allows either Zenken or Non-Zenken students (as well as teachers/admins)."""
    return role_required(['ZENKEN_STUDENT', 'NON_ZENKEN_STUDENT'])(view_func)

