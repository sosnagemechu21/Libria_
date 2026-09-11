"""
Core context processor — injects theme + themes list into every template.
"""
from django.conf import settings

THEMES = [
    ('noir', '🖤 Noir'),
    ('forest', '🌿 Forest'),
    ('paper', '📜 Paper'),
    ('midnight', '🌌 Midnight'),
    ('blush', '🌸 Blush'),
    ('mocha', '☕ Mocha'),
]

THEME_PREVIEWS = [
    ('noir',     '🖤 Noir',     '#FFFFFF', '#000000'),
    ('forest',   '🌿 Forest',   '#262D1A', '#7A9E4E'),
    ('paper',    '📜 Paper',    '#F4EDE1', '#8B6B4A'),
    ('midnight', '🌌 Midnight', '#111827', '#4B7BE5'),
    ('blush',    '🌸 Blush',    '#F7E8E8', '#C26E7A'),
    ('mocha',    '☕ Mocha',    '#E8DDD0', '#9B7355'),
]


def theme_context(request):
    theme = 'midnight'
    if request.user.is_authenticated:
        try:
            theme = request.user.profile.theme
        except Exception:
            pass
    return {
        'current_theme': theme,
        'themes': THEMES,
        'theme_previews': THEME_PREVIEWS,
        'YOUTUBE_API_KEY': getattr(settings, 'YOUTUBE_API_KEY', ''),
    }
