#!/bin/bash

if [ "$1" = "api_dev" ]; then
  exec uvicorn src.app:app --reload --host 0.0.0.0 --port 5000
fi

if [ "$1" = "api" ]; then
  exec gunicorn src.app:app --config=config/gunicorn_config.py --bind=:5000 --preload
fi

if [ "$1" = "worker" ]; then
  exec celery -A src.tasks.app worker
fi

if [ "$1" = "scheduler" ]; then
  exec celery -A src.tasks.app beat
fi

exec "$@"