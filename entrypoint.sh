#!/bin/bash
poetry run alembic upgrade head

poetry run python3 -m uvicorn app.main:app --host 0.0.0.0 --port $APP_PORT

exec "$@"
