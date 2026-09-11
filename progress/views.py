from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Count
from datetime import date, timedelta
from .models import SubjectProgress, StudyStreak, DailyStudyLog
from study.models import StudySession


@login_required
def dashboard(request):
    user = request.user
    # Streak
    streak, _ = StudyStreak.objects.get_or_create(user=user)
    # Subject progress
    subject_progress = SubjectProgress.objects.filter(user=user).select_related(
        'subject'
    ).order_by('-total_minutes')[:8]
    # Weekly study logs (last 7 days)
    today = date.today()
    week_logs = []
    for i in range(6, -1, -1):
        d = today - timedelta(days=i)
        log = DailyStudyLog.objects.filter(user=user, date=d).first()
        week_logs.append({
            'date': d.strftime('%a'),
            'minutes': log.total_minutes if log else 0,
            'goal_met': log.goal_met if log else False,
        })
    # Total stats
    total_stats = StudySession.objects.filter(
        user=user, status='completed'
    ).aggregate(
        total_seconds=Sum('actual_duration'),
        total_sessions=Count('id'),
    )
    total_minutes = (total_stats['total_seconds'] or 0) // 60
    total_sessions = total_stats['total_sessions'] or 0
    # Recent sessions
    recent_sessions = StudySession.objects.filter(
        user=user
    ).select_related('textbook', 'textbook__subject').order_by('-started_at')[:5]
    # Try get profile
    try:
        goal_minutes = user.profile.study_goal_minutes
    except Exception:
        goal_minutes = 120
    # Today log
    today_log = DailyStudyLog.objects.filter(user=user, date=today).first()
    today_minutes = today_log.total_minutes if today_log else 0

    from django.utils import timezone as tz
    hour = tz.localtime().hour
    if hour < 12:
        greeting = 'morning'
    elif hour < 17:
        greeting = 'afternoon'
    else:
        greeting = 'evening'

    return render(request, 'progress/dashboard.html', {
        'time_greeting': greeting,
        'streak': streak,
        'subject_progress': subject_progress,
        'week_logs': week_logs,
        'total_minutes': total_minutes,
        'total_sessions': total_sessions,
        'recent_sessions': recent_sessions,
        'goal_minutes': goal_minutes,
        'today_minutes': today_minutes,
        'today_percent': min(100, int(today_minutes / goal_minutes * 100)) if goal_minutes else 0,
    })
