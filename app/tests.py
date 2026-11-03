from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
import json
from account.models import TeacherProfile, ZenkenStudentProfile, NonZenkenStudentProfile
from .models import (
    AptitudeQuestion,
    AcademyUpdate,
    Quiz,
    QuizAttempt,
    UserActivityStreak,
    WeeklyNewsletter,
    Opportunity,
    StudyMaterial,
)

User = get_user_model()


class AptitudeAndArenaTests(TestCase):
    def setUp(self):
        self.client = Client()

        # Teacher superuser with password 2654
        self.teacher = User.objects.create_user(
            username='teacher_scem', password='2654', role=User.Role.TEACHER, is_staff=True, is_superuser=True
        )
        TeacherProfile.objects.create(user=self.teacher, employee_id='T001', department='Aptitude')

        # Zenken student
        self.zenken_student = User.objects.create_user(
            username='zenken1', password='pass', role=User.Role.ZENKEN_STUDENT, email='zenken1@sahyadri.edu.in'
        )
        ZenkenStudentProfile.objects.create(
            user=self.zenken_student, zenken_id='ZK001', batch_name='Batch 1', college_name='Coll 1'
        )

        # Non-Zenken student
        self.non_zenken_student = User.objects.create_user(
            username='nonzenken1', password='pass', role=User.Role.NON_ZENKEN_STUDENT, email='nonzenken1@sahyadri.edu.in'
        )
        NonZenkenStudentProfile.objects.create(
            user=self.non_zenken_student, institution_name='College 2', target_exam_or_goal='GRE'
        )

    def test_teacher_superuser_credentials(self):
        login_success = self.client.login(username='teacher_scem', password='2654')
        self.assertTrue(login_success)
        self.assertTrue(self.teacher.is_superuser)
        self.assertTrue(self.teacher.is_teacher)

    def test_exclusive_japanese_question_restriction(self):
        jp_q = AptitudeQuestion.objects.create(
            teacher=self.teacher,
            title='Kanji Reading: 先生',
            subject='JAPANESE',
            topic='JP_KANJI',
            difficulty='EASY',
            access_tier='ZENKEN_ONLY',
            question_text='Reading of 先生?',
            option_a='Sensei', option_b='Gakusei', option_c='Isha', option_d='Kaishain',
            correct_option='A',
            explanation='Sensei means teacher in Japanese.',
        )

        # Zenken student CAN access
        self.client.login(username='zenken1', password='pass')
        res = self.client.get(reverse('app:question_detail', kwargs={'pk': jp_q.pk}))
        self.assertEqual(res.status_code, 200)
        self.assertContains(res, 'Kanji Reading: 先生')
        self.client.logout()

        # Non-Zenken student CANNOT access
        self.client.login(username='nonzenken1', password='pass')
        res = self.client.get(reverse('app:question_detail', kwargs={'pk': jp_q.pk}), follow=True)
        self.assertContains(res, "exclusive to Zenken Enrolled Students")

    def test_leaderboard_and_streaks(self):
        streak, _ = UserActivityStreak.objects.get_or_create(student=self.zenken_student)
        streak.record_activity(points=50, is_quiz=True)

        self.client.login(username='zenken1', password='pass')
        res = self.client.get(reverse('app:leaderboard'))
        self.assertEqual(res.status_code, 200)
        self.assertContains(res, "Arena Leaderboard &amp; Streak Board")
        self.assertContains(res, "50")

    def test_topic_wise_practice_room(self):
        AptitudeQuestion.objects.create(
            teacher=self.teacher,
            title='Sample Topic Q',
            subject='APTITUDE',
            topic='PERCENTAGE',
            difficulty='EASY',
            access_tier='ALL',
            question_text='What is 10% of 100?',
            option_a='5', option_b='10', option_c='15', option_d='20',
            correct_option='B',
        )

        self.client.login(username='nonzenken1', password='pass')
        res = self.client.get(reverse('app:topic_practice_rooms'))
        self.assertEqual(res.status_code, 200)
        self.assertContains(res, "Topic-Wise Practice Rooms")

        res_room = self.client.get(reverse('app:topic_room_practice', kwargs={'topic_code': 'PERCENTAGE'}))
        self.assertEqual(res_room.status_code, 200)
        self.assertContains(res_room, "What is 10% of 100?")

    def test_weekly_newsletter(self):
        nl = WeeklyNewsletter.objects.create(
            title='Issue 1: Test Playbook',
            issue_number=1,
            author=self.teacher,
            content='Weekly test content',
            placement_strategies='Strategy 101',
            job_market_requirements='React & Python',
        )
        self.client.login(username='nonzenken1', password='pass')
        res = self.client.get(reverse('app:newsletter_list'))
        self.assertEqual(res.status_code, 200)
        self.assertContains(res, 'Issue #1')

    def test_opportunities(self):
        opp = Opportunity.objects.create(
            company_name='Rakuten Group',
            role_title='Associate Software Engineer',
            opportunity_type='FULL_TIME',
            apply_url='https://example.com/apply',
            eligibility='2026 Batch',
            posted_by=self.teacher,
        )
        self.client.login(username='nonzenken1', password='pass')
        res = self.client.get(reverse('app:opportunity_list'))
        self.assertEqual(res.status_code, 200)
        self.assertContains(res, 'Rakuten Group')

    def test_quiz_with_anti_cheat_violations_logged(self):
        q = AptitudeQuestion.objects.create(
            teacher=self.teacher,
            title='Speed Problem',
            subject='APTITUDE',
            topic='SPEED_DISTANCE',
            difficulty='EASY',
            access_tier='ALL',
            question_text='Speed = 60 km/h. Distance in 2 hrs?',
            option_a='100 km', option_b='120 km', option_c='140 km', option_d='160 km',
            correct_option='B',
        )
        quiz = Quiz.objects.create(
            teacher=self.teacher,
            title='Speed Quiz 20Q',
            quiz_type='APTITUDE',
            duration_minutes=20,
            pass_percentage=50,
            is_published=True,
        )
        quiz.questions.add(q)

        self.client.login(username='nonzenken1', password='pass')
        take_url = reverse('app:quiz_take', kwargs={'pk': quiz.pk})
        # Simulate test submission with 1 tab switch violation logged by anti-cheat
        res = self.client.post(take_url, {f'q_{q.pk}': 'B', 'time_taken': 60, 'tab_switch_violations': 1}, follow=True)
        self.assertEqual(res.status_code, 200)

        attempt = QuizAttempt.objects.filter(student=self.non_zenken_student, quiz=quiz).first()
        self.assertIsNotNone(attempt)
        self.assertEqual(attempt.tab_switch_violations, 1)
        self.assertEqual(attempt.total_questions, 20)
