# Libria MVP

This is the Libria MVP ready for deployment on Vercel.

## Vercel Deployment Notes
- **Database**: By default, Django uses SQLite. On Vercel, the filesystem is read-only (Serverless Functions), meaning the SQLite database will not persist changes (like new users or saved sessions) across requests. 
- **Next Steps**: To make it fully functional in production, you must connect a PostgreSQL database (like Vercel Postgres, Supabase, or Neon) by updating the `DATABASES` setting in `settings.py` and providing a `DATABASE_URL` environment variable.
- **Static Files**: WhiteNoise handles static files, which works well on Vercel.

## Local Setup
```bash
python -m venv venv
source venv/Scripts/activate # or venv/bin/activate on mac
pip install -r requirements.txt
python manage.py migrate
python manage.py seed_library
python manage.py runserver
```
