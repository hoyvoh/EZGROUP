#!/bin/bash
# Exit immediately if a command exits with a non-zero status
set -e

# Start the Django server
echo "Starting Django server..."
python manage.py runserver 0.0.0.0:8000 &

# Start Celery worker
echo "Starting Celery worker..."
celery -A api worker --loglevel=info &

# Start Celery beat
echo "Starting Celery beat..."
celery -A api beat --loglevel=info &

# Wait for all background processes
wait
