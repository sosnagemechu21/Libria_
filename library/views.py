from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Grade, Subject, Textbook


@login_required
def library_home(request):
    grades = Grade.objects.prefetch_related('subjects').all()
    return render(request, 'library/home.html', {'grades': grades})


@login_required
def grade_detail(request, grade_number):
    grade = get_object_or_404(Grade, number=grade_number)
    subjects = grade.subjects.all()
    return render(request, 'library/grade.html', {
        'grade': grade,
        'subjects': subjects,
    })


@login_required
def subject_textbooks(request, grade_number, subject_slug):
    grade = get_object_or_404(Grade, number=grade_number)
    subject = get_object_or_404(Subject, slug=subject_slug, grade=grade)
    curriculum = request.GET.get('curriculum', 'new')
    book_type = request.GET.get('type', 'student')
    textbooks = subject.textbooks.filter(
        curriculum_type=curriculum,
        book_type=book_type,
        is_available=True,
    )
    return render(request, 'library/subject.html', {
        'grade': grade,
        'subject': subject,
        'textbooks': textbooks,
        'curriculum': curriculum,
        'book_type': book_type,
    })


@login_required
def textbook_detail(request, textbook_id):
    textbook = get_object_or_404(Textbook, pk=textbook_id, is_available=True)
    chapters = textbook.chapter_list.all()
    # Related textbooks (same subject)
    related = Textbook.objects.filter(
        subject=textbook.subject,
        is_available=True
    ).exclude(pk=textbook_id)[:4]
    return render(request, 'library/textbook.html', {
        'textbook': textbook,
        'chapters': chapters,
        'related': related,
    })
