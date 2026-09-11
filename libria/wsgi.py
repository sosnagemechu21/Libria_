"""
WSGI config for libria project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'libria.settings')

application = get_wsgi_application()

if os.getenv('VERCEL') == '1' and not (os.getenv('POSTGRES_URL') or os.getenv('DATABASE_URL')):
    from django.core.management import call_command
    try:
        call_command('migrate', interactive=False)
    except Exception as e:
        print("Auto-migration failed:", e)

app = application
