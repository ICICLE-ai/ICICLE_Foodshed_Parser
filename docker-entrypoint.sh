#!/bin/bash
service nginx start;
gunicorn -w 2 -k uvicorn.workers.UvicornWorker main:app;
