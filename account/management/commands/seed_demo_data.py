from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from account.models import ZenkenStudentProfile, NonZenkenStudentProfile, TeacherProfile
from app.models import AptitudeQuestion, AcademyUpdate

User = get_user_model()


class Command(BaseCommand):
    help = "Populate database with demo accounts (Teacher, Zenken Student, Non-Zenken Student), sample aptitude questions, and academy updates."

    def handle(self, *args, **options):
        self.stdout.write("Seeding demo data...")

        # 1. Create Teacher
        teacher_user, created = User.objects.get_or_create(
            username="teacher_demo",
            defaults={
                "first_name": "Prof. Kenji",
                "last_name": "Sato",
                "email": "teacher@zenken-academy.com",
                "role": User.Role.TEACHER,
                "is_staff": True,
            }
        )
        if created:
            teacher_user.set_password("teacher123")
            teacher_user.save()
            TeacherProfile.objects.create(
                user=teacher_user,
                employee_id="TCH-2026-QA01",
                department="Quantitative Aptitude & Placement Training",
                qualification="Ph.D / Master Trainer (CAT 99.9 percentile)",
                bio="Senior instructor preparing students for IT placements and Japanese corporate aptitude tests.",
            )
            self.stdout.write(self.style.SUCCESS("Created Teacher: teacher_demo / teacher123"))

        # 2. Create Zenken Student
        zenken_user, created = User.objects.get_or_create(
            username="zenken_student",
            defaults={
                "first_name": "Yuki",
                "last_name": "Nakamura",
                "email": "yuki@zenken-scholar.com",
                "role": User.Role.ZENKEN_STUDENT,
            }
        )
        if created:
            zenken_user.set_password("zenken123")
            zenken_user.save()
            ZenkenStudentProfile.objects.create(
                user=zenken_user,
                zenken_id="ZK-2026-IND-001",
                batch_name="Batch 2026 - Japan Career FastTrack",
                japanese_level="N4",
                college_name="National Institute of Technology",
            )
            self.stdout.write(self.style.SUCCESS("Created Zenken Student: zenken_student / zenken123"))

        # 3. Create Non-Zenken Student
        non_zenken_user, created = User.objects.get_or_create(
            username="external_student",
            defaults={
                "first_name": "Rohan",
                "last_name": "Verma",
                "email": "rohan.verma@example.com",
                "role": User.Role.NON_ZENKEN_STUDENT,
            }
        )
        if created:
            non_zenken_user.set_password("student123")
            non_zenken_user.save()
            NonZenkenStudentProfile.objects.create(
                user=non_zenken_user,
                institution_name="Global Institute of Technology",
                target_exam_or_goal="Campus Placements & Quantitative Aptitude",
                graduation_year=2026,
            )
            self.stdout.write(self.style.SUCCESS("Created Non-Zenken Student: external_student / student123"))

        # 4. Seed Quantitative Aptitude Questions
        questions_data = [
            {
                "title": "Combined Work Rate Problem",
                "topic": "TIME_WORK",
                "difficulty": "MEDIUM",
                "access_tier": "ALL",
                "question_text": "A can finish a piece of work in 12 days and B can do the same work in 18 days. If they work together for 4 days, what fraction of the work remains unfinished?",
                "option_a": "4/9",
                "option_b": "5/9",
                "option_c": "1/3",
                "option_d": "2/3",
                "correct_option": "A",
                "explanation": "Rate of A = 1/12 per day. Rate of B = 1/18 per day.\nCombined rate in 1 day = 1/12 + 1/18 = (3 + 2)/36 = 5/36.\nWork done in 4 days = 4 * (5/36) = 20/36 = 5/9.\nRemaining work = 1 - 5/9 = 4/9.",
            },
            {
                "title": "Successive Discount & Profit Calculation",
                "topic": "PROFIT_LOSS",
                "difficulty": "EASY",
                "access_tier": "ALL",
                "question_text": "A shopkeeper marks his goods at 25% above the cost price and allows a discount of 10% for cash payment. What is his net profit percentage?",
                "option_a": "12.5%",
                "option_b": "15%",
                "option_c": "10%",
                "option_d": "17.5%",
                "correct_option": "A",
                "explanation": "Let Cost Price (CP) = $100.\nMarked Price (MP) = $125.\nDiscount = 10% of 125 = $12.50.\nSelling Price (SP) = 125 - 12.50 = $112.50.\nProfit = 112.50 - 100 = $12.50 on $100 -> Profit % = 12.5%.",
            },
            {
                "title": "Speed, Distance & Train Crossing a Platform",
                "topic": "SPEED_DISTANCE",
                "difficulty": "MEDIUM",
                "access_tier": "ALL",
                "question_text": "A train 240 m long passes a platform of length 260 m in 25 seconds. What is the speed of the train in km/h?",
                "option_a": "54 km/h",
                "option_b": "72 km/h",
                "option_c": "60 km/h",
                "option_d": "80 km/h",
                "correct_option": "B",
                "explanation": "Total distance = length of train + length of platform = 240 + 260 = 500 m.\nTime = 25 seconds.\nSpeed in m/s = 500 / 25 = 20 m/s.\nConvert to km/h: 20 * (18/5) = 4 * 18 = 72 km/h.",
            },
            {
                "title": "Zenken Exclusive: Advanced Permutation & Combinations for Tech Interviews",
                "topic": "PROBABILITY_PERM",
                "difficulty": "HARD",
                "access_tier": "ZENKEN_ONLY",
                "question_text": "In how many ways can the letters of the word 'ZENKEN' be arranged such that both the letter 'E's are always together?",
                "option_a": "120",
                "option_b": "60",
                "option_c": "180",
                "option_d": "240",
                "correct_option": "B",
                "explanation": "Letters in 'ZENKEN': Z, E, N, K, E, N (Total 6 letters: 2 E's, 2 N's, 1 Z, 1 K).\nBundle the two 'E's as a single unit (EE).\nNow we have 5 entities: (EE), Z, N, K, N with two identical N's.\nNumber of arrangements = 5! / 2! = 120 / 2 = 60.\nSince both E's inside the bundle are identical, (EE) has only 1 internal arrangement.\nTotal distinct arrangements = 60.",
            },
        ]

        for q_data in questions_data:
            AptitudeQuestion.objects.get_or_create(
                title=q_data["title"],
                defaults={**q_data, "teacher": teacher_user}
            )
        self.stdout.write(self.style.SUCCESS(f"Seeded {len(questions_data)} Quantitative Aptitude questions."))

        # 5. Seed Academy Updates
        updates_data = [
            {
                "title": "All-India Quantitative Aptitude Mock Test - Series 1",
                "category": "SCHEDULE",
                "target_audience": "ALL",
                "is_pinned": True,
                "content": "Dear students, the first comprehensive aptitude mock test spanning Time & Work, Speed & Distance, and Percentages is scheduled for this coming Saturday at 10:00 AM. Login to your dashboard 10 minutes prior.",
            },
            {
                "title": "Zenken Japan Placement Drive & Technical Aptitude Orientation",
                "category": "ZENKEN_EXCLUSIVE",
                "target_audience": "ZENKEN_ONLY",
                "is_pinned": True,
                "content": "Exclusive notice for enrolled Zenken scholars: Orientation for the upcoming Japanese IT hiring companies (Tokyo & Osaka technical tracks) will be conducted this Friday. Please ensure your aptitude practice modules are up to date.",
            },
            {
                "title": "Open Masterclass on Short-cut Tricks for Permutations & Number Systems",
                "category": "WORKSHOP",
                "target_audience": "ALL",
                "is_pinned": False,
                "content": "A special 90-minute live problem-solving masterclass focusing on high-speed mental math and remainder theorem shortcuts will be held tomorrow at 5:00 PM. Open to all students.",
            },
        ]

        for up_data in updates_data:
            AcademyUpdate.objects.get_or_create(
                title=up_data["title"],
                defaults={**up_data, "teacher": teacher_user}
            )
        self.stdout.write(self.style.SUCCESS(f"Seeded {len(updates_data)} Academy Updates."))
        self.stdout.write(self.style.SUCCESS("All demo data seeded successfully!"))

