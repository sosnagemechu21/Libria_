from django.db import models


CURRICULUM_CHOICES = [
    ('new', 'New Curriculum'),
    ('old', 'Old Curriculum'),
]

BOOK_TYPE_CHOICES = [
    ('student', 'Student Textbook'),
    ('teacher', "Teacher's Guide"),
]

SUBJECT_ICONS = {
    'Mathematics': '📐',
    'Physics': '⚛️',
    'Biology': '🧬',
    'Chemistry': '🧪',
    'English': '📖',
    'Amharic': '🇪🇹',
    'History': '🏛️',
    'Geography': '🌍',
    'Economics': '📊',
    'Citizenship Education': '🏛',
    'Information Technology': '💻',
    'Health and Physical Education': '🏃',
    'Civics': '⚖️',
    'General Science': '🔬',
    'Social Studies': '🌐',
}


class Grade(models.Model):
    number = models.IntegerField(unique=True)
    label = models.CharField(max_length=20)
    description = models.TextField(blank=True)
    cover_color = models.CharField(max_length=20, default='#4B7BE5')

    def __str__(self):
        return self.label

    class Meta:
        ordering = ['number']


class Subject(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100)
    icon = models.CharField(max_length=10, default='📚')
    color = models.CharField(max_length=20, default='#4B7BE5')
    grade = models.ForeignKey(Grade, on_delete=models.CASCADE, related_name='subjects')
    description = models.TextField(blank=True)
    order = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.name} (Grade {self.grade.number})"

    class Meta:
        ordering = ['order', 'name']
        unique_together = ['name', 'grade']


class Textbook(models.Model):
    title = models.CharField(max_length=255)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='textbooks')
    grade = models.ForeignKey(Grade, on_delete=models.CASCADE, related_name='textbooks')
    curriculum_type = models.CharField(max_length=10, choices=CURRICULUM_CHOICES, default='new')
    book_type = models.CharField(max_length=10, choices=BOOK_TYPE_CHOICES, default='student')
    cover_image = models.ImageField(upload_to='textbooks/covers/', blank=True, null=True)
    cover_url = models.URLField(blank=True, help_text='External cover image URL (from kehulum)')
    pdf_file = models.FileField(upload_to='textbooks/pdfs/', blank=True, null=True)
    pages = models.IntegerField(default=0)
    chapters = models.IntegerField(default=0)
    description = models.TextField(blank=True)
    kehulum_url = models.URLField(blank=True, help_text='Original source URL on kehulum.com')
    publisher = models.CharField(max_length=100, default='MoE, Ethiopia')
    year = models.IntegerField(default=2022)
    is_available = models.BooleanField(default=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.title} ({self.get_curriculum_type_display()})"

    def get_cover(self):
        if self.cover_image:
            return self.cover_image.url
        return self.cover_url or '/static/img/default_book.png'

    class Meta:
        ordering = ['grade', 'subject', 'curriculum_type']


class Chapter(models.Model):
    textbook = models.ForeignKey(Textbook, on_delete=models.CASCADE, related_name='chapter_list')
    number = models.IntegerField()
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    page_start = models.IntegerField(default=0)
    page_end = models.IntegerField(default=0)

    def __str__(self):
        return f"Chapter {self.number}: {self.title}"

    class Meta:
        ordering = ['number']
        unique_together = ['textbook', 'number']
