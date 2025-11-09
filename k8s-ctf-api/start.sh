#!/bin/sh
source venv/bin/activate

echo "Using $FLASK_ENV environment"
if [ "$FLASK_ENV" = "production" ]; then
    gunicorn -w 4 -b ${HOST}:${PORT} app:app
else
    python run.py
fi