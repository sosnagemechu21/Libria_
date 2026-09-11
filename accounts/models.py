from django.db import models
from django.contrib.auth.models import User


THEME_CHOICES = [
    ('noir', '🖤 Noir'),
    ('forest', '🌿 Forest'),
    ('paper', '📜 Paper'),
    ('midnight', '🌌 Midnight'),
    ('blush', '🌸 Blush'),
    ('mocha', '☕ Mocha'),
]

GRADE_CHOICES = [
    ('9', 'Grade 9'),
    ('10', 'Grade 10'),
    ('11', 'Grade 11'),
    ('12', 'Grade 12'),
    ('university', 'University / Freshman'),
]


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    theme = models.CharField(max_length=20, choices=THEME_CHOICES, default='midnight')
    grade_level = models.CharField(max_length=20, choices=GRADE_CHOICES, default='9')
    display_name = models.CharField(max_length=100, blank=True)
    bio = models.TextField(blank=True)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    ai_provider = models.CharField(max_length=20, default='gemini',
                                   choices=[('gemini', 'Google Gemini'), ('openai', 'OpenAI')])
    ai_api_key = models.CharField(max_length=255, blank=True,
                                  help_text='Your personal AI API key (stored locally)')
    study_goal_minutes = models.IntegerField(default=120,
                                             help_text='Daily study goal in minutes')
    joined_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username}'s Profile"

    def get_display_name(self):
        return self.display_name or self.user.first_name or self.user.username

    class Meta:
        verbose_name = 'User Profile'
        verbose_name_plural = 'User Profiles'
