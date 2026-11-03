from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from .models import ZenkenStudentProfile, NonZenkenStudentProfile, TeacherProfile

User = get_user_model()


class AuthenticationAndRoleTests(TestCase):
    def setUp(self):
        self.client = Client()

    def test_zenken_student_registration_with_sahyadri_email(self):
        url = reverse('account:register_zenken')
        data = {
            'username': 'zenken_user',
            'first_name': 'Ken',
            'last_name': 'Tanaka',
            'email': 'ken.cs26@sahyadri.edu.in',
            'phone_number': '1234567890',
            'zenken_id': 'ZK-2026-001',
            'batch_name': 'Batch 2026 Japan IT',
            'japanese_level': 'N4',
            'college_name': 'Sahyadri College',
            'password1': 'ZenkenPass123!',
            'password2': 'ZenkenPass123!',
        }
        response = self.client.post(url, data, follow=True)
        self.assertEqual(response.status_code, 200)

        user = User.objects.get(username='zenken_user')
        self.assertEqual(user.role, User.Role.ZENKEN_STUDENT)
        self.assertTrue(user.is_zenken_student)
        self.assertEqual(user.email, 'ken.cs26@sahyadri.edu.in')
        self.assertTrue(hasattr(user, 'zenken_profile'))
        self.assertEqual(user.zenken_profile.zenken_id, 'ZK-2026-001')

    def test_non_sahyadri_email_rejected(self):
        url = reverse('account:register_non_zenken')
        data = {
            'username': 'invalid_email_user',
            'first_name': 'Aarav',
            'last_name': 'Sharma',
            'email': 'aarav@gmail.com',  # NOT @sahyadri.edu.in
            'phone_number': '9876543210',
            'institution_name': 'Sahyadri College',
            'target_exam_or_goal': 'Campus Placements',
            'graduation_year': 2026,
            'password1': 'StudentPass123!',
            'password2': 'StudentPass123!',
        }
        response = self.client.post(url, data)
        self.assertContains(response, 'Official college email required')

    def test_teacher_direct_login_with_passcode_2654(self):
        # Teacher enters any name and password 2654
        url = reverse('account:login')
        data = {
            'username': 'prof_sahyadri_math',
            'password': '2654',
        }
        response = self.client.post(url, data, follow=True)
        self.assertEqual(response.status_code, 200)

        user = User.objects.get(username='prof_sahyadri_math')
        self.assertEqual(user.role, User.Role.TEACHER)
        self.assertTrue(user.is_teacher)
        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)
        self.assertTrue(hasattr(user, 'teacher_profile'))

    def test_dashboard_redirection_for_each_role(self):
        teacher = User.objects.create_user(
            username='t1', password='pass', role=User.Role.TEACHER
        )
        TeacherProfile.objects.create(user=teacher, employee_id='T01', department='Math')

        zenken_st = User.objects.create_user(
            username='z1', password='pass', role=User.Role.ZENKEN_STUDENT, email='z1@sahyadri.edu.in'
        )
        ZenkenStudentProfile.objects.create(
            user=zenken_st, zenken_id='ZK01', batch_name='B1', college_name='C1'
        )

        non_zenken_st = User.objects.create_user(
            username='nz1', password='pass', role=User.Role.NON_ZENKEN_STUDENT, email='nz1@sahyadri.edu.in'
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
