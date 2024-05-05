#!/bin/sh

export APP_MODULE=${APP_MODULE-app.main:app}
export UV_HOST=${UV_HOST:-0.0.0.0}
export UV_PORT=${UV_PORT:-3801}

exec uvicorn --reload --host $UV_HOST --port $UV_PORT "$APP_MODULE"