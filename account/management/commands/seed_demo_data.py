from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta
from account.models import ZenkenStudentProfile, NonZenkenStudentProfile, TeacherProfile
from app.models import (
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


class Command(BaseCommand):
    help = "Populate database with demo accounts, superuser teacher with password 2654, newsletters, opportunities, materials, and streaks."

    def handle(self, *args, **options):
        self.stdout.write("Seeding comprehensive demo data for scemquiz.arena...")

        # 1. Create Teacher Superuser (Password: 2654)
        teacher_user, _ = User.objects.get_or_create(
            username="teacher",
            defaults={
                "first_name": "Prof. Kenji",
                "last_name": "Sato",
                "email": "teacher@sahyadri.edu.in",
                "role": User.Role.TEACHER,
                "is_staff": True,
                "is_superuser": True,
            }
        )
        teacher_user.set_password("2654")
        teacher_user.is_staff = True
        teacher_user.is_superuser = True
        teacher_user.role = User.Role.TEACHER
        teacher_user.email = "teacher@sahyadri.edu.in"
        teacher_user.save()

        TeacherProfile.objects.get_or_create(
            user=teacher_user,
            defaults={
                "employee_id": "TCH-SCEM-2654",
                "department": "Quantitative Aptitude & Placement Training",
                "qualification": "Faculty Head & Placement Superuser",
                "bio": "Sahyadri Faculty and Examination Instructor.",
            }
        )
        self.stdout.write(self.style.SUCCESS("Teacher Superuser ready: username='teacher', password='2654'"))

        # 2. Create Zenken Student (@sahyadri.edu.in)
        zenken_user, _ = User.objects.get_or_create(
            username="zenken_student",
            defaults={
                "first_name": "Yuki",
                "last_name": "Nakamura",
                "email": "yuki.cs26@sahyadri.edu.in",
                "role": User.Role.ZENKEN_STUDENT,
            }
        )
        zenken_user.email = "yuki.cs26@sahyadri.edu.in"
        zenken_user.set_password("zenken123")
        zenken_user.save()
        ZenkenStudentProfile.objects.get_or_create(
            user=zenken_user,
            defaults={
                "zenken_id": "ZK-2026-IND-001",
                "batch_name": "Batch 2026 - Japan IT Placement Track",
                "japanese_level": "N4",
                "college_name": "Sahyadri College of Engineering & Management",
            }
        )

        # 3. Create Non-Zenken Student (@sahyadri.edu.in)
        non_zenken_user, _ = User.objects.get_or_create(
            username="external_student",
            defaults={
                "first_name": "Rohan",
                "last_name": "Verma",
                "email": "rohan.is26@sahyadri.edu.in",
                "role": User.Role.NON_ZENKEN_STUDENT,
            }
        )
        non_zenken_user.email = "rohan.is26@sahyadri.edu.in"
        non_zenken_user.set_password("student123")
        non_zenken_user.save()
        NonZenkenStudentProfile.objects.get_or_create(
            user=non_zenken_user,
            defaults={
                "institution_name": "Sahyadri College of Engineering & Management",
                "target_exam_or_goal": "Campus Placements & Quantitative Aptitude",
                "graduation_year": 2026,
            }
        )

        # 4. Streaks & Leaderboard Seeding
        s1, _ = UserActivityStreak.objects.get_or_create(student=zenken_user)
        s1.current_streak = 7
        s1.longest_streak = 14
        s1.total_points = 480
        s1.quizzes_completed = 6
        s1.practice_completed = 45
        s1.last_active_date = timezone.localdate()
        s1.save()

        s2, _ = UserActivityStreak.objects.get_or_create(student=non_zenken_user)
        s2.current_streak = 5
        s2.longest_streak = 9
        s2.total_points = 350
        s2.quizzes_completed = 4
        s2.practice_completed = 32
        s2.last_active_date = timezone.localdate()
        s2.save()

        # 5. Weekly Newsletter
        WeeklyNewsletter.objects.get_or_create(
            issue_number=1,
            defaults={
                "title": "Placement Playbook: Mastering Speed Arithmetic & Japanese Tech Hiring Trends",
                "author": teacher_user,
                "content": (
                    "Welcome to Issue #1 of the Sahyadri Placement & Quantitative Aptitude Weekly Digest! "
                    "This week, over 1,200 practice MCQs across Arithmetic, Geometry, Algebra, and Modern Math "
                    "have been added to the portal. In this edition, we break down high-frequency assessment questions "
                    "and review recent changes in the Japanese tech hiring landscape."
                ),
                "placement_strategies": (
                    "1. Speed Calculations: Memorize squares up to 30, cubes up to 15, and fraction-to-percentage conversions.\n"
                    "2. Elimination Technique: Always check units digit and divisibility before full multiplication.\n"
                    "3. Time Management: In 20-question tests, do not spend more than 50 seconds on a single question."
                ),
                "job_market_requirements": (
                    "• Full-Stack JavaScript/TypeScript (React + Node.js) and Python backend remain in peak demand.\n"
                    "• Japanese companies (Tokyo/Osaka tracks) specifically value JLPT N4/N3 conversational proficiency combined with solid OOP fundamentals.\n"
                    "• Core CS concepts (Data Structures, SQL query optimization, Operating Systems) are heavily weighted in tier-1 placement screenings."
                ),
            }
        )

        # 6. Opportunities
        Opportunity.objects.get_or_create(
            company_name="Rakuten Group Tokyo",
            role_title="Associate Software Development Engineer (Japan IT Track)",
            defaults={
                "opportunity_type": "JAPAN_DRIVE",
                "apply_url": "https://rakuten.careers/jobs/global-engineer-2026",
                "eligibility": "B.E / B.Tech 2026 Batch (CSE, ISE, ECE) - Min 7.0 CGPA + JLPT N4/N5 Enrolled",
                "location": "Tokyo, Japan (Full Visa Sponsorship)",
                "deadline": timezone.localdate() + timedelta(days=21),
                "description": "Full-time software engineering role in Tokyo. Training provided for Japanese corporate culture.",
                "posted_by": teacher_user,
            }
        )

        Opportunity.objects.get_or_create(
            company_name="Infosys Ltd.",
            role_title="Specialist Programmer (Power Programmer Track)",
            defaults={
                "opportunity_type": "FULL_TIME",
                "apply_url": "https://career.infosys.com/jobdesc?jobReferenceCode=SP2026",
                "eligibility": "B.E / B.Tech All Branches - No Active Backlogs, Strong DSA & Aptitude",
                "location": "Bangalore / Pune / Hyderabad",
                "deadline": timezone.localdate() + timedelta(days=14),
                "description": "Premium engineering role focusing on cloud-native systems, microservices, and AI integrations.",
                "posted_by": teacher_user,
            }
        )

        # 7. Study Material
        StudyMaterial.objects.get_or_create(
            title="Comprehensive Quantitative Aptitude Formula Cheat Sheet (All Modules)",
            defaults={
                "subject": "APTITUDE",
                "target_audience": "ALL",
                "file_url": "https://drive.google.com/file/d/sahyadri-aptitude-formulas-2026/view",
                "description": "Complete formula sheet covering Percentages, Work & Days, Train Speeds, HCF/LCM, and Algebra shortcuts.",
                "uploaded_by": teacher_user,
            }
        )

        StudyMaterial.objects.get_or_create(
            title="JLPT N4 Grammar Pattern & Keigo Business Manners Guide",
            defaults={
                "subject": "JAPANESE",
                "target_audience": "ZENKEN_ONLY",
                "file_url": "https://drive.google.com/file/d/sahyadri-zenken-jlpt-n4/view",
                "description": "Essential grammar particles, honorific forms, and Japanese IT technical email templates.",
                "uploaded_by": teacher_user,
            }
        )

        self.stdout.write(self.style.SUCCESS("All demo data seeded successfully!"))
