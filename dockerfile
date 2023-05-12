FROM python:3.7-slim-buster

ENV PYTHONFAULTHANDLER=1 \
  PYTHONUNBUFFERED=1 \
  PYTHONHASHSEED=random \
  PIP_NO_CACHE_DIR=off \
  PIP_DISABLE_PIP_VERSION_CHECK=on \
  PIP_DEFAULT_TIMEOUT=100 \
  POETRY_VERSION=1.0.0

RUN pip install poetry

RUN python3 -m pip install --user pipx
RUN python3 -m pipx ensurepath

WORKDIR /app
# Install poetry environment
COPY pyproject.toml poetry.lock ./
COPY src/ ./
COPY curlAPI.py ./
COPY demo.py ./
COPY runCompletePipeline.sh ./
COPY trained_models/ ./trained_models
# RUN poetry config virtualenvs.in-project true
# RUN poetry env use /usr/bin/python3.7
# RUN poetry install
RUN poetry config installer.max-workers 10
RUN poetry config virtualenvs.create false
RUN poetry install --no-dev --no-interaction --no-ansi
RUN poetry shell

# Install fastapi and uvicorn
RUN python3.7 -m pip install fastapi
RUN python3.7 -m pip install uvicorn

RUN export PYTHONPATH=$PWD

ENTRYPOINT uvicorn curlAPI:app --reload --host 0.0.0.0 --port 8000
# This app is using fastapi