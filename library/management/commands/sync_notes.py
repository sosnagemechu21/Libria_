"""
Management command to sync chapter metadata from Books/Notes/ into the database.
Run: python manage.py sync_notes
"""
import os
import re
from django.core.management.base import BaseCommand
from django.conf import settings
from library.models import Grade, Subject, Textbook, Chapter

SUBJECT_METADATA = {
    'biology': {'name': 'Biology', 'icon': '🧬', 'color': '#10B981'},
    'chemistry': {'name': 'Chemistry', 'icon': '🧪', 'color': '#F59E0B'},
    'physics': {'name': 'Physics', 'icon': '⚛️', 'color': '#8B5CF6'},
    'mathematics': {'name': 'Mathematics', 'icon': '📐', 'color': '#3B82F6'},
    'english': {'name': 'English', 'icon': '📖', 'color': '#EF4444'},
    'history': {'name': 'History', 'icon': '🏛️', 'color': '#92400E'},
    'geography': {'name': 'Geography', 'icon': '🌍', 'color': '#059669'},
    'economics': {'name': 'Economics', 'icon': '📊', 'color': '#7C3AED'},
    'information_technology': {'name': 'Information Technology', 'icon': '💻', 'color': '#0EA5E9'},
    'citizenship_education': {'name': 'Citizenship Education', 'icon': '🏛', 'color': '#6366F1'},
    'agriculture': {'name': 'Agriculture', 'icon': '🌱', 'color': '#22C55E'},
}

class Command(BaseCommand):
    help = 'Syncs chapter notes from Books/Notes/ into the database'

    def handle(self, *args, **options):
        notes_base = os.path.join(settings.BASE_DIR, 'Books', 'Notes')
        if not os.path.exists(notes_base):
            self.stdout.write(self.style.ERROR(f"Directory not found: {notes_base}"))
            return

        total_synced = 0
        for root, dirs, files in os.walk(notes_base):
            txt_files = [f for f in files if f.startswith('Chapter_') and f.endswith('.txt')]
            if not txt_files:
                continue

            rel_path = os.path.relpath(root, notes_base)
            parts = rel_path.split(os.sep)

            grade_num = None
            sub_slug = None

            if parts[0].startswith('Grade_'):
                grade_num = int(parts[0].split('_')[1])
                sub_slug = parts[-1]
            elif '_Grade_' in parts[0]:
                match = re.match(r'([A-Za-z]+)_Grade_(\d+)', parts[0])
                if match:
                    sub_slug = match.group(1).lower()
                    grade_num = int(match.group(2))

            if not grade_num or not sub_slug:
                continue

            meta = SUBJECT_METADATA.get(sub_slug, {
                'name': sub_slug.replace('_', ' ').title(),
                'icon': '📚',
                'color': '#4B7BE5'
            })

            grade_obj, _ = Grade.objects.get_or_create(number=grade_num, defaults={
                'label': f'Grade {grade_num}',
                'cover_color': '#4B7BE5'
            })

            subject_obj, _ = Subject.objects.get_or_create(
                name=meta['name'],
                grade=grade_obj,
                defaults={
                    'slug': sub_slug.replace('_', '-'),
                    'icon': meta['icon'],
                    'color': meta['color'],
                    'description': f'{meta["name"]} for Grade {grade_num}'
                }
            )

            textbook_obj, _ = Textbook.objects.get_or_create(
                subject=subject_obj,
                grade=grade_obj,
                curriculum_type='new',
                defaults={
                    'title': f'Grade {grade_num} {meta["name"]} Student Textbook (New Curriculum)',
                    'publisher': 'MoE, Ethiopia',
                    'year': 2023,
                    'is_available': True
                }
            )

            for tf in txt_files:
                m = re.match(r'Chapter_(\d+)\.txt', tf)
                if not m:
                    continue
                ch_num = int(m.group(1))
                ch_path = os.path.join(root, tf)

                title = f"Chapter {ch_num}"
                page_start = 0
                page_end = 0
                try:
                    with open(ch_path, 'r', encoding='utf-8') as f:
                        lines = [f.readline() for _ in range(6)]
                        for l in lines:
                            if l.startswith(f"Chapter {ch_num}:"):
                                title = l.split(f"Chapter {ch_num}:", 1)[1].strip()
                            elif l.startswith("Pages:"):
                                pm = re.search(r'(\d+)\s+to\s+(\d+)', l)
                                if pm:
                                    page_start = int(pm.group(1))
                                    page_end = int(pm.group(2))
                except Exception:
                    pass

                Chapter.objects.update_or_create(
                    textbook=textbook_obj,
                    number=ch_num,
                    defaults={
                        'title': title,
                        'page_start': page_start,
                        'page_end': page_end,
                    }
                )
                total_synced += 1

        self.stdout.write(self.style.SUCCESS(f"Successfully synced {total_synced} chapters into database."))
