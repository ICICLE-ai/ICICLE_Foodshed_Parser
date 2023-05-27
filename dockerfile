
FROM python:3.7-slim-buster as build-stage

# Set environment variables
ENV PIP_DISABLE_PIP_VERSION_CHECK=on \
  PIP_DEFAULT_TIMEOUT=100

# Install system dependencies
RUN apt update && apt install -y git

WORKDIR /app

# Create virtual environment
RUN python -m venv .venv

# Upgrade pip, setuptools and wheel. Need this to avoid errors installing older packages
RUN .venv/bin/pip install --upgrade pip \
  setuptools \
  wheel

# Install dependencies for Conversational AI
COPY requirements.txt ./requirements.txt
RUN .venv/bin/pip install -r requirements.txt
RUN .venv/bin/pip install git+https://github.com/microsoft/task_oriented_dialogue_as_dataflow_synthesis.git

# Install dependencies for application
RUN .venv/bin/pip install fastapi \
  prometheus-client \
  uvicorn \
  gunicorn

FROM python:3.7-slim-buster as production-stage

ENV PYTHONUNBUFFERED=1 \
  PYTHONHASHSEED=random \
  PROMETHEUS_MULTIPROC_DIR=/tmp/prometheus

# Create directory for prometheus multiprocess
RUN mkdir -p /tmp/prometheus

# Copy virtual environment from build stage
WORKDIR /app
COPY --from=build-stage /app/.venv .venv

# Copy source files
COPY src/ ./
COPY main.py ./main.py
COPY demo.py ./demo.py
COPY runCompletePipeline.sh ./runCompletePipeline.sh
COPY trained_models/ ./trained_models

# Copy docker entrypoint and gunicorn config
COPY docker-entrypoint.sh ./docker-entrypoint.sh
COPY gunicorn.conf.py ./gunicorn.conf.py

# Run the application
ENTRYPOINT sh docker-entrypoint.sh