#!/bin/bash
# Build script for Vercel
echo "Building for Vercel..."
python3.12 -m pip install -r requirements.txt
python3.12 manage.py collectstatic --noinput
python3.12 manage.py migrate
echo "Build completed."
