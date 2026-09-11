from django.contrib import admin
from .models import StudySession, BreakSession, YouTubeVideoWatch


@admin.register(StudySession)
class StudySessionAdmin(admin.ModelAdmin):
    list_display = ['user', 'textbook', 'planned_duration', 'actual_duration',
                    'status', 'started_at']
    list_filter = ['status', 'textbook__grade']
    search_fields = ['user__username']


@admin.register(BreakSession)
class BreakSessionAdmin(admin.ModelAdmin):
    list_display = ['study_session', 'planned_duration', 'actual_duration', 'started_at']


@admin.register(YouTubeVideoWatch)
class YouTubeVideoWatchAdmin(admin.ModelAdmin):
    list_display = ['user', 'title', 'watch_type', 'approved_for_study', 'watched_at']
    list_filter = ['watch_type', 'approved_for_study']
