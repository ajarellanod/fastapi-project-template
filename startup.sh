#!/bin/bash
sleep 10
alembic upgrade head

LOG_LEVEL=$(printenv LOG_LEVEL)
if [ -z "$LOG_LEVEL" ]; then
  LOG_LEVEL="error"
fi

uvicorn project.main:app --host 0.0.0.0 --port 8000 --log-level "$LOG_LEVEL"
