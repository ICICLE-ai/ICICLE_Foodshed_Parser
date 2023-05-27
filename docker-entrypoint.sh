#!/bin/bash
.venv/bin/gunicorn --config gunicorn.conf.py main:app;
