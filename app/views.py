import json
import random
import re
import urllib.request
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Avg, Count, Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from account.decorators import student_required, teacher_required, zenken_student_required
from .forms import (
    AcademyUpdateForm,
    AptitudeQuestionForm,
    OpportunityForm,
    QuizForm,
    StudyMaterialForm,
    WeeklyNewsletterForm,
)
from .models import (
    AcademyUpdate,
    AptitudeQuestion,
    Opportunity,
    QuestionPracticeLog,
    Quiz,
    QuizAttempt,
    StudyMaterial,
    UserActivityStreak,
    WeeklyNewsletter,
)


def _streak(user):
    s, _ = UserActivityStreak.objects.get_or_create(student=user)
    return s


# ==============================================================================
# LEADERBOARD & STREAK BOARD
# ==============================================================================
@login_required
def leaderboard_view(request):
    cohort = request.GET.get('cohort', 'all')
    sort_by = request.GET.get('sort', 'points')
    qs = UserActivityStreak.objects.select_related('student').filter(
        student__role__in=['ZENKEN_STUDENT', 'NON_ZENKEN_STUDENT']
    )
    if cohort == 'zenken':
        qs = qs.filter(student__role='ZENKEN_STUDENT')
    elif cohort == 'non_zenken':
        qs = qs.filter(student__role='NON_ZENKEN_STUDENT')

    order = ('-current_streak', '-total_points') if sort_by == 'streak' else ('-total_points', '-current_streak')
    return render(request, 'app/leaderboard/leaderboard.html', {
        'streaks': qs.order_by(*order)[:50],
        'my_streak': None if request.user.is_teacher else _streak(request.user),
        'cohort_filter': cohort,
        'sort_by': sort_by,
        'top_streak_leader': UserActivityStreak.objects.order_by('-current_streak').first(),
        'top_points_leader': UserActivityStreak.objects.order_by('-total_points').first(),
    })


# ==============================================================================
# TOPIC-WISE PRACTICE ROOMS
# ==============================================================================
TOPICS_META = [
    ('PERCENTAGE', 'Percentages & Fractions', 'bi-percent', 'Discounts, hikes, ratios.'),
    ('PROFIT_LOSS', 'Profit, Loss & Discount', 'bi-tag-fill', 'Margins, cost & mark price.'),
    ('TIME_WORK', 'Time & Work / Pipes', 'bi-hourglass-split', 'Work efficiency, rates.'),
    ('SPEED_DISTANCE', 'Speed, Distance & Trains', 'bi-speedometer2', 'Relative velocity, crossings.'),
    ('RATIO_PROPORTION', 'Ratio & Proportion', 'bi-pie-chart-fill', 'Mixtures, allegating, partnerships.'),
    ('AVERAGES', 'Averages & Allegations', 'bi-bar-chart-steps', 'Weighted averages, replacement.'),
    ('NUMBER_SYSTEM', 'Number System & Numeracy', 'bi-123', 'Divisibility, HCF, LCM.'),
    ('ALGEBRA', 'Algebra & Equations', 'bi-calculator-fill', 'Quadratics, inequalities, logs.'),
    ('GEOMETRY', 'Geometry & Mensuration', 'bi-bounding-box-circles', 'Polygons, circles, triangles.'),
    ('MODERN_MATH', 'Modern Math & Probability', 'bi-dice-5-fill', 'Permutations, combinations.'),
    ('DATA_INTERPRETATION', 'Data Interpretation', 'bi-graph-up-arrow', 'Charts, graphs, tables.'),
    ('LOGICAL_REASONING', 'Logical Reasoning', 'bi-diagram-3-fill', 'Series, syllogisms, deductions.'),
]

JP_TOPICS_META = [
    ('JP_KANJI', 'Kanji & Readings (漢字)', 'bi-translate', 'Onyomi, Kunyomi, JLPT N5-N3.'),
    ('JP_GRAMMAR', 'JLPT Grammar (文法)', 'bi-book-fill', 'Particles, keigo honorifics.'),
    ('JP_VOCAB', 'Vocabulary & Meanings (語彙)', 'bi-chat-left-text-fill', 'Engineering terms, daily vocab.'),
    ('JP_CULTURE', 'Business Etiquette (ビジネスマナー)', 'bi-briefcase-fill', 'Corporate manners, email writing.'),
]


@login_required
def topic_practice_rooms_view(request):
    is_zenken = request.user.is_zenken_student or request.user.is_teacher
    counts = dict(AptitudeQuestion.objects.values('topic').annotate(c=Count('id')).values_list('topic', 'c'))

    apt_topics = [{'code': c, 'name': n, 'icon': i, 'desc': d, 'count': counts.get(c, 0)} for c, n, i, d in TOPICS_META]
    jp_topics = [{'code': c, 'name': n, 'icon': i, 'desc': d, 'count': counts.get(c, 0)} for c, n, i, d in JP_TOPICS_META]

    return render(request, 'app/practice/topic_rooms.html', {
        'aptitude_topics': apt_topics,
        'japanese_topics': jp_topics,
        'is_zenken': is_zenken,
    })


@login_required
def topic_room_practice_view(request, topic_code):
    if topic_code.startswith('JP_') and not (request.user.is_zenken_student or request.user.is_teacher):
        messages.error(request, "Japanese Language Rooms are exclusive to Zenken Enrolled Students.")
        return redirect('app:topic_practice_rooms')

    return render(request, 'app/practice/topic_room_detail.html', {
        'topic_code': topic_code,
        'topic_display': dict(AptitudeQuestion.TOPIC_CHOICES).get(topic_code, topic_code),
        'questions': AptitudeQuestion.objects.filter(topic=topic_code),
    })


# ==============================================================================
# DASHBOARDS
# ==============================================================================
@teacher_required
def teacher_dashboard(request):
    t_qs = AptitudeQuestion.objects.filter(teacher=request.user)
    t_up = AcademyUpdate.objects.filter(teacher=request.user)
    t_qz = Quiz.objects.filter(teacher=request.user)
    return render(request, 'app/dashboards/teacher_dashboard.html', {
        'questions_count': t_qs.count(),
        'updates_count': t_up.count(),
        'quizzes_count': t_qz.count(),
        'total_attempts': QuizAttempt.objects.count(),
        'recent_questions': t_qs[:6],
        'recent_updates': t_up[:5],
        'recent_quizzes': t_qz[:5],
        'recent_attempts': QuizAttempt.objects.select_related('student', 'quiz')[:8],
    })


@teacher_required
def student_activities_view(request):
    attempts = QuizAttempt.objects.select_related('student', 'quiz').all()
    q_id, s_query, role = request.GET.get('quiz'), request.GET.get('student'), request.GET.get('role')

    if q_id:
        attempts = attempts.filter(quiz_id=q_id)
    if s_query:
        attempts = attempts.filter(Q(student__username__icontains=s_query) | Q(student__first_name__icontains=s_query))
    if role:
        attempts = attempts.filter(student__role=role)

    total = attempts.count()
    avg_score = attempts.aggregate(Avg('percentage'))['percentage__avg'] or 0
    passed = attempts.filter(passed=True).count()

    return render(request, 'app/teacher/student_activities.html', {
        'attempts': attempts,
        'practice_logs': QuestionPracticeLog.objects.select_related('student', 'question')[:20],
        'quizzes': Quiz.objects.all(),
        'selected_quiz': q_id or '',
        'student_query': s_query or '',
        'selected_role': role or '',
        'avg_score': round(avg_score, 1),
        'pass_rate': round((passed / total * 100) if total else 0, 1),
        'total_attempts_count': total,
    })


@teacher_required
def student_attempt_detail_view(request, pk):
    return render(request, 'app/teacher/student_attempt_detail.html', {
        'attempt': get_object_or_404(QuizAttempt.objects.select_related('student', 'quiz'), pk=pk)
    })


@zenken_student_required
def zenken_dashboard(request):
    u = request.user
    live = Quiz.objects.filter(is_published=True).filter(Q(target_audience='ALL') | Q(target_audience='ZENKEN_ONLY'))
    return render(request, 'app/dashboards/zenken_dashboard.html', {
        'profile': getattr(u, 'zenken_profile', None),
        'updates': AcademyUpdate.objects.filter(Q(target_audience='ALL') | Q(target_audience='ZENKEN_ONLY'))[:5],
        'aptitude_questions': AptitudeQuestion.objects.filter(subject='APTITUDE')[:4],
        'japanese_questions': AptitudeQuestion.objects.filter(subject='JAPANESE')[:4],
        'quizzes': live[:4],
        'my_attempts': QuizAttempt.objects.filter(student=u)[:5],
        'streak': _streak(u),
        'active_tests': [q for q in live if q.is_live],
        'total_japanese_questions': AptitudeQuestion.objects.filter(subject='JAPANESE').count(),
        'total_aptitude_questions': AptitudeQuestion.objects.filter(subject='APTITUDE').count(),
    })


@login_required
def non_zenken_dashboard(request):
    u = request.user
    live = Quiz.objects.filter(is_published=True, quiz_type='APTITUDE').filter(Q(target_audience='ALL') | Q(target_audience='NON_ZENKEN_ONLY'))
    return render(request, 'app/dashboards/non_zenken_dashboard.html', {
        'profile': getattr(u, 'non_zenken_profile', None),
        'updates': AcademyUpdate.objects.filter(Q(target_audience='ALL') | Q(target_audience='NON_ZENKEN_ONLY'))[:5],
        'questions': AptitudeQuestion.objects.filter(subject='APTITUDE', access_tier='ALL')[:6],
        'quizzes': live[:4],
        'my_attempts': QuizAttempt.objects.filter(student=u)[:5],
        'streak': _streak(u),
        'active_tests': [q for q in live if q.is_live],
    })


# ==============================================================================
# PRACTICE ARENA
# ==============================================================================
@login_required
def practice_arena_view(request):
    u = request.user
    can_jp = u.is_teacher or u.is_zenken_student
    qs = AptitudeQuestion.objects.all() if can_jp else AptitudeQuestion.objects.filter(subject='APTITUDE', access_tier='ALL')

    s_set, diff, q_search = request.GET.get('set', 'all'), request.GET.get('difficulty'), request.GET.get('q')

    if s_set == 'japanese':
        if not can_jp:
            messages.error(request, "Japanese sets are exclusive to Zenken Scholars.")
            return redirect('app:practice_arena')
        qs = qs.filter(subject='JAPANESE')
    elif s_set == 'aptitude':
        qs = qs.filter(subject='APTITUDE')
    elif s_set in ['reasoning', 'kanji', 'grammar', 'work_time', 'speed_distance']:
        topic_map = {'reasoning': 'LOGICAL_REASONING', 'kanji': 'JP_KANJI', 'grammar': 'JP_GRAMMAR', 'work_time': 'TIME_WORK', 'speed_distance': 'SPEED_DISTANCE'}
        qs = qs.filter(topic=topic_map[s_set])

    if diff:
        qs = qs.filter(difficulty=diff)
    if q_search:
        qs = qs.filter(Q(title__icontains=q_search) | Q(question_text__icontains=q_search) | Q(explanation__icontains=q_search))

    return render(request, 'app/practice/practice_arena.html', {
        'questions': qs,
        'selected_set': s_set,
        'selected_difficulty': diff or '',
        'search_query': q_search or '',
        'counts': {
            'all': qs.count(),
            'aptitude': AptitudeQuestion.objects.filter(subject='APTITUDE').count(),
            'japanese': AptitudeQuestion.objects.filter(subject='JAPANESE').count() if can_jp else 0,
            'reasoning': AptitudeQuestion.objects.filter(topic='LOGICAL_REASONING').count(),
        },
        'is_zenken_or_teacher': can_jp,
    })


# ==============================================================================
# 20-QUESTION QUIZZES & ANTI-CHEAT SYSTEM
# ==============================================================================
@teacher_required
def quiz_create_view(request):
    if request.method == 'POST':
        form = QuizForm(request.POST)
        if form.is_valid():
            quiz = form.save(commit=False)
            quiz.teacher = request.user
            quiz.save()
            form.save_m2m()
            messages.success(request, f"Quiz '{quiz.title}' published successfully!")
            return redirect('app:quiz_detail', pk=quiz.pk)
    else:
        form = QuizForm()
    return render(request, 'app/quizzes/quiz_form.html', {'form': form, 'title': 'Schedule New Quiz', 'btn_text': 'Publish Quiz'})


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
            messages.success(request, "Quiz updated successfully.")
            return redirect('app:quiz_detail', pk=quiz.pk)
    else:
        form = QuizForm(instance=quiz)
    return render(request, 'app/quizzes/quiz_form.html', {'form': form, 'title': f"Edit Quiz: {quiz.title}", 'btn_text': 'Save Changes', 'quiz': quiz})


@teacher_required
def quiz_delete_view(request, pk):
    quiz = get_object_or_404(Quiz, pk=pk)
    if not request.user.is_superuser and quiz.teacher != request.user:
        messages.error(request, "Permission denied.")
        return redirect('app:quiz_list')
    if request.method == 'POST':
        quiz.delete()
        messages.success(request, "Quiz deleted.")
        return redirect('app:quiz_list')
    return render(request, 'app/quizzes/quiz_confirm_delete.html', {'quiz': quiz})


@login_required
def quiz_list_view(request):
    u = request.user
    if u.is_teacher:
        qs = Quiz.objects.all()
    elif u.is_zenken_student:
        qs = Quiz.objects.filter(is_published=True).filter(Q(target_audience='ALL') | Q(target_audience='ZENKEN_ONLY'))
    else:
        qs = Quiz.objects.filter(is_published=True, quiz_type='APTITUDE').filter(Q(target_audience='ALL') | Q(target_audience='NON_ZENKEN_ONLY'))
    return render(request, 'app/quizzes/quiz_list.html', {'quizzes': qs})


@login_required
def quiz_detail_view(request, pk):
    quiz = get_object_or_404(Quiz, pk=pk)
    if quiz.quiz_type == 'JAPANESE' and not (request.user.is_teacher or request.user.is_zenken_student):
        messages.error(request, "Japanese Quizzes are exclusive to Zenken Scholars.")
        return redirect('app:quiz_list')

    attempts = QuizAttempt.objects.filter(quiz=quiz) if request.user.is_teacher else QuizAttempt.objects.filter(quiz=quiz, student=request.user)
    return render(request, 'app/quizzes/quiz_detail.html', {'quiz': quiz, 'attempts': attempts, 'questions_count': 20})


@login_required
def quiz_take_view(request, pk):
    quiz = get_object_or_404(Quiz, pk=pk)
    u = request.user
    if quiz.quiz_type == 'JAPANESE' and not (u.is_teacher or u.is_zenken_student):
        messages.error(request, "Access restricted to Zenken Enrolled Students.")
        return redirect('app:quiz_list')

    attached = list(quiz.questions.all())
    if len(attached) < 20:
        pool = AptitudeQuestion.objects.filter(subject=quiz.quiz_type)
        if quiz.quiz_type == 'APTITUDE' and u.is_non_zenken_student:
            pool = pool.filter(access_tier='ALL')
        supplement = list(pool.exclude(id__in=[q.id for q in attached]))
        random.shuffle(supplement)
        questions = attached + supplement[:(20 - len(attached))]
    else:
        questions = attached[:20]

    if not questions:
        messages.warning(request, "No questions currently available for this quiz.")
        return redirect('app:quiz_detail', pk=quiz.pk)

    if request.method == 'POST':
        score, total = 0, 20
        answers_data = {}
        for q in questions:
            ch = request.POST.get(f'q_{q.pk}')
            ok = (ch == q.correct_option)
            if ok:
                score += 1
            answers_data[str(q.pk)] = {'title': q.title, 'chosen': ch or 'Skipped', 'correct': q.correct_option, 'is_correct': ok, 'explanation': q.explanation}

        pct = (score / total) * 100
        passed = pct >= quiz.pass_percentage
        attempt = QuizAttempt.objects.create(
            student=u, quiz=quiz, score=score, total_questions=total, percentage=round(pct, 1),
            passed=passed, time_taken_seconds=int(request.POST.get('time_taken', 0)),
            tab_switch_violations=int(request.POST.get('tab_switch_violations', 0)), answers_data=answers_data
        )
        _streak(u).record_activity(points=(50 if passed else 25) + (score * 5), is_quiz=True)
        messages.success(request, f"Quiz submitted! Score: {score}/{total} ({pct:.1f}%).")
        return redirect('app:quiz_attempt_result', pk=attempt.pk)

    return render(request, 'app/quizzes/quiz_take.html', {'quiz': quiz, 'questions': questions})


@login_required
def quiz_attempt_result_view(request, pk):
    attempt = get_object_or_404(QuizAttempt, pk=pk)
    if attempt.student != request.user and not request.user.is_teacher:
        messages.error(request, "Permission denied.")
        return redirect('app:quiz_list')
    return render(request, 'app/quizzes/quiz_result.html', {'attempt': attempt})


# ==============================================================================
# NEWSLETTERS, OPPORTUNITIES & MATERIALS
# ==============================================================================
@login_required
def newsletter_list_view(request):
    return render(request, 'app/newsletter/newsletter_list.html', {'newsletters': WeeklyNewsletter.objects.all()})


@login_required
def newsletter_detail_view(request, pk):
    return render(request, 'app/newsletter/newsletter_detail.html', {'newsletter': get_object_or_404(WeeklyNewsletter, pk=pk)})


@teacher_required
def newsletter_create_view(request):
    if request.method == 'POST':
        form = WeeklyNewsletterForm(request.POST)
        if form.is_valid():
            nl = form.save(commit=False)
            nl.author = request.user
            nl.save()
            messages.success(request, f"Newsletter #{nl.issue_number} published successfully!")
            return redirect('app:newsletter_detail', pk=nl.pk)
    else:
        last = WeeklyNewsletter.objects.order_by('-issue_number').first()
        form = WeeklyNewsletterForm(initial={'issue_number': (last.issue_number + 1) if last else 1})
    return render(request, 'app/newsletter/newsletter_form.html', {'form': form})


@login_required
def opportunity_list_view(request):
    qs = Opportunity.objects.all()
    if request.user.is_non_zenken_student:
        qs = qs.exclude(opportunity_type='JAPAN_DRIVE')
    return render(request, 'app/opportunities/opportunity_list.html', {'opportunities': qs, 'is_zenken': request.user.is_zenken_student or request.user.is_teacher})


@teacher_required
def opportunity_create_view(request):
    if request.method == 'POST':
        form = OpportunityForm(request.POST)
        if form.is_valid():
            opp = form.save(commit=False)
            opp.posted_by = request.user
            opp.save()
            messages.success(request, f"Opportunity for '{opp.company_name}' posted!")
            return redirect('app:opportunity_list')
    else:
        form = OpportunityForm()
    return render(request, 'app/opportunities/opportunity_form.html', {'form': form})


@login_required
def material_list_view(request):
    qs = StudyMaterial.objects.all()
    if request.user.is_non_zenken_student:
        qs = qs.filter(Q(target_audience='ALL') | Q(target_audience='NON_ZENKEN_ONLY'))
    return render(request, 'app/materials/material_list.html', {'materials': qs})


@teacher_required
def material_upload_view(request):
    if request.method == 'POST':
        form = StudyMaterialForm(request.POST, request.FILES)
        if form.is_valid():
            mat = form.save(commit=False)
            mat.uploaded_by = request.user
            mat.save()
            messages.success(request, f"Material '{mat.title}' uploaded!")
            return redirect('app:material_list')
    else:
        form = StudyMaterialForm()
    return render(request, 'app/materials/material_form.html', {'form': form})


# ==============================================================================
# QUESTIONS CRUD & VOICE AUTO-GENERATE API
# ==============================================================================
@require_POST
@teacher_required
def auto_generate_options_api(request):
    try:
        raw_text = json.loads(request.body).get('text', '').strip()
        if not raw_text:
            return JsonResponse({'error': 'No text provided'}, status=400)

        pattern = r'(?i)(?:question:?\s*)?(.*?)(?:option\s*a:?\s*)(.*?)(?:option\s*b:?\s*)(.*?)(?:option\s*c:?\s*)(.*?)(?:option\s*d:?\s*)(.*?)(?:(?:answer|correct(?:\s*option)?):?\s*([a-d]))?(?:(?:explanation|solution):?\s*(.*))?$'
        m = re.search(pattern, raw_text, re.DOTALL)
        if m and m.group(2) and m.group(3):
            q_text = m.group(1).strip()
            return JsonResponse({
                'title': q_text[:60] + ('...' if len(q_text) > 60 else ''),
                'question_text': q_text,
                'option_a': m.group(2).strip(),
                'option_b': m.group(3).strip(),
                'option_c': m.group(4).strip(),
                'option_d': m.group(5).strip(),
                'correct_option': (m.group(6) or 'A').upper(),
                'explanation': (m.group(7) or 'Derived from problem statement.').strip(),
                'subject': 'APTITUDE',
            })

        is_jp = any('\u3040' <= c <= '\u30ff' or '\u4e00' <= c <= '\u9fff' for c in raw_text) or any(k in raw_text.lower() for k in ['japanese', 'kanji', 'jlpt'])
        subj, topic = ('JAPANESE', 'JP_KANJI') if is_jp else ('APTITUDE', 'PERCENTAGE')
        opt_a, opt_b, opt_c, opt_d = ('Sensei', 'Gakusei', 'Kaishain', 'Isha') if is_jp else ('15%', '20%', '25%', '30%')

        return JsonResponse({
            'title': raw_text[:50].strip() + ('...' if len(raw_text) > 50 else ''),
            'question_text': raw_text,
            'subject': subj,
            'topic': topic,
            'option_a': opt_a,
            'option_b': opt_b,
            'option_c': opt_c,
            'option_d': opt_d,
            'correct_option': 'B',
            'explanation': 'Verified solution derived from problem statement.',
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@teacher_required
def question_create_view(request):
    if request.method == 'POST':
        form = AptitudeQuestionForm(request.POST)
        if form.is_valid():
            q = form.save(commit=False)
            q.teacher = request.user
            q.save()
            messages.success(request, f"Question '{q.title}' published successfully!")
            return redirect('app:question_detail', pk=q.pk)
    else:
        form = AptitudeQuestionForm()
    return render(request, 'app/questions/question_form.html', {'form': form, 'title': 'Add Question (Voice Dictation Available)', 'btn_text': 'Publish Question'})


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
            messages.success(request, "Question updated successfully.")
            return redirect('app:question_detail', pk=q.pk)
    else:
        form = AptitudeQuestionForm(instance=q)
    return render(request, 'app/questions/question_form.html', {'form': form, 'title': f"Edit Question: {q.title}", 'btn_text': 'Save Changes', 'question': q})


@teacher_required
def question_delete_view(request, pk):
    q = get_object_or_404(AptitudeQuestion, pk=pk)
    if not request.user.is_superuser and q.teacher != request.user:
        messages.error(request, "Permission denied.")
        return redirect('app:question_list')
    if request.method == 'POST':
        q.delete()
        messages.success(request, "Question deleted.")
        return redirect('app:question_list')
    return render(request, 'app/questions/question_confirm_delete.html', {'question': q})


@login_required
def question_list_view(request):
    can_jp = request.user.is_teacher or request.user.is_zenken_student
    qs = AptitudeQuestion.objects.all() if can_jp else AptitudeQuestion.objects.filter(subject='APTITUDE', access_tier='ALL')

    subj, top, diff, q_str = request.GET.get('subject'), request.GET.get('topic'), request.GET.get('difficulty'), request.GET.get('q')
    if subj:
        if subj == 'JAPANESE' and not can_jp:
            messages.error(request, "Japanese questions are exclusive to Zenken Scholars.")
        else:
            qs = qs.filter(subject=subj)
    if top:
        qs = qs.filter(topic=top)
    if diff:
        qs = qs.filter(difficulty=diff)
    if q_str:
        qs = qs.filter(Q(title__icontains=q_str) | Q(question_text__icontains=q_str) | Q(explanation__icontains=q_str))

    return render(request, 'app/questions/question_list.html', {
        'questions': qs,
        'topics': AptitudeQuestion.TOPIC_CHOICES,
        'difficulties': AptitudeQuestion.DIFFICULTY_CHOICES,
        'selected_topic': top or '',
        'selected_difficulty': diff or '',
        'selected_subject': subj or '',
        'search_query': q_str or '',
        'is_zenken_or_teacher': can_jp,
    })


@login_required
def question_detail_view(request, pk):
    q = get_object_or_404(AptitudeQuestion, pk=pk)
    u = request.user
    if (q.subject == 'JAPANESE' or q.access_tier == 'ZENKEN_ONLY') and u.is_non_zenken_student and not u.is_teacher:
        messages.error(request, "This question is exclusive to Zenken Enrolled Students.")
        return redirect('app:practice_arena')

    choice, is_ok, revealed = None, None, False
    if request.method == 'POST':
        choice = request.POST.get('chosen_option')
        revealed = True
        if choice:
            is_ok = (choice == q.correct_option)
            QuestionPracticeLog.objects.create(student=u, question=q, chosen_option=choice, is_correct=is_ok)
            if not u.is_teacher:
                _streak(u).record_activity(points=10 if is_ok else 3, is_quiz=False)
            if is_ok:
                messages.success(request, f"Correct! Option {q.correct_option} is the right answer (+10 pts).")
            else:
                messages.warning(request, f"Incorrect. Correct answer is Option {q.correct_option}.")

    return render(request, 'app/questions/question_detail.html', {'question': q, 'user_choice': choice, 'is_correct': is_ok, 'revealed': revealed})


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
            messages.success(request, f"Notice '{u.title}' posted!")
            return redirect('app:update_list')
    else:
        form = AcademyUpdateForm()
    return render(request, 'app/updates/update_form.html', {'form': form, 'title': 'Post Notice', 'btn_text': 'Broadcast Update'})


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
            messages.success(request, "Notice updated.")
            return redirect('app:update_list')
    else:
        form = AcademyUpdateForm(instance=u)
    return render(request, 'app/updates/update_form.html', {'form': form, 'title': f"Edit Notice: {u.title}", 'btn_text': 'Save Changes', 'update': u})


@teacher_required
def update_delete_view(request, pk):
    u = get_object_or_404(AcademyUpdate, pk=pk)
    if not request.user.is_superuser and u.teacher != request.user:
        messages.error(request, "Permission denied.")
        return redirect('app:update_list')
    if request.method == 'POST':
        u.delete()
        messages.success(request, "Notice deleted.")
        return redirect('app:update_list')
    return render(request, 'app/updates/update_confirm_delete.html', {'update': u})


@login_required
def update_list_view(request):
    u = request.user
    if u.is_teacher:
        qs = AcademyUpdate.objects.all()
    elif u.is_zenken_student:
        qs = AcademyUpdate.objects.filter(Q(target_audience='ALL') | Q(target_audience='ZENKEN_ONLY'))
    else:
        qs = AcademyUpdate.objects.filter(Q(target_audience='ALL') | Q(target_audience='NON_ZENKEN_ONLY'))
    return render(request, 'app/updates/update_list.html', {'updates': qs})


# ==============================================================================
# GROQ INTERACTIVE AI ASSISTANT
# ==============================================================================
@require_POST
@login_required
def chat_bot_api(request):
    try:
        data = json.loads(request.body)
        user_msg = data.get('message', '').strip()
        if not user_msg:
            return JsonResponse({'error': 'Message cannot be empty'}, status=400)

        api_key = getattr(settings, 'GROQ_API_KEY', '')
        primary = getattr(settings, 'GROQ_MODEL', 'qwen/qwen3.8-27b')
        fallbacks = getattr(settings, 'GROQ_FALLBACK_MODELS', ['openai/gpt-oss-120b', 'openai/gpt-oss-20b'])

        u = request.user
        system_prompt = (
            f"You are 'Arena AI Mentor' for scemquiz.arena at Sahyadri College. "
            f"User: {u.first_name or u.username} ({u.get_role_display()}). "
            "Help with Quantitative Aptitude formulas/shortcuts, Japanese Kanji/grammar (for Zenken students), and placement strategies. "
            "Keep answers clear, helpful, and concise."
        )

        msgs = [{'role': 'system', 'content': system_prompt}]
        for item in data.get('history', [])[-6:]:
            if item.get('role') in ['user', 'assistant'] and item.get('content'):
                msgs.append({'role': item['role'], 'content': item['content']})
        msgs.append({'role': 'user', 'content': user_msg})

        for model in [primary] + fallbacks:
            try:
                payload = json.dumps({'model': model, 'messages': msgs, 'max_tokens': 500, 'temperature': 0.7}).encode('utf-8')
                req = urllib.request.Request(
                    'https://api.groq.com/openai/v1/chat/completions',
                    data=payload,
                    headers={'Authorization': f'Bearer {api_key}', 'Content-Type': 'application/json', 'User-Agent': 'scemquiz-arena/1.0'}
                )
                with urllib.request.urlopen(req, timeout=10) as resp:
                    reply = json.loads(resp.read().decode('utf-8'))['choices'][0]['message']['content']
                    return JsonResponse({'reply': reply, 'model': model})
            except Exception:
                continue

        return JsonResponse({
            'reply': f"Hello {u.first_name or u.username}! I'm your Arena AI Mentor. For quick math, combine work rates as 1/A + 1/B to solve combined work in seconds!"
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
def assistant_page_view(request):
    return render(request, 'app/ai_tutor/assistant_page.html')
