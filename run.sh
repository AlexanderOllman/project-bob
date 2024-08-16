#!/bin/sh

# Set default values
APP_MODULE=${APP_MODULE:-app.src.app.main:app}
HOST=${HOST:-0.0.0.0}
PORT=${PORT:-8080}

# Activate virtualenv in subshell for isolation
(
  source jyoti-core-venv/bin/activate

  uvicorn "$APP_MODULE" --host "$HOST" --port "$PORT" --loop asyncio
)

trap 'kill %1' INT TERM EXIT

