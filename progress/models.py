from django.db import models
from django.contrib.auth.models import User
from library.models import Subject, Textbook


class SubjectProgress(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='subject_progress')
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    total_minutes = models.IntegerField(default=0)
    sessions_count = models.IntegerField(default=0)
    last_studied = models.DateTimeField(null=True, blank=True)
    strength_score = models.FloatField(default=0.0,
                                       help_text='0.0 = needs work, 1.0 = strong')
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['user', 'subject']
        ordering = ['-total_minutes']

    def __str__(self):
        return f"{self.user.username} - {self.subject.name}"


class StudyStreak(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='streak')
    current_streak = models.IntegerField(default=0)
    longest_streak = models.IntegerField(default=0)
    last_study_date = models.DateField(null=True, blank=True)
    total_study_days = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.user.username}: {self.current_streak} day streak"


class DailyStudyLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='daily_logs')
    date = models.DateField()
    total_minutes = models.IntegerField(default=0)
    sessions_count = models.IntegerField(default=0)
    goal_minutes = models.IntegerField(default=120)
    goal_met = models.BooleanField(default=False)

    class Meta:
        unique_together = ['user', 'date']
        ordering = ['-date']

    def __str__(self):
        return f"{self.user.username} - {self.date}: {self.total_minutes} min"
