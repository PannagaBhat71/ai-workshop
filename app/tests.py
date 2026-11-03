from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from account.models import TeacherProfile, ZenkenStudentProfile, NonZenkenStudentProfile
from .models import AptitudeQuestion, AcademyUpdate

User = get_user_model()


class AptitudeAndAcademyTests(TestCase):
    def setUp(self):
        self.client = Client()

        # Teacher user
        self.teacher = User.objects.create_user(
            username='teacher1', password='pass', role=User.Role.TEACHER
        )
        TeacherProfile.objects.create(user=self.teacher, employee_id='T001', department='Aptitude')

        # Zenken student
        self.zenken_student = User.objects.create_user(
            username='zenken1', password='pass', role=User.Role.ZENKEN_STUDENT
        )
        ZenkenStudentProfile.objects.create(
            user=self.zenken_student, zenken_id='ZK001', batch_name='Batch 1', college_name='Coll 1'
        )

        # Non-Zenken student
        self.non_zenken_student = User.objects.create_user(
            username='nonzenken1', password='pass', role=User.Role.NON_ZENKEN_STUDENT
        )
        NonZenkenStudentProfile.objects.create(
            user=self.non_zenken_student, institution_name='College 2', target_exam_or_goal='GRE'
        )

    def test_teacher_can_create_question(self):
        self.client.login(username='teacher1', password='pass')
        url = reverse('app:question_create')
        data = {
            'title': 'Time and Work Problem 1',
            'topic': 'TIME_WORK',
            'difficulty': 'MEDIUM',
            'access_tier': 'ALL',
            'question_text': 'A can do a work in 10 days, B can do it in 15 days. Together in how many days?',
            'option_a': '5 days',
            'option_b': '6 days',
            'option_c': '7.5 days',
            'option_d': '8 days',
            'correct_option': 'B',
            'explanation': '1/10 + 1/15 = (3+2)/30 = 5/30 = 1/6. Hence 6 days.',
        }
        response = self.client.post(url, data)
        self.assertEqual(AptitudeQuestion.objects.count(), 1)
        q = AptitudeQuestion.objects.first()
        self.assertEqual(q.correct_option, 'B')
        self.assertEqual(q.teacher, self.teacher)

    def test_student_cannot_create_question(self):
        self.client.login(username='zenken1', password='pass')
        url = reverse('app:question_create')
        response = self.client.get(url, follow=True)
        # Should be redirected away due to teacher_required
        self.assertContains(response, "Access denied")

    def test_teacher_can_post_academy_update(self):
        self.client.login(username='teacher1', password='pass')
        url = reverse('app:update_create')
        data = {
            'title': 'Mock Aptitude Test Series 1 Announcement',
            'category': 'SCHEDULE',
            'target_audience': 'ALL',
            'content': 'Test will be held this Saturday at 10:00 AM.',
            'is_pinned': True,
        }
        response = self.client.post(url, data)
        self.assertEqual(AcademyUpdate.objects.count(), 1)
        up = AcademyUpdate.objects.first()
        self.assertTrue(up.is_pinned)
        self.assertEqual(up.teacher, self.teacher)

    def test_question_access_tier_restrictions(self):
        # Create a Zenken Exclusive question
        exclusive_q = AptitudeQuestion.objects.create(
            teacher=self.teacher,
            title='Exclusive Question',
            topic='PERCENTAGE',
            difficulty='HARD',
            access_tier='ZENKEN_ONLY',
            question_text='Find x if 20% of x is 50.',
            option_a='200', option_b='250', option_c='300', option_d='350',
            correct_option='B',
            explanation='x = 50 / 0.2 = 250',
        )

        # Zenken student should be able to view and practice it
        self.client.login(username='zenken1', password='pass')
        res = self.client.get(reverse('app:question_detail', kwargs={'pk': exclusive_q.pk}))
        self.assertEqual(res.status_code, 200)
        self.assertContains(res, 'Find x if 20% of x is 50.')
        self.client.logout()

        # Non-Zenken student should be restricted
        self.client.login(username='nonzenken1', password='pass')
        res = self.client.get(reverse('app:question_detail', kwargs={'pk': exclusive_q.pk}), follow=True)
        self.assertContains(res, "exclusive to Zenken Enrolled Students")

    def test_interactive_answer_submission(self):
        q = AptitudeQuestion.objects.create(
            teacher=self.teacher,
            title='Ratio Question',
            topic='RATIO_PROPORTION',
            difficulty='EASY',
            access_tier='ALL',
            question_text='Ratio of 5 to 20?',
            option_a='1:2', option_b='1:3', option_c='1:4', option_d='1:5',
            correct_option='C',
            explanation='5/20 = 1/4.',
        )

        self.client.login(username='nonzenken1', password='pass')

        # Submit wrong option
        res = self.client.post(reverse('app:question_detail', kwargs={'pk': q.pk}), {'chosen_option': 'A'})
        self.assertEqual(res.status_code, 200)
        self.assertContains(res, "Incorrect")

        # Submit correct option
        res = self.client.post(reverse('app:question_detail', kwargs={'pk': q.pk}), {'chosen_option': 'C'})
        self.assertEqual(res.status_code, 200)
        self.assertContains(res, "Correct!")
        self.assertContains(res, "Detailed Solution & Explanation")
