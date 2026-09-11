from django.db import models
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
