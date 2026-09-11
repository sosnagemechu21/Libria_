import json
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.utils import timezone
from django.conf import settings
from .models import StudySession, BreakSession, YouTubeVideoWatch
from library.models import Textbook, Chapter
import requests


@login_required
def study_setup(request):
    """Step 1: Choose textbook, chapter, and duration."""
    textbook_id = request.GET.get('textbook')
    selected_textbook = None
    if textbook_id:
        selected_textbook = get_object_or_404(Textbook, pk=textbook_id, is_available=True)

    recent_sessions = StudySession.objects.filter(
        user=request.user
    ).select_related('textbook', 'textbook__subject')[:5]

    if request.method == 'POST':
        tb_id = request.POST.get('textbook_id')
        chapter_id = request.POST.get('chapter_id') or None
        duration = int(request.POST.get('duration', 25))
        textbook = get_object_or_404(Textbook, pk=tb_id)
        chapter = None
        if chapter_id:
            chapter = get_object_or_404(Chapter, pk=chapter_id, textbook=textbook)
        session = StudySession.objects.create(
            user=request.user,
            textbook=textbook,
            chapter=chapter,
            planned_duration=duration,
            status='active',
        )
        return redirect('study:session', session_id=session.pk)

    all_textbooks = Textbook.objects.filter(is_available=True).select_related(
        'subject', 'grade'
    ).order_by('grade__number', 'subject__name')

    return render(request, 'study/setup.html', {
        'all_textbooks': all_textbooks,
        'selected_textbook': selected_textbook,
        'recent_sessions': recent_sessions,
    })


@login_required
def study_session(request, session_id):
    """The main focus screen (from the sketch)."""
    session = get_object_or_404(StudySession, pk=session_id, user=request.user)
    if session.status == 'completed':
        return redirect('study:complete', session_id=session.pk)
    chapters = session.textbook.chapter_list.all()
    return render(request, 'study/session.html', {
        'session': session,
        'chapters': chapters,
        'youtube_api_key': settings.YOUTUBE_API_KEY,
    })


@login_required
def update_session(request, session_id):
    """AJAX: update session duration/notes/status."""
    if request.method == 'POST':
        session = get_object_or_404(StudySession, pk=session_id, user=request.user)
        data = json.loads(request.body)
        if 'actual_duration' in data:
            session.actual_duration = data['actual_duration']
        if 'notes' in data:
            session.notes = data['notes']
        if 'status' in data:
            session.status = data['status']
            if data['status'] == 'completed':
                session.ended_at = timezone.now()
                _update_progress(request.user, session)
        session.save()
        return JsonResponse({'status': 'ok'})
    return JsonResponse({'error': 'invalid'}, status=400)


@login_required
def take_break(request, session_id):
    """Start a break session."""
    session = get_object_or_404(StudySession, pk=session_id, user=request.user)
    duration = int(request.POST.get('duration', 5))
    break_session = BreakSession.objects.create(
        study_session=session,
        planned_duration=duration,
    )
    return redirect('study:break_screen', break_id=break_session.pk)


@login_required
def break_screen(request, break_id):
    """Break screen with YouTube player."""
    break_session = get_object_or_404(BreakSession, pk=break_id,
                                       study_session__user=request.user)
    return render(request, 'study/break.html', {
        'break_session': break_session,
        'session': break_session.study_session,
        'youtube_api_key': settings.YOUTUBE_API_KEY,
    })


@login_required
def end_break(request, break_id):
    """End break, return to study."""
    if request.method == 'POST':
        break_session = get_object_or_404(BreakSession, pk=break_id,
                                          study_session__user=request.user)
        data = json.loads(request.body)
        break_session.actual_duration = data.get('actual_duration', 0)
        break_session.ended_at = timezone.now()
        break_session.save()
        return JsonResponse({'redirect': f'/study/session/{break_session.study_session_id}/'})
    return JsonResponse({'error': 'invalid'}, status=400)


@login_required
def session_complete(request, session_id):
    """Session summary after completion."""
    session = get_object_or_404(StudySession, pk=session_id, user=request.user)
    breaks = session.breaks.all()
    return render(request, 'study/complete.html', {
        'session': session,
        'breaks': breaks,
        'total_break_minutes': sum(b.actual_duration for b in breaks) // 60,
    })


def youtube_search(request):
    """Server-side YouTube search with filtering."""
    query = request.GET.get('q', '')
    mode = request.GET.get('mode', 'study')  # 'study' or 'break'
    api_key = settings.YOUTUBE_API_KEY

    if not api_key or not query:
        return JsonResponse({'items': [], 'error': 'No API key or query'})

    params = {
        'part': 'snippet',
        'q': query,
        'type': 'video',
        'maxResults': 10,
        'key': api_key,
        'videoDuration': 'medium' if mode == 'study' else 'any',
    }
    if mode == 'study':
        params['videoCategoryId'] = '27'  # Education category

    try:
        r = requests.get('https://www.googleapis.com/youtube/v3/search', params=params, timeout=8)
        data = r.json()
        items = []
        for item in data.get('items', []):
            video_id = item['id'].get('videoId', '')
            if not video_id:
                continue
            items.append({
                'id': video_id,
                'title': item['snippet']['title'],
                'channel': item['snippet']['channelTitle'],
                'thumbnail': item['snippet']['thumbnails']['medium']['url'],
            })
        return JsonResponse({'items': items})
    except Exception as e:
        return JsonResponse({'items': [], 'error': str(e)})


def _update_progress(user, session):
    """Update progress stats after a session completes."""
    from progress.models import SubjectProgress, DailyStudyLog, StudyStreak
    from datetime import date

    subject = session.textbook.subject
    minutes = session.actual_duration // 60

    prog, _ = SubjectProgress.objects.get_or_create(user=user, subject=subject)
    prog.total_minutes += minutes
    prog.sessions_count += 1
    prog.last_studied = timezone.now()
    prog.save()

    today = date.today()
    log, _ = DailyStudyLog.objects.get_or_create(user=user, date=today,
                                                   defaults={'goal_minutes': getattr(
                                                       user.profile, 'study_goal_minutes', 120)})
    log.total_minutes += minutes
    log.sessions_count += 1
    try:
        goal = user.profile.study_goal_minutes
    except Exception:
        goal = 120
    log.goal_met = log.total_minutes >= goal
    log.save()

    streak, _ = StudyStreak.objects.get_or_create(user=user)
    from datetime import timedelta
    if streak.last_study_date is None or streak.last_study_date < today:
        if streak.last_study_date == today - timedelta(days=1):
            streak.current_streak += 1
        else:
            streak.current_streak = 1
        streak.total_study_days += 1
        streak.last_study_date = today
        if streak.current_streak > streak.longest_streak:
            streak.longest_streak = streak.current_streak
        streak.save()
