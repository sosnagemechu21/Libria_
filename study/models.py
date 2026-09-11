from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from library.models import Textbook, Chapter


SESSION_STATUS = [
    ('active', 'Active'),
    ('paused', 'Paused'),
    ('completed', 'Completed'),
    ('abandoned', 'Abandoned'),
]


class StudySession(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='study_sessions')
    textbook = models.ForeignKey(Textbook, on_delete=models.CASCADE, related_name='sessions')
    chapter = models.ForeignKey(Chapter, on_delete=models.SET_NULL, null=True, blank=True)
    planned_duration = models.IntegerField(default=25, help_text='Duration in minutes')
    actual_duration = models.IntegerField(default=0, help_text='Actual seconds studied')
    started_at = models.DateTimeField(auto_now_add=True)
    ended_at = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=15, choices=SESSION_STATUS, default='active')
    notes = models.TextField(blank=True, help_text='Student notes during session')
    topics_covered = models.TextField(blank=True)

    def __str__(self):
        return f"{self.user.username} - {self.textbook.subject.name} ({self.started_at.date()})"

    def get_duration_minutes(self):
        return round(self.actual_duration / 60)

    class Meta:
        ordering = ['-started_at']


class BreakSession(models.Model):
    study_session = models.ForeignKey(StudySession, on_delete=models.CASCADE,
                                      related_name='breaks')
    planned_duration = models.IntegerField(default=5, help_text='Break duration in minutes')
    actual_duration = models.IntegerField(default=0, help_text='Actual seconds on break')
    overrun = models.BooleanField(default=False)
    overrun_minutes = models.FloatField(default=0.0)
    started_at = models.DateTimeField(auto_now_add=True)
    ended_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Break after session {self.study_session_id}"


class YouTubeVideoWatch(models.Model):
    WATCH_TYPE_CHOICES = [
        ('study', 'During Study'),
        ('break', 'During Break'),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='youtube_watches')
    study_session = models.ForeignKey(StudySession, on_delete=models.SET_NULL,
                                      null=True, blank=True)
    break_session = models.ForeignKey(BreakSession, on_delete=models.SET_NULL,
                                      null=True, blank=True)
    video_id = models.CharField(max_length=20)
    title = models.CharField(max_length=300)
    channel = models.CharField(max_length=150, blank=True)
    duration_seconds = models.IntegerField(default=0)
    watch_type = models.CharField(max_length=10, choices=WATCH_TYPE_CHOICES, default='study')
    approved_for_study = models.BooleanField(default=False)
    watched_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} ({self.watch_type})"

    class Meta:
        ordering = ['-watched_at']

# ==========================================
# Focus Loop & Boundary Engine Integration
# ==========================================

class BoundaryEvent(models.Model):
    EVENT_TYPES = [
        ('YOUTUBE_ATTEMPT_FOCUS', 'YouTube Blocked During Focus 🔒'),
        ('SHORTS_BLOCKED_BREAK', 'Shorts Intercepted During Break ❌'),
        ('APP_BLOCKED_FOCUS', 'Protected App Blocked 🚫'),
        ('BREAK_OVERRUN', 'Break Overrun ⚠️'),
        ('LONG_VIDEO_WATCHED', 'Long Video Watched ✅'),
        ('BREAK_COMPLETED', 'Break Completed On Time 🌿'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='boundary_events')
    study_session = models.ForeignKey(StudySession, on_delete=models.SET_NULL, null=True, blank=True)
    event_type = models.CharField(max_length=40, choices=EVENT_TYPES)
    app_name = models.CharField(max_length=60, default='YouTube')
    target_url = models.CharField(max_length=500, blank=True)
    timestamp = models.DateTimeField(default=timezone.now)
    note = models.CharField(max_length=255, blank=True)
    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return f"[{self.timestamp.strftime('%H:%M:%S')}] {self.get_event_type_display()} ({self.user.username})"


class YouTubeChannel(models.Model):
    name = models.CharField(max_length=150)
    handle = models.CharField(max_length=100, blank=True, null=True, unique=True)
    channel_id = models.CharField(max_length=80, blank=True, null=True, unique=True)
    custom_url = models.CharField(max_length=255, blank=True, null=True)
    avatar_url = models.URLField(blank=True, default='')
    description = models.TextField(blank=True, default='')
    subscriber_count = models.CharField(max_length=50, blank=True, default='')
    video_count = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} ({self.handle or self.channel_id or 'No Handle'})"


class CuratedVideo(models.Model):
    channel_ref = models.ForeignKey(
        YouTubeChannel,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='videos'
    )
    title = models.CharField(max_length=255)
    channel = models.CharField(max_length=120)
    duration_str = models.CharField(max_length=20, default="24m")
    duration_minutes = models.IntegerField(default=24)
    youtube_id = models.CharField(max_length=60)
    category = models.CharField(max_length=60, default="Documentary")
    description = models.TextField(blank=True)
    thumbnail_url = models.URLField(blank=True)
    is_saved = models.BooleanField(default=False)
    watch_count = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-is_saved', '-created_at']

    def __str__(self):
        return f"{self.title} ({self.channel})"


class ProtectedApp(models.Model):
    name = models.CharField(max_length=60, unique=True)
    is_enabled = models.BooleanField(default=True)
    special_rule = models.CharField(max_length=150, default="Blocked during focus")
    icon = models.CharField(max_length=40, default="shield")

    def __str__(self):
        return f"{self.name} ({'Protected' if self.is_enabled else 'Off'})"
