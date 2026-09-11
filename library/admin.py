from django.contrib import admin
from .models import Grade, Subject, Textbook, Chapter


class ChapterInline(admin.TabularInline):
    model = Chapter
    extra = 1


@admin.register(Grade)
class GradeAdmin(admin.ModelAdmin):
    list_display = ['number', 'label', 'subject_count']
    def subject_count(self, obj):
        return obj.subjects.count()
    subject_count.short_description = 'Subjects'


@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ['name', 'grade', 'icon', 'order']
    list_filter = ['grade']
    search_fields = ['name']
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Textbook)
class TextbookAdmin(admin.ModelAdmin):
    list_display = ['title', 'grade', 'subject', 'curriculum_type', 'book_type',
                    'pages', 'chapters', 'is_available']
    list_filter = ['grade', 'curriculum_type', 'book_type', 'is_available']
    search_fields = ['title', 'description']
    inlines = [ChapterInline]
    readonly_fields = ['uploaded_at', 'updated_at']
    fieldsets = (
        ('Basic Info', {
            'fields': ('title', 'subject', 'grade', 'curriculum_type', 'book_type',
                       'description', 'is_available')
        }),
        ('Content', {
            'fields': ('cover_image', 'cover_url', 'pdf_file', 'pages', 'chapters')
        }),
        ('Metadata', {
            'fields': ('publisher', 'year', 'kehulum_url', 'uploaded_at', 'updated_at')
        }),
    )


@admin.register(Chapter)
class ChapterAdmin(admin.ModelAdmin):
    list_display = ['textbook', 'number', 'title']
    list_filter = ['textbook__grade', 'textbook__subject']
    search_fields = ['title', 'textbook__title']
