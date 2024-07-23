FROM python:3.12-alpine3.19
ENV PYTHONPATH=/app/src

ARG DEPLOYMENT_ENV

ENV DEPLOYMENT_ENV=${DEPLOYMENT_ENV} \
  FLASK_APP=run.py \
  PYTHONFAULTHANDLER=1 \
  PYTHONUNBUFFERED=1 \
  PYTHONHASHSEED=random \
  PIP_NO_CACHE_DIR=off \
  PIP_DISABLE_PIP_VERSION_CHECK=on \
  PIP_DEFAULT_TIMEOUT=100 \
  POETRY_VERSION=1.7.1 \
  LOG_LEVEL=DEBUG


WORKDIR /app

RUN pip install poetry==$POETRY_VERSION

COPY poetry.lock pyproject.toml /app/

RUN poetry config virtualenvs.create false \
  && poetry install $(test "$DEPLOYMENT_ENV" == production && echo "--no-dev") --no-interaction --no-ansi

COPY ./velero_ui /app/velero_ui
COPY ./run.py /app/run.py

CMD poetry run gunicorn run:app --bind 0.0.0.0:5000 --log-level "$LOG_LEVEL"