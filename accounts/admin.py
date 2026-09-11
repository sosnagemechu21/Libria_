from django.contrib import admin
from .models import UserProfile


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'theme', 'grade_level', 'display_name', 'joined_at']
    list_filter = ['theme', 'grade_level']
    search_fields = ['user__username', 'display_name']
    readonly_fields = ['joined_at', 'updated_at']
