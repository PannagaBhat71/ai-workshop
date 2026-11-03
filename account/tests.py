from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from .models import ZenkenStudentProfile, NonZenkenStudentProfile, TeacherProfile

User = get_user_model()


class AuthenticationAndRoleTests(TestCase):
    def setUp(self):
        self.client = Client()

    def test_zenken_student_registration(self):
        url = reverse('account:register_zenken')
        data = {
            'username': 'zenken_user',
            'first_name': 'Ken',
            'last_name': 'Tanaka',
            'email': 'ken@example.com',
            'phone_number': '1234567890',
            'zenken_id': 'ZK-2026-001',
            'batch_name': 'Batch 2026 Japan IT',
            'japanese_level': 'N4',
            'college_name': 'Engineering College',
            'password1': 'ZenkenPass123!',
            'password2': 'ZenkenPass123!',
        }
        response = self.client.post(url, data, follow=True)
        self.assertEqual(response.status_code, 200)

        user = User.objects.get(username='zenken_user')
        self.assertEqual(user.role, User.Role.ZENKEN_STUDENT)
        self.assertTrue(user.is_zenken_student)
        self.assertFalse(user.is_teacher)
        self.assertTrue(hasattr(user, 'zenken_profile'))
        self.assertEqual(user.zenken_profile.zenken_id, 'ZK-2026-001')
        self.assertEqual(user.zenken_profile.japanese_level, 'N4')

    def test_non_zenken_student_registration(self):
        url = reverse('account:register_non_zenken')
        data = {
            'username': 'external_user',
            'first_name': 'Aarav',
            'last_name': 'Sharma',
            'email': 'aarav@example.com',
            'phone_number': '9876543210',
            'institution_name': 'City Tech University',
            'target_exam_or_goal': 'Campus Placements & GATE',
            'graduation_year': 2026,
            'password1': 'StudentPass123!',
            'password2': 'StudentPass123!',
        }
        response = self.client.post(url, data, follow=True)
        self.assertEqual(response.status_code, 200)

        user = User.objects.get(username='external_user')
        self.assertEqual(user.role, User.Role.NON_ZENKEN_STUDENT)
        self.assertTrue(user.is_non_zenken_student)
        self.assertTrue(hasattr(user, 'non_zenken_profile'))
        self.assertEqual(user.non_zenken_profile.institution_name, 'City Tech University')

    def test_teacher_registration(self):
        url = reverse('account:register_teacher')
        data = {
            'username': 'prof_aptitude',
            'first_name': 'Ramesh',
            'last_name': 'Kumar',
            'email': 'ramesh@zenken-academy.com',
            'phone_number': '9988776655',
            'employee_id': 'TCH-QA-099',
            'department': 'Quantitative Aptitude & Placement',
            'qualification': 'M.Sc Applied Mathematics',
            'bio': 'Aptitude mentor with 10+ years experience.',
            'password1': 'TeacherPass123!',
            'password2': 'TeacherPass123!',
        }
        response = self.client.post(url, data, follow=True)
        self.assertEqual(response.status_code, 200)

        user = User.objects.get(username='prof_aptitude')
        self.assertEqual(user.role, User.Role.TEACHER)
        self.assertTrue(user.is_teacher)
        self.assertTrue(hasattr(user, 'teacher_profile'))
        self.assertEqual(user.teacher_profile.employee_id, 'TCH-QA-099')

    def test_dashboard_redirection_for_each_role(self):
        # Create 3 users
        teacher = User.objects.create_user(
            username='t1', password='pass', role=User.Role.TEACHER
        )
        TeacherProfile.objects.create(user=teacher, employee_id='T01', department='Math')

        zenken_st = User.objects.create_user(
            username='z1', password='pass', role=User.Role.ZENKEN_STUDENT
        )
        ZenkenStudentProfile.objects.create(
            user=zenken_st, zenken_id='ZK01', batch_name='B1', college_name='C1'
        )

        non_zenken_st = User.objects.create_user(
            username='nz1', password='pass', role=User.Role.NON_ZENKEN_STUDENT
        )
        NonZenkenStudentProfile.objects.create(
            user=non_zenken_st, institution_name='Univ1', target_exam_or_goal='CAT'
        )

        # Login as teacher -> redirects to teacher dashboard
        self.client.login(username='t1', password='pass')
        res = self.client.get(reverse('account:dashboard'))
        self.assertRedirects(res, reverse('app:teacher_dashboard'))
        self.client.logout()

        # Login as Zenken student -> redirects to zenken dashboard
        self.client.login(username='z1', password='pass')
        res = self.client.get(reverse('account:dashboard'))
        self.assertRedirects(res, reverse('app:zenken_dashboard'))
        self.client.logout()

        # Login as Non-Zenken student -> redirects to non-zenken dashboard
        self.client.login(username='nz1', password='pass')
        res = self.client.get(reverse('account:dashboard'))
        self.assertRedirects(res, reverse('app:non_zenken_dashboard'))
        self.client.logout()
