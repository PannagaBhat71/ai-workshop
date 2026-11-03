from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from .models import AptitudeQuestion, AcademyUpdate
from .forms import AptitudeQuestionForm, AcademyUpdateForm
from account.decorators import teacher_required, zenken_student_required, student_required


# ==============================================================================
# DASHBOARDS
# ==============================================================================

@teacher_required
def teacher_dashboard(request):
    """Teacher portal dashboard: metrics, questions list, and updates list."""
    teacher_questions = AptitudeQuestion.objects.filter(teacher=request.user)
    teacher_updates = AcademyUpdate.objects.filter(teacher=request.user)

    context = {
        'questions_count': teacher_questions.count(),
        'updates_count': teacher_updates.count(),
        'recent_questions': teacher_questions[:6],
        'recent_updates': teacher_updates[:6],
    }
    return render(request, 'app/dashboards/teacher_dashboard.html', context)


@zenken_student_required
def zenken_dashboard(request):
    """Zenken Enrolled Student dashboard."""
    # Zenken students have access to both ALL and ZENKEN_ONLY updates & questions
    updates = AcademyUpdate.objects.filter(
        Q(target_audience='ALL') | Q(target_audience='ZENKEN_ONLY')
    )[:5]

    questions = AptitudeQuestion.objects.all()[:6]
    exclusive_count = AptitudeQuestion.objects.filter(access_tier='ZENKEN_ONLY').count()

    context = {
        'profile': getattr(request.user, 'zenken_profile', None),
        'updates': updates,
        'questions': questions,
        'total_questions_available': AptitudeQuestion.objects.count(),
        'exclusive_count': exclusive_count,
    }
    return render(request, 'app/dashboards/zenken_dashboard.html', context)


@login_required
def non_zenken_dashboard(request):
    """Non-Zenken Student dashboard."""
    # Non-Zenken students have access to ALL and NON_ZENKEN_ONLY updates, and ALL access questions
    updates = AcademyUpdate.objects.filter(
        Q(target_audience='ALL') | Q(target_audience='NON_ZENKEN_ONLY')
    )[:5]

    questions = AptitudeQuestion.objects.filter(access_tier='ALL')[:6]

    context = {
        'profile': getattr(request.user, 'non_zenken_profile', None),
        'updates': updates,
        'questions': questions,
        'total_questions_available': questions.count(),
    }
    return render(request, 'app/dashboards/non_zenken_dashboard.html', context)


# ==============================================================================
# TEACHER: APTITUDE QUESTIONS MANAGEMENT
# ==============================================================================

@teacher_required
def question_create_view(request):
    """Upload a new Quantitative Aptitude question."""
    if request.method == 'POST':
        form = AptitudeQuestionForm(request.POST)
        if form.is_valid():
            question = form.save(commit=False)
            question.teacher = request.user
            question.save()
            messages.success(request, f"Quantitative Aptitude Question '{question.title}' uploaded successfully!")
            return redirect('app:question_detail', pk=question.pk)
    else:
        form = AptitudeQuestionForm()

    return render(request, 'app/questions/question_form.html', {
        'form': form,
        'title': 'Upload New Aptitude Question',
        'btn_text': 'Publish Question',
    })


@teacher_required
def question_edit_view(request, pk):
    """Edit an existing aptitude question."""
    if request.user.is_superuser:
        question = get_object_or_404(AptitudeQuestion, pk=pk)
    else:
        question = get_object_or_404(AptitudeQuestion, pk=pk, teacher=request.user)

    if request.method == 'POST':
        form = AptitudeQuestionForm(request.POST, instance=question)
        if form.is_valid():
            form.save()
            messages.success(request, f"Question '{question.title}' updated successfully.")
            return redirect('app:question_detail', pk=question.pk)
    else:
        form = AptitudeQuestionForm(instance=question)

    return render(request, 'app/questions/question_form.html', {
        'form': form,
        'title': f"Edit Question: {question.title}",
        'btn_text': 'Update Question',
        'question': question,
    })


@teacher_required
def question_delete_view(request, pk):
    """Delete an aptitude question."""
    if request.user.is_superuser:
        question = get_object_or_404(AptitudeQuestion, pk=pk)
    else:
        question = get_object_or_404(AptitudeQuestion, pk=pk, teacher=request.user)

    if request.method == 'POST':
        title = question.title
        question.delete()
        messages.success(request, f"Question '{title}' has been deleted.")
        return redirect('app:teacher_dashboard')

    return render(request, 'app/questions/question_confirm_delete.html', {
        'question': question,
    })


# ==============================================================================
# TEACHER: ACADEMY UPDATES MANAGEMENT
# ==============================================================================

@teacher_required
def update_create_view(request):
    """Post an academy update or announcement."""
    if request.method == 'POST':
        form = AcademyUpdateForm(request.POST)
        if form.is_valid():
            update = form.save(commit=False)
            update.teacher = request.user
            update.save()
            messages.success(request, f"Academy Update '{update.title}' posted successfully!")
            return redirect('app:update_list')
    else:
        form = AcademyUpdateForm()

    return render(request, 'app/updates/update_form.html', {
        'form': form,
        'title': 'Post Academy Update / Announcement',
        'btn_text': 'Post Update',
    })


@teacher_required
def update_edit_view(request, pk):
    """Edit an existing academy update."""
    if request.user.is_superuser:
        update = get_object_or_404(AcademyUpdate, pk=pk)
    else:
        update = get_object_or_404(AcademyUpdate, pk=pk, teacher=request.user)

    if request.method == 'POST':
        form = AcademyUpdateForm(request.POST, instance=update)
        if form.is_valid():
            form.save()
            messages.success(request, f"Update '{update.title}' modified successfully.")
            return redirect('app:update_list')
    else:
        form = AcademyUpdateForm(instance=update)

    return render(request, 'app/updates/update_form.html', {
        'form': form,
        'title': f"Edit Update: {update.title}",
        'btn_text': 'Save Changes',
        'update': update,
    })


@teacher_required
def update_delete_view(request, pk):
    """Delete an academy update."""
    if request.user.is_superuser:
        update = get_object_or_404(AcademyUpdate, pk=pk)
    else:
        update = get_object_or_404(AcademyUpdate, pk=pk, teacher=request.user)

    if request.method == 'POST':
        title = update.title
        update.delete()
        messages.success(request, f"Update '{title}' was removed.")
        return redirect('app:update_list')

    return render(request, 'app/updates/update_confirm_delete.html', {
        'update': update,
    })


# ==============================================================================
# QUESTIONS: LIST & INTERACTIVE PRACTICE VIEW
# ==============================================================================

@login_required
def question_list_view(request):
    """Browse questions with permission checks and filters."""
    user = request.user
    if user.is_teacher or user.is_zenken_student:
        queryset = AptitudeQuestion.objects.all()
    else:
        queryset = AptitudeQuestion.objects.filter(access_tier='ALL')

    # Topic filter
    topic = request.GET.get('topic')
    if topic:
        queryset = queryset.filter(topic=topic)

    # Difficulty filter
    difficulty = request.GET.get('difficulty')
    if difficulty:
        queryset = queryset.filter(difficulty=difficulty)

    # Search keyword
    query = request.GET.get('q')
    if query:
        queryset = queryset.filter(
            Q(title__icontains=query) |
            Q(question_text__icontains=query) |
            Q(explanation__icontains=query)
        )

    context = {
        'questions': queryset,
        'topics': AptitudeQuestion.TOPIC_CHOICES,
        'difficulties': AptitudeQuestion.DIFFICULTY_CHOICES,
        'selected_topic': topic or '',
        'selected_difficulty': difficulty or '',
        'search_query': query or '',
    }
    return render(request, 'app/questions/question_list.html', context)


@login_required
def question_detail_view(request, pk):
    """Interactive practice mode: select an option, evaluate answer, view solution."""
    question = get_object_or_404(AptitudeQuestion, pk=pk)

    # Permission check for Non-Zenken students
    if question.access_tier == 'ZENKEN_ONLY' and request.user.is_non_zenken_student and not request.user.is_teacher:
        messages.error(request, "This aptitude question is exclusive to Zenken Enrolled Students.")
        return redirect('app:question_list')

    user_choice = None
    is_correct = None
    revealed = False

    if request.method == 'POST':
        user_choice = request.POST.get('chosen_option')
        revealed = True
        if user_choice:
            is_correct = (user_choice == question.correct_option)
            if is_correct:
                messages.success(request, f"Correct! Option {question.correct_option} is the right answer.")
            else:
                messages.warning(request, f"Incorrect. You selected Option {user_choice}. Correct answer is Option {question.correct_option}.")

    context = {
        'question': question,
        'user_choice': user_choice,
        'is_correct': is_correct,
        'revealed': revealed,
    }
    return render(request, 'app/questions/question_detail.html', context)


# ==============================================================================
# ACADEMY UPDATES: LIST VIEW
# ==============================================================================

@login_required
def update_list_view(request):
    """View academy announcements filtered according to user role."""
    user = request.user
    if user.is_teacher:
        updates = AcademyUpdate.objects.all()
    elif user.is_zenken_student:
        updates = AcademyUpdate.objects.filter(
            Q(target_audience='ALL') | Q(target_audience='ZENKEN_ONLY')
        )
    else:
        updates = AcademyUpdate.objects.filter(
            Q(target_audience='ALL') | Q(target_audience='NON_ZENKEN_ONLY')
        )

    return render(request, 'app/updates/update_list.html', {
        'updates': updates,
    })
