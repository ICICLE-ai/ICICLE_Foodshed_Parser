
FROM nginx:1.21.3

ENV PIP_DISABLE_PIP_VERSION_CHECK=on \
  PIP_DEFAULT_TIMEOUT=100 

RUN apt update && apt install -y python3.7 python3-venv python3-pip git
# RUN curl -sSL https://install.python-poetry.org | python3 -

WORKDIR /app
# Install poetry environment
# RUN python -m venv venv
RUN python3.7 -m pip install --upgrade pip
RUN python3.7 -m pip install --upgrade setuptools
RUN python3.7 -m pip install --upgrade wheel


COPY requirements.txt ./requirements.txt
RUN python3.7 -m pip install -r requirements.txt
RUN python3.7 -m pip install git+https://github.com/microsoft/task_oriented_dialogue_as_dataflow_synthesis.git
# RUN python3.7 -m pip install pandas

RUN python3.7 -m pip install fastapi \
    prometheus-client \
    uvicorn \
    gunicorn

ENV PYTHONUNBUFFERED=1 \
  PYTHONHASHSEED=random
# RUN apt update && apt install -y  python3-venv

WORKDIR /app

# COPY --from=builder /app/venv ./venv
COPY src/ ./
COPY main.py ./main.py
COPY demo.py ./demo.py
COPY runCompletePipeline.sh ./runCompletePipeline.sh
COPY trained_models/ ./trained_models
COPY docker-entrypoint.sh ./docker-entrypoint.sh
COPY gunicorn.conf.py ./gunicorn.conf.py
COPY nginx.conf /etc/nginx/nginx.conf

EXPOSE 80
ENTRYPOINT sh docker-entrypoint.sh