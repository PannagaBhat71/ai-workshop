from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Avg, Count, Sum
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.utils import timezone
import json
import re
import random

from .models import (
    AptitudeQuestion,
    AcademyUpdate,
    Quiz,
    QuizAttempt,
    QuestionPracticeLog,
    UserActivityStreak,
    WeeklyNewsletter,
    Opportunity,
    StudyMaterial,
)
from .forms import (
    AptitudeQuestionForm,
    AcademyUpdateForm,
    QuizForm,
    WeeklyNewsletterForm,
    OpportunityForm,
    StudyMaterialForm,
)
from account.decorators import teacher_required, zenken_student_required, student_required


def get_or_create_streak(user):
    """Helper to get or create streak record for student."""
    streak, _ = UserActivityStreak.objects.get_or_create(student=user)
    return streak


# ==============================================================================
# LEADERBOARD & STREAK BOARD
# ==============================================================================

@login_required
def leaderboard_view(request):
    """
    Leaderboard tracking users, activity, points, and consecutive practice streaks.
    """
    cohort_filter = request.GET.get('cohort', 'all')
    sort_by = request.GET.get('sort', 'points')

    # Query all streaks for students
    streaks = UserActivityStreak.objects.select_related('student').filter(
        student__role__in=['ZENKEN_STUDENT', 'NON_ZENKEN_STUDENT']
    )

    if cohort_filter == 'zenken':
        streaks = streaks.filter(student__role='ZENKEN_STUDENT')
    elif cohort_filter == 'non_zenken':
        streaks = streaks.filter(student__role='NON_ZENKEN_STUDENT')

    if sort_by == 'streak':
        streaks = streaks.order_by('-current_streak', '-total_points')
    else:
        streaks = streaks.order_by('-total_points', '-current_streak')

    my_streak = None
    if not request.user.is_teacher:
        my_streak = get_or_create_streak(request.user)

    top_streak_leader = UserActivityStreak.objects.order_by('-current_streak').first()
    top_points_leader = UserActivityStreak.objects.order_by('-total_points').first()

    context = {
        'streaks': streaks[:50],
        'my_streak': my_streak,
        'cohort_filter': cohort_filter,
        'sort_by': sort_by,
        'top_streak_leader': top_streak_leader,
        'top_points_leader': top_points_leader,
    }
    return render(request, 'app/leaderboard/leaderboard.html', context)


# ==============================================================================
# TOPIC-WISE PRACTICE ROOM
# ==============================================================================

@login_required
def topic_practice_rooms_view(request):
    """
    Topic-Wise Practice Room covering all resource topics:
    Percentages, Work, Speed, Ratio, Numbers, Algebra, Geometry, Modern Math,
    Data Interpretation, and Japanese sets (Zenken Exclusive).
    """
    user = request.user
    topics_list = [
        {'code': 'PERCENTAGE', 'name': 'Percentages & Fractions', 'icon': 'bi-percent', 'desc': 'Successive discounts, salary hikes, population change.'},
        {'code': 'PROFIT_LOSS', 'name': 'Profit, Loss & Discount', 'icon': 'bi-tag-fill', 'desc': 'Cost price, marked price, trade discounts, margin.'},
        {'code': 'TIME_WORK', 'name': 'Time & Work / Pipes & Cisterns', 'icon': 'bi-hourglass-split', 'desc': 'Work efficiency, alternate day work, inlet/outlet pipes.'},
        {'code': 'SPEED_DISTANCE', 'name': 'Speed, Distance & Trains', 'icon': 'bi-speedometer2', 'desc': 'Relative speed, train crossing platforms, boats & streams.'},
        {'code': 'RATIO_PROPORTION', 'name': 'Ratio, Proportion & Mixtures', 'icon': 'bi-pie-chart-fill', 'desc': 'Partnership ratios, allegating liquids, age problems.'},
        {'code': 'AVERAGES', 'name': 'Averages & Allegations', 'icon': 'bi-bar-chart-steps', 'desc': 'Weighted averages, replacement problems, speed averages.'},
        {'code': 'NUMBER_SYSTEM', 'name': 'Number System & Numeracy', 'icon': 'bi-123', 'desc': 'Divisibility rules, HCF & LCM, remainder theorem.'},
        {'code': 'ALGEBRA', 'name': 'Algebra & Equations', 'icon': 'bi-calculator-fill', 'desc': 'Linear, quadratic equations, inequalities, logarithms.'},
        {'code': 'GEOMETRY', 'name': 'Geometry & Mensuration', 'icon': 'bi-bounding-box-circles', 'desc': 'Circles, regular polygons, triangles, surface areas.'},
        {'code': 'MODERN_MATH', 'name': 'Modern Math & Probability', 'icon': 'bi-dice-5-fill', 'desc': 'Permutations, combinations, probability distributions.'},
        {'code': 'DATA_INTERPRETATION', 'name': 'Data Interpretation', 'icon': 'bi-graph-up-arrow', 'desc': 'Tables, bar graphs, pie charts, line plots.'},
        {'code': 'LOGICAL_REASONING', 'name': 'Logical Reasoning & Analytics', 'icon': 'bi-diagram-3-fill', 'desc': 'Series completion, syllogisms, analytical puzzles.'},
    ]

    japanese_topics = [
        {'code': 'JP_KANJI', 'name': 'Kanji & Readings (漢字)', 'icon': 'bi-translate', 'desc': 'Onyomi, Kunyomi, JLPT N5/N4/N3 character compounds.'},
        {'code': 'JP_GRAMMAR', 'name': 'JLPT Grammar (文法)', 'icon': 'bi-book-fill', 'desc': 'Particles, passive/causative, honorific keigo forms.'},
        {'code': 'JP_VOCAB', 'name': 'Vocabulary & Meanings (語彙)', 'icon': 'bi-chat-left-text-fill', 'desc': 'IT engineering terminology, everyday vocabulary.'},
        {'code': 'JP_CULTURE', 'name': 'Business Etiquette (ビジネスマナー)', 'icon': 'bi-briefcase-fill', 'desc': 'Japanese corporate communications and email manners.'},
    ]

    # Annotate counts
    for t in topics_list:
        t['count'] = AptitudeQuestion.objects.filter(topic=t['code']).count()

    is_zenken = user.is_zenken_student or user.is_teacher
    if is_zenken:
        for jt in japanese_topics:
            jt['count'] = AptitudeQuestion.objects.filter(topic=jt['code']).count()

    context = {
        'aptitude_topics': topics_list,
        'japanese_topics': japanese_topics,
        'is_zenken': is_zenken,
    }
    return render(request, 'app/practice/topic_rooms.html', context)


@login_required
def topic_room_practice_view(request, topic_code):
    """Practice questions strictly inside a selected topic room."""
    user = request.user
    is_japanese = topic_code.startswith('JP_')

    if is_japanese and not (user.is_zenken_student or user.is_teacher):
        messages.error(request, "Japanese Language Topic Rooms are exclusive to Zenken Enrolled Students.")
        return redirect('app:topic_practice_rooms')

    questions = AptitudeQuestion.objects.filter(topic=topic_code)
    topic_display = dict(AptitudeQuestion.TOPIC_CHOICES).get(topic_code, topic_code)

    return render(request, 'app/practice/topic_room_detail.html', {
        'topic_code': topic_code,
        'topic_display': topic_display,
        'questions': questions,
    })


# ==============================================================================
# DASHBOARDS & STUDENT ACTIVITY REVIEW
# ==============================================================================

@teacher_required
def teacher_dashboard(request):
    """Teacher portal dashboard: metrics, questions list, scheduled quizzes, updates, and student activity."""
    teacher_questions = AptitudeQuestion.objects.filter(teacher=request.user)
    teacher_updates = AcademyUpdate.objects.filter(teacher=request.user)
    teacher_quizzes = Quiz.objects.filter(teacher=request.user)
    recent_attempts = QuizAttempt.objects.select_related('student', 'quiz').all()[:8]

    context = {
        'questions_count': teacher_questions.count(),
        'updates_count': teacher_updates.count(),
        'quizzes_count': teacher_quizzes.count(),
        'total_attempts': QuizAttempt.objects.count(),
        'recent_questions': teacher_questions[:6],
        'recent_updates': teacher_updates[:5],
        'recent_quizzes': teacher_quizzes[:5],
        'recent_attempts': recent_attempts,
    }
    return render(request, 'app/dashboards/teacher_dashboard.html', context)


@teacher_required
def student_activities_view(request):
    """Teacher can review student activities, quiz submissions, performance, and practice logs."""
    attempts = QuizAttempt.objects.select_related('student', 'quiz').all()
    practice_logs = QuestionPracticeLog.objects.select_related('student', 'question').all()[:20]

    quiz_id = request.GET.get('quiz')
    student_query = request.GET.get('student')
    role_filter = request.GET.get('role')

    if quiz_id:
        attempts = attempts.filter(quiz_id=quiz_id)
    if student_query:
        attempts = attempts.filter(
            Q(student__username__icontains=student_query) |
            Q(student__first_name__icontains=student_query) |
            Q(student__last_name__icontains=student_query)
        )
    if role_filter:
        attempts = attempts.filter(student__role=role_filter)

    quizzes = Quiz.objects.all()

    avg_score = attempts.aggregate(Avg('percentage'))['percentage__avg'] or 0
    passed_count = attempts.filter(passed=True).count()
    total_attempts_count = attempts.count()
    pass_rate = (passed_count / total_attempts_count * 100) if total_attempts_count > 0 else 0

    context = {
        'attempts': attempts,
        'practice_logs': practice_logs,
        'quizzes': quizzes,
        'selected_quiz': quiz_id or '',
        'student_query': student_query or '',
        'selected_role': role_filter or '',
        'avg_score': round(avg_score, 1),
        'pass_rate': round(pass_rate, 1),
        'total_attempts_count': total_attempts_count,
    }
    return render(request, 'app/teacher/student_activities.html', context)


@teacher_required
def student_attempt_detail_view(request, pk):
    """Detailed review of a single student's quiz attempt."""
    attempt = get_object_or_404(QuizAttempt.objects.select_related('student', 'quiz'), pk=pk)
    return render(request, 'app/teacher/student_attempt_detail.html', {'attempt': attempt})


@zenken_student_required
def zenken_dashboard(request):
    """Zenken Enrolled Student dashboard (Japanese + Aptitude)."""
    updates = AcademyUpdate.objects.filter(
        Q(target_audience='ALL') | Q(target_audience='ZENKEN_ONLY')
    )[:5]

    aptitude_questions = AptitudeQuestion.objects.filter(subject='APTITUDE')[:4]
    japanese_questions = AptitudeQuestion.objects.filter(subject='JAPANESE')[:4]

    quizzes = Quiz.objects.filter(
        is_published=True
    ).filter(
        Q(target_audience='ALL') | Q(target_audience='ZENKEN_ONLY')
    )[:4]

    my_attempts = QuizAttempt.objects.filter(student=request.user)[:5]
    streak = get_or_create_streak(request.user)

    # Check live active quizzes for notification
    live_quizzes = Quiz.objects.filter(is_published=True).filter(
        Q(target_audience='ALL') | Q(target_audience='ZENKEN_ONLY')
    )
    active_tests = [q for q in live_quizzes if q.is_live]

    context = {
        'profile': getattr(request.user, 'zenken_profile', None),
        'updates': updates,
        'aptitude_questions': aptitude_questions,
        'japanese_questions': japanese_questions,
        'quizzes': quizzes,
        'my_attempts': my_attempts,
        'streak': streak,
        'active_tests': active_tests,
        'total_japanese_questions': AptitudeQuestion.objects.filter(subject='JAPANESE').count(),
        'total_aptitude_questions': AptitudeQuestion.objects.filter(subject='APTITUDE').count(),
    }
    return render(request, 'app/dashboards/zenken_dashboard.html', context)


@login_required
def non_zenken_dashboard(request):
    """Non-Zenken Student dashboard (Only Aptitude - Japanese is restricted)."""
    updates = AcademyUpdate.objects.filter(
        Q(target_audience='ALL') | Q(target_audience='NON_ZENKEN_ONLY')
    )[:5]

    questions = AptitudeQuestion.objects.filter(subject='APTITUDE', access_tier='ALL')[:6]

    quizzes = Quiz.objects.filter(
        is_published=True,
        quiz_type='APTITUDE'
    ).filter(
        Q(target_audience='ALL') | Q(target_audience='NON_ZENKEN_ONLY')
    )[:4]

    my_attempts = QuizAttempt.objects.filter(student=request.user)[:5]
    streak = get_or_create_streak(request.user)

    live_quizzes = Quiz.objects.filter(is_published=True, quiz_type='APTITUDE').filter(
        Q(target_audience='ALL') | Q(target_audience='NON_ZENKEN_ONLY')
    )
    active_tests = [q for q in live_quizzes if q.is_live]

    context = {
        'profile': getattr(request.user, 'non_zenken_profile', None),
        'updates': updates,
        'questions': questions,
        'quizzes': quizzes,
        'my_attempts': my_attempts,
        'streak': streak,
        'active_tests': active_tests,
    }
    return render(request, 'app/dashboards/non_zenken_dashboard.html', context)


# ==============================================================================
# PRACTICE ARENA
# ==============================================================================

@login_required
def practice_arena_view(request):
    """Practice Arena with sets."""
    user = request.user
    selected_set = request.GET.get('set', 'all')
    difficulty = request.GET.get('difficulty')
    search_q = request.GET.get('q')

    if user.is_teacher or user.is_zenken_student:
        queryset = AptitudeQuestion.objects.all()
    else:
        queryset = AptitudeQuestion.objects.filter(subject='APTITUDE', access_tier='ALL')

    if selected_set == 'japanese':
        if not (user.is_teacher or user.is_zenken_student):
            messages.error(request, "Japanese Language Practice Sets are exclusive to Zenken Enrolled Students.")
            return redirect('app:practice_arena')
        queryset = queryset.filter(subject='JAPANESE')
    elif selected_set == 'aptitude':
        queryset = queryset.filter(subject='APTITUDE')
    elif selected_set == 'reasoning':
        queryset = queryset.filter(topic='LOGICAL_REASONING')
    elif selected_set == 'kanji':
        queryset = queryset.filter(topic='JP_KANJI')
    elif selected_set == 'grammar':
        queryset = queryset.filter(topic='JP_GRAMMAR')
    elif selected_set == 'work_time':
        queryset = queryset.filter(topic='TIME_WORK')
    elif selected_set == 'speed_distance':
        queryset = queryset.filter(topic='SPEED_DISTANCE')

    if difficulty:
        queryset = queryset.filter(difficulty=difficulty)
    if search_q:
        queryset = queryset.filter(
            Q(title__icontains=search_q) |
            Q(question_text__icontains=search_q) |
            Q(explanation__icontains=search_q)
        )

    counts = {
        'all': queryset.count(),
        'aptitude': AptitudeQuestion.objects.filter(subject='APTITUDE').count(),
        'japanese': AptitudeQuestion.objects.filter(subject='JAPANESE').count() if (user.is_teacher or user.is_zenken_student) else 0,
        'reasoning': AptitudeQuestion.objects.filter(topic='LOGICAL_REASONING').count(),
    }

    context = {
        'questions': queryset,
        'selected_set': selected_set,
        'selected_difficulty': difficulty or '',
        'search_query': search_q or '',
        'counts': counts,
        'is_zenken_or_teacher': user.is_teacher or user.is_zenken_student,
    }
    return render(request, 'app/practice/practice_arena.html', context)


# ==============================================================================
# STRICT 20-QUESTION QUIZZES & ANTI-CHEAT TAB SWITCH RESTRICTION
# ==============================================================================

@teacher_required
def quiz_create_view(request):
    """Teacher schedules & posts new Quizzes."""
    if request.method == 'POST':
        form = QuizForm(request.POST)
        if form.is_valid():
            quiz = form.save(commit=False)
            quiz.teacher = request.user
            quiz.save()
            form.save_m2m()
            messages.success(request, f"Quiz '{quiz.title}' scheduled and published successfully!")
            return redirect('app:quiz_detail', pk=quiz.pk)
    else:
        form = QuizForm()

    return render(request, 'app/quizzes/quiz_form.html', {
        'form': form,
        'title': 'Schedule & Post New Quiz',
        'btn_text': 'Publish Quiz',
    })


@teacher_required
def quiz_edit_view(request, pk):
    quiz = get_object_or_404(Quiz, pk=pk)
    if not request.user.is_superuser and quiz.teacher != request.user:
        messages.error(request, "Permission denied.")
        return redirect('app:quiz_list')

    if request.method == 'POST':
        form = QuizForm(request.POST, instance=quiz)
        if form.is_valid():
            form.save()
            messages.success(request, f"Quiz '{quiz.title}' updated successfully.")
            return redirect('app:quiz_detail', pk=quiz.pk)
    else:
        form = QuizForm(instance=quiz)

    return render(request, 'app/quizzes/quiz_form.html', {
        'form': form,
        'title': f"Edit Quiz: {quiz.title}",
        'btn_text': 'Save Changes',
        'quiz': quiz,
    })


@teacher_required
def quiz_delete_view(request, pk):
    quiz = get_object_or_404(Quiz, pk=pk)
    if not request.user.is_superuser and quiz.teacher != request.user:
        messages.error(request, "Permission denied.")
        return redirect('app:quiz_list')

    if request.method == 'POST':
        title = quiz.title
        quiz.delete()
        messages.success(request, f"Quiz '{title}' has been deleted.")
        return redirect('app:quiz_list')

    return render(request, 'app/quizzes/quiz_confirm_delete.html', {'quiz': quiz})


@login_required
def quiz_list_view(request):
    """Browse live and scheduled quizzes."""
    user = request.user
    if user.is_teacher:
        quizzes = Quiz.objects.all()
    elif user.is_zenken_student:
        quizzes = Quiz.objects.filter(is_published=True).filter(
            Q(target_audience='ALL') | Q(target_audience='ZENKEN_ONLY')
        )
    else:
        quizzes = Quiz.objects.filter(is_published=True, quiz_type='APTITUDE').filter(
            Q(target_audience='ALL') | Q(target_audience='NON_ZENKEN_ONLY')
        )

    return render(request, 'app/quizzes/quiz_list.html', {'quizzes': quizzes})


@login_required
def quiz_detail_view(request, pk):
    quiz = get_object_or_404(Quiz, pk=pk)
    user = request.user

    if quiz.quiz_type == 'JAPANESE' and not (user.is_teacher or user.is_zenken_student):
        messages.error(request, "Japanese Language Quizzes are exclusive to Zenken Enrolled Students.")
        return redirect('app:quiz_list')

    attempts = QuizAttempt.objects.filter(quiz=quiz, student=user) if not user.is_teacher else QuizAttempt.objects.filter(quiz=quiz)
    return render(request, 'app/quizzes/quiz_detail.html', {
        'quiz': quiz,
        'attempts': attempts,
        'questions_count': 20,  # Strictly 20 questions
    })


@login_required
def quiz_take_view(request, pk):
    """
    STRICT 20-QUESTION QUIZ TAKING WITH LIVE TIMER AND TAB RESTRICTION ANTI-CHEAT.
    """
    quiz = get_object_or_404(Quiz, pk=pk)
    user = request.user

    if quiz.quiz_type == 'JAPANESE' and not (user.is_teacher or user.is_zenken_student):
        messages.error(request, "Access restricted to Zenken Enrolled Students.")
        return redirect('app:quiz_list')

    # Gather strictly 20 questions
    attached_questions = list(quiz.questions.all())
    if len(attached_questions) < 20:
        # Supplement from pool
        supplement_query = AptitudeQuestion.objects.filter(subject=quiz.quiz_type)
        if quiz.quiz_type == 'APTITUDE' and user.is_non_zenken_student:
            supplement_query = supplement_query.filter(access_tier='ALL')
        supplement = list(supplement_query.exclude(id__in=[q.id for q in attached_questions]))
        random.shuffle(supplement)
        needed = 20 - len(attached_questions)
        questions = attached_questions + supplement[:needed]
    else:
        questions = attached_questions[:20]

    if not questions:
        messages.warning(request, "No questions are currently available for this quiz.")
        return redirect('app:quiz_detail', pk=quiz.pk)

    if request.method == 'POST':
        score = 0
        total = 20  # Strictly 20 questions in quiz assessment
        answers_data = {}

        for q in questions:
            chosen = request.POST.get(f'q_{q.pk}')
            is_correct = (chosen == q.correct_option)
            if is_correct:
                score += 1
            answers_data[str(q.pk)] = {
                'title': q.title,
                'chosen': chosen or 'Skipped',
                'correct': q.correct_option,
                'is_correct': is_correct,
                'explanation': q.explanation,
            }

        percentage = (score / total) * 100
        passed = percentage >= quiz.pass_percentage
        time_taken = int(request.POST.get('time_taken', 0))
        tab_violations = int(request.POST.get('tab_switch_violations', 0))

        attempt = QuizAttempt.objects.create(
            student=user,
            quiz=quiz,
            score=score,
            total_questions=total,
            percentage=round(percentage, 1),
            passed=passed,
            time_taken_seconds=time_taken,
            tab_switch_violations=tab_violations,
            answers_data=answers_data,
        )

        # Update streak & points
        streak = get_or_create_streak(user)
        pts = (50 if passed else 25) + (score * 5)
        streak.record_activity(points=pts, is_quiz=True)

        messages.success(request, f"Quiz submitted! Score: {score}/{total} ({percentage:.1f}%). Activity points added!")
        return redirect('app:quiz_attempt_result', pk=attempt.pk)

    return render(request, 'app/quizzes/quiz_take.html', {
        'quiz': quiz,
        'questions': questions,
    })


@login_required
def quiz_attempt_result_view(request, pk):
    attempt = get_object_or_404(QuizAttempt, pk=pk)
    if attempt.student != request.user and not request.user.is_teacher:
        messages.error(request, "Permission denied.")
        return redirect('app:quiz_list')

    return render(request, 'app/quizzes/quiz_result.html', {'attempt': attempt})


# ==============================================================================
# WEEKLY NEWSLETTER: PLACEMENT PREP & JOB MARKET DEMANDS
# ==============================================================================

@login_required
def newsletter_list_view(request):
    newsletters = WeeklyNewsletter.objects.all()
    return render(request, 'app/newsletter/newsletter_list.html', {'newsletters': newsletters})


@login_required
def newsletter_detail_view(request, pk):
    newsletter = get_object_or_404(WeeklyNewsletter, pk=pk)
    return render(request, 'app/newsletter/newsletter_detail.html', {'newsletter': newsletter})


@teacher_required
def newsletter_create_view(request):
    if request.method == 'POST':
        form = WeeklyNewsletterForm(request.POST)
        if form.is_valid():
            newsletter = form.save(commit=False)
            newsletter.author = request.user
            newsletter.save()
            messages.success(request, f"Weekly Newsletter #{newsletter.issue_number} published successfully!")
            return redirect('app:newsletter_detail', pk=newsletter.pk)
    else:
        last_issue = WeeklyNewsletter.objects.order_by('-issue_number').first()
        next_num = (last_issue.issue_number + 1) if last_issue else 1
        form = WeeklyNewsletterForm(initial={'issue_number': next_num})

    return render(request, 'app/newsletter/newsletter_form.html', {'form': form})


# ==============================================================================
# OPPORTUNITIES (JOBS, INTERNSHIPS & PLACEMENT LINKS)
# ==============================================================================

@login_required
def opportunity_list_view(request):
    opps = Opportunity.objects.all()
    user = request.user
    if user.is_non_zenken_student:
        opps = opps.exclude(opportunity_type='JAPAN_DRIVE')

    return render(request, 'app/opportunities/opportunity_list.html', {
        'opportunities': opps,
        'is_zenken': user.is_zenken_student or user.is_teacher,
    })


@teacher_required
def opportunity_create_view(request):
    if request.method == 'POST':
        form = OpportunityForm(request.POST)
        if form.is_valid():
            opp = form.save(commit=False)
            opp.posted_by = request.user
            opp.save()
            messages.success(request, f"Opportunity for '{opp.company_name}' posted successfully!")
            return redirect('app:opportunity_list')
    else:
        form = OpportunityForm()

    return render(request, 'app/opportunities/opportunity_form.html', {'form': form})


# ==============================================================================
# TEACHER STUDY MATERIAL & DOCUMENT UPLOAD
# ==============================================================================

@login_required
def material_list_view(request):
    materials = StudyMaterial.objects.all()
    user = request.user
    if user.is_non_zenken_student:
        materials = materials.filter(Q(target_audience='ALL') | Q(target_audience='NON_ZENKEN_ONLY'))

    return render(request, 'app/materials/material_list.html', {'materials': materials})


@teacher_required
def material_upload_view(request):
    if request.method == 'POST':
        form = StudyMaterialForm(request.POST, request.FILES)
        if form.is_valid():
            mat = form.save(commit=False)
            mat.uploaded_by = request.user
            mat.save()
            messages.success(request, f"Study material '{mat.title}' uploaded successfully!")
            return redirect('app:material_list')
    else:
        form = StudyMaterialForm()

    return render(request, 'app/materials/material_form.html', {'form': form})


# ==============================================================================
# VOICE DICTATION & AUTO-GENERATION API
# ==============================================================================

@require_POST
@teacher_required
def auto_generate_options_api(request):
    """Smart Speech & Math Parser API."""
    try:
        data = json.loads(request.body)
        raw_text = data.get('text', '').strip()

        if not raw_text:
            return JsonResponse({'error': 'No text provided'}, status=400)

        pattern = r'(?i)(?:question:?\s*)?(.*?)(?:option\s*a:?\s*)(.*?)(?:option\s*b:?\s*)(.*?)(?:option\s*c:?\s*)(.*?)(?:option\s*d:?\s*)(.*?)(?:(?:answer|correct(?:\s*option)?):?\s*([a-d]))?(?:(?:explanation|solution):?\s*(.*))?$'
        match = re.search(pattern, raw_text, re.DOTALL)

        if match and match.group(2) and match.group(3):
            q_text = match.group(1).strip()
            return JsonResponse({
                'title': q_text[:60] + ('...' if len(q_text) > 60 else ''),
                'question_text': q_text,
                'option_a': match.group(2).strip(),
                'option_b': match.group(3).strip(),
                'option_c': match.group(4).strip(),
                'option_d': match.group(5).strip(),
                'correct_option': (match.group(6) or 'A').upper(),
                'explanation': (match.group(7) or 'Derived from problem statement.').strip(),
                'subject': 'APTITUDE',
            })

        q_text = raw_text
        subject = 'APTITUDE'
        topic = 'PERCENTAGE'
        opt_a, opt_b, opt_c, opt_d = '10', '20', '30', '40'
        correct = 'B'
        expl = 'Step-by-step mathematical calculation applied.'

        if any('\u3040' <= char <= '\u30ff' or '\u4e00' <= char <= '\u9fff' for char in q_text) or 'japanese' in q_text.lower() or 'kanji' in q_text.lower():
            subject = 'JAPANESE'
            topic = 'JP_KANJI'
            opt_a = 'Sensei (Teacher)'
            opt_b = 'Gakusei (Student)'
            opt_c = 'Kaishain (Company Employee)'
            opt_d = 'Isha (Doctor)'
            correct = 'A'
            expl = 'Standard Japanese vocabulary and JLPT N5/N4 reading.'
        elif '%' in q_text or 'percent' in q_text.lower():
            topic = 'PERCENTAGE'
            opt_a = '15%'
            opt_b = '20%'
            opt_c = '25%'
            opt_d = '30%'
            correct = 'B'
            expl = 'Calculated using percentage formula: (Part / Whole) * 100.'
        elif 'speed' in q_text.lower() or 'km' in q_text.lower() or 'train' in q_text.lower():
            topic = 'SPEED_DISTANCE'
            opt_a = '45 km/h'
            opt_b = '60 km/h'
            opt_c = '72 km/h'
            opt_d = '90 km/h'
            correct = 'C'
            expl = 'Speed = Distance / Time. Converted to km/h with 18/5 multiplier.'
        elif 'work' in q_text.lower() or 'days' in q_text.lower():
            topic = 'TIME_WORK'
            opt_a = '6 days'
            opt_b = '8 days'
            opt_c = '10 days'
            opt_d = '12 days'
            correct = 'A'
            expl = 'Combined work rate = 1/A + 1/B. Inverted for total days.'
        else:
            opt_a = 'Option 1'
            opt_b = 'Option 2 (Correct Answer)'
            opt_c = 'Option 3'
            opt_d = 'Option 4'
            correct = 'B'
            expl = 'Verified solution according to standard problem-solving logic.'

        title = q_text[:50].strip() + ('...' if len(q_text) > 50 else '')

        return JsonResponse({
            'title': title,
            'question_text': q_text,
            'subject': subject,
            'topic': topic,
            'option_a': opt_a,
            'option_b': opt_b,
            'option_c': opt_c,
            'option_d': opt_d,
            'correct_option': correct,
            'explanation': expl,
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


# ==============================================================================
# QUESTIONS CRUD & PRACTICE
# ==============================================================================

@teacher_required
def question_create_view(request):
    if request.method == 'POST':
        form = AptitudeQuestionForm(request.POST)
        if form.is_valid():
            q = form.save(commit=False)
            q.teacher = request.user
            q.save()
            messages.success(request, f"Question '{q.title}' uploaded successfully!")
            return redirect('app:question_detail', pk=q.pk)
    else:
        form = AptitudeQuestionForm()

    return render(request, 'app/questions/question_form.html', {
        'form': form,
        'title': 'Upload New Question (Voice Dictation Available)',
        'btn_text': 'Publish Question',
    })


@teacher_required
def question_edit_view(request, pk):
    q = get_object_or_404(AptitudeQuestion, pk=pk)
    if not request.user.is_superuser and q.teacher != request.user:
        messages.error(request, "Permission denied.")
        return redirect('app:question_list')

    if request.method == 'POST':
        form = AptitudeQuestionForm(request.POST, instance=q)
        if form.is_valid():
            form.save()
            messages.success(request, f"Question '{q.title}' updated successfully.")
            return redirect('app:question_detail', pk=q.pk)
    else:
        form = AptitudeQuestionForm(instance=q)

    return render(request, 'app/questions/question_form.html', {
        'form': form,
        'title': f"Edit Question: {q.title}",
        'btn_text': 'Save Question',
        'question': q,
    })


@teacher_required
def question_delete_view(request, pk):
    q = get_object_or_404(AptitudeQuestion, pk=pk)
    if not request.user.is_superuser and q.teacher != request.user:
        messages.error(request, "Permission denied.")
        return redirect('app:question_list')

    if request.method == 'POST':
        title = q.title
        q.delete()
        messages.success(request, f"Question '{title}' deleted.")
        return redirect('app:question_list')

    return render(request, 'app/questions/question_confirm_delete.html', {'question': q})


@login_required
def question_list_view(request):
    user = request.user
    if user.is_teacher or user.is_zenken_student:
        queryset = AptitudeQuestion.objects.all()
    else:
        queryset = AptitudeQuestion.objects.filter(subject='APTITUDE', access_tier='ALL')

    subject = request.GET.get('subject')
    if subject:
        if subject == 'JAPANESE' and not (user.is_teacher or user.is_zenken_student):
            messages.error(request, "Japanese questions are exclusive to Zenken Enrolled Students.")
        else:
            queryset = queryset.filter(subject=subject)

    topic = request.GET.get('topic')
    if topic:
        queryset = queryset.filter(topic=topic)

    difficulty = request.GET.get('difficulty')
    if difficulty:
        queryset = queryset.filter(difficulty=difficulty)

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
        'selected_subject': subject or '',
        'search_query': query or '',
        'is_zenken_or_teacher': user.is_teacher or user.is_zenken_student,
    }
    return render(request, 'app/questions/question_list.html', context)


@login_required
def question_detail_view(request, pk):
    question = get_object_or_404(AptitudeQuestion, pk=pk)
    user = request.user

    if (question.subject == 'JAPANESE' or question.access_tier == 'ZENKEN_ONLY') and user.is_non_zenken_student and not user.is_teacher:
        messages.error(request, "This question is exclusive to Zenken Enrolled Students.")
        return redirect('app:practice_arena')

    user_choice = None
    is_correct = None
    revealed = False

    if request.method == 'POST':
        user_choice = request.POST.get('chosen_option')
        revealed = True
        if user_choice:
            is_correct = (user_choice == question.correct_option)
            QuestionPracticeLog.objects.create(
                student=user,
                question=question,
                chosen_option=user_choice,
                is_correct=is_correct,
            )
            # Update user streak & points
            if not user.is_teacher:
                streak = get_or_create_streak(user)
                streak.record_activity(points=10 if is_correct else 3, is_quiz=False)

            if is_correct:
                messages.success(request, f"Correct! Option {question.correct_option} is the right answer. (+10 Streak Points!)")
            else:
                messages.warning(request, f"Incorrect. You chose Option {user_choice}. Correct answer is Option {question.correct_option}.")

    context = {
        'question': question,
        'user_choice': user_choice,
        'is_correct': is_correct,
        'revealed': revealed,
    }
    return render(request, 'app/questions/question_detail.html', context)


# ==============================================================================
# ACADEMY UPDATES
# ==============================================================================

@teacher_required
def update_create_view(request):
    if request.method == 'POST':
        form = AcademyUpdateForm(request.POST)
        if form.is_valid():
            u = form.save(commit=False)
            u.teacher = request.user
            u.save()
            messages.success(request, f"Academy Notice '{u.title}' broadcast successfully!")
            return redirect('app:update_list')
    else:
        form = AcademyUpdateForm()

    return render(request, 'app/updates/update_form.html', {
        'form': form,
        'title': 'Post Academy Notice',
        'btn_text': 'Broadcast Update',
    })


@teacher_required
def update_edit_view(request, pk):
    u = get_object_or_404(AcademyUpdate, pk=pk)
    if not request.user.is_superuser and u.teacher != request.user:
        messages.error(request, "Permission denied.")
        return redirect('app:update_list')

    if request.method == 'POST':
        form = AcademyUpdateForm(request.POST, instance=u)
        if form.is_valid():
            form.save()
            messages.success(request, f"Notice '{u.title}' updated.")
            return redirect('app:update_list')
    else:
        form = AcademyUpdateForm(instance=u)

    return render(request, 'app/updates/update_form.html', {
        'form': form,
        'title': f"Edit Notice: {u.title}",
        'btn_text': 'Save Changes',
        'update': u,
    })


@teacher_required
def update_delete_view(request, pk):
    u = get_object_or_404(AcademyUpdate, pk=pk)
    if not request.user.is_superuser and u.teacher != request.user:
        messages.error(request, "Permission denied.")
        return redirect('app:update_list')

    if request.method == 'POST':
        title = u.title
        u.delete()
        messages.success(request, f"Notice '{title}' deleted.")
        return redirect('app:update_list')

    return render(request, 'app/updates/update_confirm_delete.html', {'update': u})


@login_required
def update_list_view(request):
    user = request.user
    if user.is_teacher:
        updates = AcademyUpdate.objects.all()
    elif user.is_zenken_student:
        updates = AcademyUpdate.objects.filter(Q(target_audience='ALL') | Q(target_audience='ZENKEN_ONLY'))
    else:
        updates = AcademyUpdate.objects.filter(Q(target_audience='ALL') | Q(target_audience='NON_ZENKEN_ONLY'))

    return render(request, 'app/updates/update_list.html', {'updates': updates})


# ==============================================================================
# INTERACTIVE AI TUTOR & CHATBOT (POWERED BY GROQ)
# ==============================================================================

import urllib.request
from django.conf import settings


@require_POST
@login_required
def chat_bot_api(request):
    """
    API endpoint: Interactive AI Tutor and Career Advisor powered by Groq.
    Assists students with Aptitude shortcuts, Japanese explanations, placement tips,
    and platform navigation.
    """
    try:
        data = json.loads(request.body)
        user_message = data.get('message', '').strip()
        history = data.get('history', [])

        if not user_message:
            return JsonResponse({'error': 'Message cannot be empty'}, status=400)

        api_key = getattr(settings, 'GROQ_API_KEY', '')
        primary_model = getattr(settings, 'GROQ_MODEL', 'qwen/qwen3.8-27b')
        fallback_models = getattr(settings, 'GROQ_FALLBACK_MODELS', ['openai/gpt-oss-120b', 'openai/gpt-oss-20b'])

        user = request.user
        role_label = user.get_role_display()
        is_zenken = user.is_zenken_student or user.is_teacher

        system_prompt = (
            "You are 'Arena AI Mentor', the official intelligent interactive tutor for scemquiz.arena at Sahyadri College of Engineering & Management. "
            f"The user you are speaking with is {user.first_name or user.username} (Role: {role_label}). "
            "Your core capabilities: "
            "1. Aptitude Mastery: Solve quantitative problems step-by-step, give short mental-math tricks for Time & Work, Speed, Percentages, Algebra, and Geometry. "
            "2. Japanese Language Mentor: For Zenken Scholars, explain Kanji readings (Onyomi/Kunyomi), JLPT N5/N4/N3 grammar particles, and Japanese corporate etiquette (Keigo). "
            "3. Placement Strategy: Give actionable advice on technical interview rounds, resume building, and placement drives. "
            "4. Platform Guide: Guide users to scemquiz.arena features like Leaderboards, Topic Practice Rooms (1,200+ MCQs), 20-Question Timed Quizzes, Opportunities, and Study Materials. "
            "Tone: Inspiring, friendly, knowledgeable, and concise. Format math formulas cleanly using markdown bolding or bullet points."
        )

        messages_list = [{'role': 'system', 'content': system_prompt}]
        for item in history[-6:]:
            role = item.get('role', 'user')
            content = item.get('content', '')
            if role in ['user', 'assistant'] and content:
                messages_list.append({'role': role, 'content': content})

        messages_list.append({'role': 'user', 'content': user_message})

        models_to_try = [primary_model] + fallback_models
        last_error = None

        for model in models_to_try:
            try:
                payload = {
                    'model': model,
                    'messages': messages_list,
                    'max_tokens': 600,
                    'temperature': 0.7,
                }
                req = urllib.request.Request(
                    'https://api.groq.com/openai/v1/chat/completions',
                    data=json.dumps(payload).encode('utf-8'),
                    headers={
                        'Authorization': f'Bearer {api_key}',
                        'Content-Type': 'application/json',
                        'User-Agent': 'scemquiz-arena/1.0 (Mozilla/5.0)'
                    }
                )
                with urllib.request.urlopen(req, timeout=12) as response:
                    res_json = json.loads(response.read().decode('utf-8'))
                    bot_reply = res_json['choices'][0]['message']['content']
                    return JsonResponse({'reply': bot_reply, 'model': model})
            except Exception as e:
                last_error = str(e)
                continue

        fallback_reply = (
            f"Hello {user.first_name or user.username}! I am your Arena AI Mentor. "
            "Here is a key aptitude tip: For Time & Work, combine work rates as 1/A + 1/B to easily solve combined days! "
            "Check out our Topic-Wise Practice Rooms to test your skills."
        )
        return JsonResponse({'reply': fallback_reply, 'note': last_error})

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
def assistant_page_view(request):
    """Full-page interactive AI tutor & mentor interface."""
    return render(request, 'app/ai_tutor/assistant_page.html')
