#!/bin/bash -e
poetry run alembic upgrade head

exec $@
