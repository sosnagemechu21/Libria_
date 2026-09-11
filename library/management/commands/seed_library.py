"""
Management command to seed the library with Grade 9-12 Ethiopian textbook metadata.
Run: python manage.py seed_library
"""
from django.core.management.base import BaseCommand
from django.utils.text import slugify
from library.models import Grade, Subject, Textbook

LIBRARY_DATA = {
    9: {
        'color': '#4B7BE5',
        'subjects': [
            {'name': 'Mathematics', 'icon': '📐', 'color': '#3B82F6', 'books': [
                {'title': 'Grade 9 Mathematics Student Textbook (New Curriculum)',
                 'curriculum': 'new', 'type': 'student', 'pages': 375, 'chapters': 9,
                 'desc': 'Covers sets, algebra, geometry, trigonometry, vectors, and probability.',
                 'kehulum': 'https://kehulum.com/student-textbook/new/grade-9/mathematics',
                 'cover': 'https://kehulum.com/up_asset/b/301/kehulum1700104401bc719d0c41.png'},
                {'title': 'Grade 9 Mathematics Student Textbook (Old Curriculum)',
                 'curriculum': 'old', 'type': 'student', 'pages': 280, 'chapters': 7,
                 'desc': 'Old curriculum Grade 9 Mathematics textbook.',
                 'kehulum': 'https://kehulum.com/student-textbook/old/grade-9/mathimatics',
                 'cover': 'https://kehulum.com/ups_asset/b/384/kehulumcom-1754573315cb4206c742.png'},
            ]},
            {'name': 'Physics', 'icon': '⚛️', 'color': '#8B5CF6', 'books': [
                {'title': 'Grade 9 Physics Student Textbook (New Curriculum)',
                 'curriculum': 'new', 'type': 'student', 'pages': 183, 'chapters': 7,
                 'desc': 'Covers motion, forces, energy, waves, and electricity.',
                 'kehulum': 'https://kehulum.com/student-textbook/new/grade-9/physics',
                 'cover': 'https://kehulum.com/up_asset/b/302/kehulum1700104626b8ce08725a.png'},
                {'title': 'Grade 9 Physics Student Textbook (Old Curriculum)',
                 'curriculum': 'old', 'type': 'student', 'pages': 180, 'chapters': 6,
                 'desc': 'Old curriculum Grade 9 Physics textbook.',
                 'kehulum': 'https://kehulum.com/student-textbook/old/grade-9/physics',
                 'cover': 'https://kehulum.com/ups_asset/b/380/kehulumcom-17545779351ef74e4da0.png'},
            ]},
            {'name': 'Biology', 'icon': '🧬', 'color': '#10B981', 'books': [
                {'title': 'Grade 9 Biology Student Textbook (New Curriculum)',
                 'curriculum': 'new', 'type': 'student', 'pages': 171, 'chapters': 6,
                 'desc': 'Covers cell biology, genetics, evolution, ecology.',
                 'kehulum': 'https://kehulum.com/student-textbook/new/grade-9/biology',
                 'cover': 'https://kehulum.com/up_asset/b/292/kehulum1700066941b553ce998a.png'},
                {'title': 'Grade 9 Biology Student Textbook (Old Curriculum)',
                 'curriculum': 'old', 'type': 'student', 'pages': 160, 'chapters': 6,
                 'desc': 'Old curriculum Grade 9 Biology textbook.',
                 'kehulum': 'https://kehulum.com/student-textbook/old/grade-9/biology',
                 'cover': 'https://kehulum.com/ups_asset/b/381//kehulumcom173416280088f51c0958.webp'},
            ]},
            {'name': 'Chemistry', 'icon': '🧪', 'color': '#F59E0B', 'books': [
                {'title': 'Grade 9 Chemistry Student Textbook (New Curriculum)',
                 'curriculum': 'new', 'type': 'student', 'pages': 183, 'chapters': 5,
                 'desc': 'Covers atomic structure, periodic table, chemical bonding, reactions.',
                 'kehulum': 'https://kehulum.com/student-textbook/new/grade-9/chemistry',
                 'cover': 'https://kehulum.com/up_asset/b/293/kehulum1700067193038199a456.png'},
            ]},
            {'name': 'English', 'icon': '📖', 'color': '#EF4444', 'books': [
                {'title': 'Grade 9 English for Ethiopia Student Textbook (New Curriculum)',
                 'curriculum': 'new', 'type': 'student', 'pages': 200, 'chapters': 10,
                 'desc': '10 themed units with grammar, vocabulary, reading, writing, and listening.',
                 'kehulum': 'https://kehulum.com/student-textbook/new/grade-9/english-for-ethiopia',
                 'cover': 'https://kehulum.com/up_asset/b/296/kehulum17001026849986a7fb61.png'},
            ]},
            {'name': 'Amharic', 'icon': '🇪🇹', 'color': '#06B6D4', 'books': [
                {'title': 'Grade 9 Amharic Student Textbook (New Curriculum)',
                 'curriculum': 'new', 'type': 'student', 'pages': 175, 'chapters': 9,
                 'desc': 'አዲሱ ካሪኩለም አማርኛ ቋንቋ የተማሪ መጽሐፍ - 9 units.',
                 'kehulum': 'https://kehulum.com/student-textbook/new/grade-9/amharic',
                 'cover': 'https://kehulum.com/up_asset/b/291/kehulum17000662613aa345e0e0.png'},
            ]},
            {'name': 'History', 'icon': '🏛️', 'color': '#92400E', 'books': [
                {'title': 'Grade 9 History Student Textbook (New Curriculum)',
                 'curriculum': 'new', 'type': 'student', 'pages': 219, 'chapters': 9,
                 'desc': 'Ethiopian and world history from ancient civilizations.',
                 'kehulum': 'https://kehulum.com/student-textbook/new/grade-9/history',
                 'cover': 'https://kehulum.com/up_asset/b/298/kehulum1700103684e5f04496f8.png'},
            ]},
            {'name': 'Geography', 'icon': '🌍', 'color': '#059669', 'books': [
                {'title': 'Grade 9 Geography Student Textbook (New Curriculum)',
                 'curriculum': 'new', 'type': 'student', 'pages': 237, 'chapters': 8,
                 'desc': 'Physical and human geography, maps, population, and environment.',
                 'kehulum': 'https://kehulum.com/student-textbook/new/grade-9/geography',
                 'cover': 'https://kehulum.com/up_asset/b/297/kehulum1700103242374050debf.png'},
            ]},
            {'name': 'Economics', 'icon': '📊', 'color': '#7C3AED', 'books': [
                {'title': 'Grade 9 Economics Student Textbook (New Curriculum)',
                 'curriculum': 'new', 'type': 'student', 'pages': 119, 'chapters': 8,
                 'desc': 'Fundamentals of economics, markets, supply and demand.',
                 'kehulum': 'https://kehulum.com/student-textbook/new/grade-9/economics',
                 'cover': 'https://kehulum.com/up_asset/b/295/kehulum1700073874846cdfbb7d.png'},
            ]},
            {'name': 'Information Technology', 'icon': '💻', 'color': '#0EA5E9', 'books': [
                {'title': 'Grade 9 Information Technology Student Textbook (New Curriculum)',
                 'curriculum': 'new', 'type': 'student', 'pages': 251, 'chapters': 6,
                 'desc': 'Computer fundamentals, software, networking, and digital literacy.',
                 'kehulum': 'https://kehulum.com/student-textbook/new/grade-9/information-technology',
                 'cover': 'https://kehulum.com/up_asset/b/300/kehulum170010415376a86f4221.png'},
            ]},
            {'name': 'Health and Physical Education', 'icon': '🏃', 'color': '#F97316', 'books': [
                {'title': 'Grade 9 HPE Student Textbook (New Curriculum)',
                 'curriculum': 'new', 'type': 'student', 'pages': 167, 'chapters': 8,
                 'desc': 'Health, nutrition, physical fitness, and sports education.',
                 'kehulum': 'https://kehulum.com/student-textbook/new/grade-9/health-and-physical-education-hpe',
                 'cover': 'https://kehulum.com/up_asset/b/299/kehulum170010391438d023fa86.png'},
            ]},
            {'name': 'Citizenship Education', 'icon': '⚖️', 'color': '#6366F1', 'books': [
                {'title': 'Grade 9 Citizenship Education Student Textbook (New Curriculum)',
                 'curriculum': 'new', 'type': 'student', 'pages': 173, 'chapters': 8,
                 'desc': 'Civic responsibility, rights, democracy, and ethics.',
                 'kehulum': 'https://kehulum.com/student-textbook/new/grade-9/citizenship-education',
                 'cover': 'https://kehulum.com/up_asset/b/294/kehulum17000736174cd3a40c79.png'},
            ]},
        ]
    },
    10: {
        'color': '#10B981',
        'subjects': [
            {'name': 'Mathematics', 'icon': '📐', 'color': '#3B82F6', 'books': [
                {'title': 'Grade 10 Mathematics Student Textbook (New Curriculum)',
                 'curriculum': 'new', 'type': 'student', 'pages': 380, 'chapters': 9,
                 'desc': 'Advanced algebra, trigonometry, statistics, and probability.',
                 'kehulum': 'https://kehulum.com/student-textbook/new/grade-10/mathematics',
                 'cover': 'https://kehulum.com/ups_asset/b/91/kehulumcom-1753863269f1780b1ff8.png'},
            ]},
            {'name': 'Physics', 'icon': '⚛️', 'color': '#8B5CF6', 'books': [
                {'title': 'Grade 10 Physics Student Textbook (New Curriculum)',
                 'curriculum': 'new', 'type': 'student', 'pages': 200, 'chapters': 7,
                 'desc': 'Mechanics, thermodynamics, optics, and electromagnetism.',
                 'kehulum': 'https://kehulum.com/student-textbook/new/grade-10/physics',
                 'cover': 'https://kehulum.com/ups_asset/b/106/kehulumcom-175386331911b0915925.png'},
            ]},
            {'name': 'Biology', 'icon': '🧬', 'color': '#10B981', 'books': [
                {'title': 'Grade 10 Biology Student Textbook (New Curriculum)',
                 'curriculum': 'new', 'type': 'student', 'pages': 195, 'chapters': 7,
                 'desc': 'Human body systems, reproduction, genetics and heredity.',
                 'kehulum': 'https://kehulum.com/student-textbook/new/grade-10/biology',
                 'cover': 'https://kehulum.com/ups_asset/b/106/kehulumcom-175386331911b0915925.png'},
            ]},
            {'name': 'Chemistry', 'icon': '🧪', 'color': '#F59E0B', 'books': [
                {'title': 'Grade 10 Chemistry Student Textbook (New Curriculum)',
                 'curriculum': 'new', 'type': 'student', 'pages': 210, 'chapters': 6,
                 'desc': 'Chemical equilibrium, acids and bases, electrochemistry.',
                 'kehulum': 'https://kehulum.com/student-textbook/new/grade-10/chemistry',
                 'cover': 'https://kehulum.com/ups_asset/b/106/kehulumcom-175386331911b0915925.png'},
            ]},
            {'name': 'English', 'icon': '📖', 'color': '#EF4444', 'books': [
                {'title': 'Grade 10 English for Ethiopia Student Textbook (New Curriculum)',
                 'curriculum': 'new', 'type': 'student', 'pages': 210, 'chapters': 10,
                 'desc': 'Advanced reading comprehension, writing, grammar, and literature.',
                 'kehulum': 'https://kehulum.com/student-textbook/new/grade-10/english-for-ethiopia',
                 'cover': 'https://kehulum.com/ups_asset/b/106/kehulumcom-175386331911b0915925.png'},
            ]},
            {'name': 'Amharic', 'icon': '🇪🇹', 'color': '#06B6D4', 'books': [
                {'title': 'Grade 10 Amharic Student Textbook (New Curriculum)',
                 'curriculum': 'new', 'type': 'student', 'pages': 180, 'chapters': 9,
                 'desc': 'Grade 10 Amharic language and literature.',
                 'kehulum': 'https://kehulum.com/student-textbook/new/grade-10/amharic',
                 'cover': 'https://kehulum.com/ups_asset/b/106/kehulumcom-175386331911b0915925.png'},
            ]},
            {'name': 'History', 'icon': '🏛️', 'color': '#92400E', 'books': [
                {'title': 'Grade 10 History Student Textbook (New Curriculum)',
                 'curriculum': 'new', 'type': 'student', 'pages': 230, 'chapters': 9,
                 'desc': 'Modern Ethiopian and world history.',
                 'kehulum': 'https://kehulum.com/student-textbook/new/grade-10/history',
                 'cover': 'https://kehulum.com/ups_asset/b/106/kehulumcom-175386331911b0915925.png'},
            ]},
            {'name': 'Geography', 'icon': '🌍', 'color': '#059669', 'books': [
                {'title': 'Grade 10 Geography Student Textbook (New Curriculum)',
                 'curriculum': 'new', 'type': 'student', 'pages': 240, 'chapters': 8,
                 'desc': 'Economic geography, natural resources, and development.',
                 'kehulum': 'https://kehulum.com/student-textbook/new/grade-10/geography',
                 'cover': 'https://kehulum.com/ups_asset/b/106/kehulumcom-175386331911b0915925.png'},
            ]},
            {'name': 'Economics', 'icon': '📊', 'color': '#7C3AED', 'books': [
                {'title': 'Grade 10 Economics Student Textbook (New Curriculum)',
                 'curriculum': 'new', 'type': 'student', 'pages': 135, 'chapters': 8,
                 'desc': 'National economy, trade, development, and financial systems.',
                 'kehulum': 'https://kehulum.com/student-textbook/new/grade-10/economics',
                 'cover': 'https://kehulum.com/ups_asset/b/106/kehulumcom-175386331911b0915925.png'},
            ]},
            {'name': 'Information Technology', 'icon': '💻', 'color': '#0EA5E9', 'books': [
                {'title': 'Grade 10 Information Technology Student Textbook (New Curriculum)',
                 'curriculum': 'new', 'type': 'student', 'pages': 260, 'chapters': 6,
                 'desc': 'Programming fundamentals, databases, internet, and security.',
                 'kehulum': 'https://kehulum.com/student-textbook/new/grade-10/information-technology',
                 'cover': 'https://kehulum.com/ups_asset/b/106/kehulumcom-175386331911b0915925.png'},
            ]},
        ]
    },
    11: {
        'color': '#F59E0B',
        'subjects': [
            {'name': 'Mathematics', 'icon': '📐', 'color': '#3B82F6', 'books': [
                {'title': 'Grade 11 Mathematics Student Textbook (New Curriculum)',
                 'curriculum': 'new', 'type': 'student', 'pages': 400, 'chapters': 10,
                 'desc': 'Calculus, functions, matrices, and advanced statistics.',
                 'kehulum': 'https://kehulum.com/student-textbook/new/grade-11/mathematics',
                 'cover': 'https://kehulum.com/ups_asset/b/91/kehulumcom-1753863269f1780b1ff8.png'},
            ]},
            {'name': 'Physics', 'icon': '⚛️', 'color': '#8B5CF6', 'books': [
                {'title': 'Grade 11 Physics Student Textbook (New Curriculum)',
                 'curriculum': 'new', 'type': 'student', 'pages': 220, 'chapters': 8,
                 'desc': 'Rotational motion, waves, quantum physics, and nuclear physics.',
                 'kehulum': 'https://kehulum.com/student-textbook/new/grade-11/physics',
                 'cover': 'https://kehulum.com/ups_asset/b/106/kehulumcom-175386331911b0915925.png'},
            ]},
            {'name': 'Biology', 'icon': '🧬', 'color': '#10B981', 'books': [
                {'title': 'Grade 11 Biology Student Textbook (New Curriculum)',
                 'curriculum': 'new', 'type': 'student', 'pages': 210, 'chapters': 8,
                 'desc': 'Biochemistry, molecular biology, and ecosystem dynamics.',
                 'kehulum': 'https://kehulum.com/student-textbook/new/grade-11/biology',
                 'cover': 'https://kehulum.com/ups_asset/b/106/kehulumcom-175386331911b0915925.png'},
            ]},
            {'name': 'Chemistry', 'icon': '🧪', 'color': '#F59E0B', 'books': [
                {'title': 'Grade 11 Chemistry Student Textbook (New Curriculum)',
                 'curriculum': 'new', 'type': 'student', 'pages': 225, 'chapters': 7,
                 'desc': 'Organic chemistry, thermochemistry, and analytical methods.',
                 'kehulum': 'https://kehulum.com/student-textbook/new/grade-11/chemistry',
                 'cover': 'https://kehulum.com/ups_asset/b/106/kehulumcom-175386331911b0915925.png'},
            ]},
            {'name': 'English', 'icon': '📖', 'color': '#EF4444', 'books': [
                {'title': 'Grade 11 English for Ethiopia Student Textbook (New Curriculum)',
                 'curriculum': 'new', 'type': 'student', 'pages': 215, 'chapters': 10,
                 'desc': 'Critical reading, academic writing, and advanced communication.',
                 'kehulum': 'https://kehulum.com/student-textbook/new/grade-11/english-for-ethiopia',
                 'cover': 'https://kehulum.com/ups_asset/b/106/kehulumcom-175386331911b0915925.png'},
            ]},
            {'name': 'History', 'icon': '🏛️', 'color': '#92400E', 'books': [
                {'title': 'Grade 11 History Student Textbook (New Curriculum)',
                 'curriculum': 'new', 'type': 'student', 'pages': 235, 'chapters': 9,
                 'desc': 'Contemporary world history, colonialism, and global issues.',
                 'kehulum': 'https://kehulum.com/student-textbook/new/grade-11/history',
                 'cover': 'https://kehulum.com/ups_asset/b/106/kehulumcom-175386331911b0915925.png'},
            ]},
            {'name': 'Geography', 'icon': '🌍', 'color': '#059669', 'books': [
                {'title': 'Grade 11 Geography Student Textbook (New Curriculum)',
                 'curriculum': 'new', 'type': 'student', 'pages': 245, 'chapters': 8,
                 'desc': 'Environmental geography, climate change, and sustainable development.',
                 'kehulum': 'https://kehulum.com/student-textbook/new/grade-11/geography',
                 'cover': 'https://kehulum.com/ups_asset/b/106/kehulumcom-175386331911b0915925.png'},
            ]},
        ]
    },
    12: {
        'color': '#EF4444',
        'subjects': [
            {'name': 'Mathematics', 'icon': '📐', 'color': '#3B82F6', 'books': [
                {'title': 'Grade 12 Mathematics Student Textbook (New Curriculum)',
                 'curriculum': 'new', 'type': 'student', 'pages': 420, 'chapters': 10,
                 'desc': 'Advanced calculus, complex numbers, and exam preparation.',
                 'kehulum': 'https://kehulum.com/student-textbook/new/grade-12/mathematics',
                 'cover': 'https://kehulum.com/ups_asset/b/91/kehulumcom-1753863269f1780b1ff8.png'},
            ]},
            {'name': 'Physics', 'icon': '⚛️', 'color': '#8B5CF6', 'books': [
                {'title': 'Grade 12 Physics Student Textbook (New Curriculum)',
                 'curriculum': 'new', 'type': 'student', 'pages': 240, 'chapters': 8,
                 'desc': 'Advanced electromagnetism, relativity, and modern physics.',
                 'kehulum': 'https://kehulum.com/student-textbook/new/grade-12/physics',
                 'cover': 'https://kehulum.com/ups_asset/b/106/kehulumcom-175386331911b0915925.png'},
            ]},
            {'name': 'Biology', 'icon': '🧬', 'color': '#10B981', 'books': [
                {'title': 'Grade 12 Biology Student Textbook (New Curriculum)',
                 'curriculum': 'new', 'type': 'student', 'pages': 225, 'chapters': 8,
                 'desc': 'Advanced genetics, biotechnology, and conservation biology.',
                 'kehulum': 'https://kehulum.com/student-textbook/new/grade-12/biology',
                 'cover': 'https://kehulum.com/ups_asset/b/106/kehulumcom-175386331911b0915925.png'},
            ]},
            {'name': 'Chemistry', 'icon': '🧪', 'color': '#F59E0B', 'books': [
                {'title': 'Grade 12 Chemistry Student Textbook (New Curriculum)',
                 'curriculum': 'new', 'type': 'student', 'pages': 240, 'chapters': 7,
                 'desc': 'Polymer chemistry, industrial chemistry, and exam prep.',
                 'kehulum': 'https://kehulum.com/student-textbook/new/grade-12/chemistry',
                 'cover': 'https://kehulum.com/ups_asset/b/106/kehulumcom-175386331911b0915925.png'},
            ]},
            {'name': 'English', 'icon': '📖', 'color': '#EF4444', 'books': [
                {'title': 'Grade 12 English for Ethiopia Student Textbook (New Curriculum)',
                 'curriculum': 'new', 'type': 'student', 'pages': 220, 'chapters': 10,
                 'desc': 'University-prep English: essays, analysis, and language mastery.',
                 'kehulum': 'https://kehulum.com/student-textbook/new/grade-12/english-for-ethiopia',
                 'cover': 'https://kehulum.com/ups_asset/b/106/kehulumcom-175386331911b0915925.png'},
            ]},
            {'name': 'History', 'icon': '🏛️', 'color': '#92400E', 'books': [
                {'title': 'Grade 12 History Student Textbook (New Curriculum)',
                 'curriculum': 'new', 'type': 'student', 'pages': 250, 'chapters': 9,
                 'desc': "Post-independence Africa, Ethiopia's modern history, global politics.",
                 'kehulum': 'https://kehulum.com/student-textbook/new/grade-12/history',
                 'cover': 'https://kehulum.com/ups_asset/b/106/kehulumcom-175386331911b0915925.png'},
            ]},
            {'name': 'Geography', 'icon': '🌍', 'color': '#059669', 'books': [
                {'title': 'Grade 12 Geography Student Textbook (New Curriculum)',
                 'curriculum': 'new', 'type': 'student', 'pages': 250, 'chapters': 8,
                 'desc': 'Global geography, urban development, and environmental crises.',
                 'kehulum': 'https://kehulum.com/student-textbook/new/grade-12/geography',
                 'cover': 'https://kehulum.com/ups_asset/b/106/kehulumcom-175386331911b0915925.png'},
            ]},
        ]
    }
}


class Command(BaseCommand):
    help = 'Seeds the library with Grade 9-12 Ethiopian textbook metadata from kehulum.com'

    def handle(self, *args, **kwargs):
        self.stdout.write('Seeding Libria library...\n')
        total_books = 0

        for grade_num, grade_data in LIBRARY_DATA.items():
            grade, created = Grade.objects.get_or_create(
                number=grade_num,
                defaults={
                    'label': f'Grade {grade_num}',
                    'cover_color': grade_data['color'],
                }
            )
            if created:
                self.stdout.write(f'  [OK] Created Grade {grade_num}')

            for order, subj_data in enumerate(grade_data['subjects']):
                slug = slugify(subj_data['name'])
                subject, created = Subject.objects.get_or_create(
                    name=subj_data['name'],
                    grade=grade,
                    defaults={
                        'slug': slug,
                        'icon': subj_data['icon'],
                        'color': subj_data['color'],
                        'order': order,
                    }
                )
                if created:
                    self.stdout.write(f'    [+] Created subject: {subj_data["name"]}')

                for book_data in subj_data['books']:
                    book, created = Textbook.objects.get_or_create(
                        title=book_data['title'],
                        grade=grade,
                        defaults={
                            'subject': subject,
                            'curriculum_type': book_data['curriculum'],
                            'book_type': book_data['type'],
                            'pages': book_data['pages'],
                            'chapters': book_data['chapters'],
                            'description': book_data['desc'],
                            'kehulum_url': book_data['kehulum'],
                            'cover_url': book_data['cover'],
                            'is_available': True,
                        }
                    )
                    if created:
                        total_books += 1
                        self.stdout.write(f'      [book] Added: {book_data["title"][:60]}...')

        self.stdout.write(self.style.SUCCESS(
            f'\nDone! Added {total_books} textbooks across Grades 9-12.'
        ))
