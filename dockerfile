
FROM nginx:1.21.3

# Set environment variables
ENV PIP_DISABLE_PIP_VERSION_CHECK=on \
  PIP_DEFAULT_TIMEOUT=100 \
  PYTHONUNBUFFERED=1 \
  PYTHONHASHSEED=random \
  PROMETHEUS_MULTIPROC_DIR=/tmp/prometheus

# Install system dependencies
RUN apt update && apt install -y python3.7 python3-venv python3-pip git

WORKDIR /app

# Upgrade pip, setuptools and wheel. Need this to avoid errors installing older packages
RUN python3.7 -m pip install --upgrade pip \
  setuptools \
  wheel

# Install dependencies for Conversational AI
COPY requirements.txt ./requirements.txt
RUN python3.7 -m pip install -r requirements.txt
RUN python3.7 -m pip install git+https://github.com/microsoft/task_oriented_dialogue_as_dataflow_synthesis.git

# Install dependencies for application
RUN python3.7 -m pip install fastapi \
  prometheus-client \
  uvicorn \
  gunicorn

# Create directory for prometheus multiprocess
RUN mkdir -p /tmp/prometheus

# Copy source files
COPY src/ ./
COPY main.py ./main.py
COPY demo.py ./demo.py
COPY runCompletePipeline.sh ./runCompletePipeline.sh
COPY trained_models/ ./trained_models

# Copy nginx and gunicorn configuration files
COPY gunicorn.conf.py ./gunicorn.conf.py
COPY nginx.conf /etc/nginx/nginx.conf

# Copy docker entrypoint
COPY docker-entrypoint.sh ./docker-entrypoint.sh

# Run the application
ENTRYPOINT sh docker-entrypoint.sh