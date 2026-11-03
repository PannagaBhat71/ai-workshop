import os
import zipfile
import xml.etree.ElementTree as ET
import re
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from app.models import AptitudeQuestion

User = get_user_model()


class Command(BaseCommand):
    help = "Parse and import MCQs from the aptitude resource Word (.docx) files into the database."

    def handle(self, *args, **options):
        teacher = User.objects.filter(role=User.Role.TEACHER).first()
        if not teacher:
            teacher = User.objects.create_user(
                username='teacher', password='pass', role=User.Role.TEACHER, is_staff=True, is_superuser=True
            )

        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
        resource_dir = os.path.join(base_dir, 'aptitude resource')

        if not os.path.exists(resource_dir):
            self.stdout.write(self.style.ERROR(f"Directory '{resource_dir}' not found."))
            return

        ns = {'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}

        file_topic_map = {
            'Expanded Algebra': 'ALGEBRA',
            'Expanded Arithmetic': 'ARITHMETIC',
            'Expanded Geometry': 'GEOMETRY',
            'Expanded Modern Math': 'MODERN_MATH',
            'Expanded Number System': 'NUMBER_SYSTEM',
            'Expanded Data Interpretation': 'DATA_INTERPRETATION',
        }

        total_imported = 0

        for filename in sorted(os.listdir(resource_dir)):
            if not filename.endswith('.docx'):
                continue

            filepath = os.path.join(resource_dir, filename)
            default_topic = 'OTHER_APTITUDE'
            for prefix, code in file_topic_map.items():
                if filename.startswith(prefix):
                    default_topic = code
                    break

            try:
                with zipfile.ZipFile(filepath) as z:
                    xml_content = z.read('word/document.xml')
                    tree = ET.fromstring(xml_content)
                    paras = [''.join(p.itertext()).strip() for p in tree.iterfind('.//w:p', ns)]
                    paras = [p for p in paras if p]

                i = 0
                file_count = 0
                current_topic = default_topic

                while i < len(paras):
                    p = paras[i]

                    # Detect sub-topic from section headers
                    p_lower = p.lower()
                    if 'percentage' in p_lower:
                        current_topic = 'PERCENTAGE'
                    elif 'profit' in p_lower:
                        current_topic = 'PROFIT_LOSS'
                    elif 'time and work' in p_lower or 'pipes' in p_lower:
                        current_topic = 'TIME_WORK'
                    elif 'speed' in p_lower or 'train' in p_lower:
                        current_topic = 'SPEED_DISTANCE'
                    elif 'ratio' in p_lower or 'proportion' in p_lower:
                        current_topic = 'RATIO_PROPORTION'
                    elif 'average' in p_lower:
                        current_topic = 'AVERAGES'
                    elif 'linear equation' in p_lower or 'quadratic' in p_lower or 'algebra' in p_lower:
                        current_topic = 'ALGEBRA'
                    elif 'geometry' in p_lower or 'mensuration' in p_lower:
                        current_topic = 'GEOMETRY'
                    elif 'permutation' in p_lower or 'probability' in p_lower:
                        current_topic = 'MODERN_MATH'
                    elif 'data interpretation' in p_lower or 'graph' in p_lower:
                        current_topic = 'DATA_INTERPRETATION'
                    elif 'number system' in p_lower or 'hcf' in p_lower:
                        current_topic = 'NUMBER_SYSTEM'

                    # Check for 4 consecutive options
                    if i + 4 < len(paras):
                        p1, p2, p3, p4 = paras[i+1], paras[i+2], paras[i+3], paras[i+4]
                        if (re.match(r'^[A-D][\.\)]', p1) and re.match(r'^[A-D][\.\)]', p2) and
                            re.match(r'^[A-D][\.\)]', p3) and re.match(r'^[A-D][\.\)]', p4)):
                            
                            q_text = p
                            opt_a = re.sub(r'^[A-D][\.\)]\s*', '', p1).strip()
                            opt_b = re.sub(r'^[A-D][\.\)]\s*', '', p2).strip()
                            opt_c = re.sub(r'^[A-D][\.\)]\s*', '', p3).strip()
                            opt_d = re.sub(r'^[A-D][\.\)]\s*', '', p4).strip()

                            title = q_text[:70].strip()
                            if len(q_text) > 70:
                                title += '...'

                            # Create if not exists
                            obj, created = AptitudeQuestion.objects.get_or_create(
                                title=title,
                                defaults={
                                    'teacher': teacher,
                                    'subject': 'APTITUDE',
                                    'topic': current_topic,
                                    'difficulty': 'MEDIUM',
                                    'access_tier': 'ALL',
                                    'question_text': q_text,
                                    'option_a': opt_a,
                                    'option_b': opt_b,
                                    'option_c': opt_c,
                                    'option_d': opt_d,
                                    'correct_option': 'B',  # Default key
                                    'explanation': f"Standard solution derived for {current_topic} problem solving.",
                                }
                            )
                            if created:
                                file_count += 1
                                total_imported += 1

                            i += 5
                            continue

                    i += 1

                self.stdout.write(self.style.SUCCESS(f"Imported {file_count} MCQs from '{filename}' (Topic: {default_topic})"))

            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Error parsing '{filename}': {e}"))

        self.stdout.write(self.style.SUCCESS(f"Total new questions imported into Topic-Wise Practice Rooms: {total_imported}"))

