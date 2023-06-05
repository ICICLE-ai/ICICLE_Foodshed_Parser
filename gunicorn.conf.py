import os
import multiprocessing
from prometheus_client import multiprocess

def child_exit(server, worker):
    multiprocess.mark_process_dead(worker.pid)

# Bind to host and port
bind = os.environ['HOST'] + ':' + os.environ['PORT']

# Set the number of workers
workers = os.getenv('WORKERS', default=(multiprocessing.cpu_count() * 2 + 1))

# Set the worker class to uvicorn workers
worker_class = 'uvicorn.workers.UvicornWorker'

# Set the maximum number of requests a worker will process before restarting
backlog = os.getenv('BACKLOG', default=2048)

# Set the number of worker threads
threads = os.getenv('THREADS', default=(multiprocessing.cpu_count() * 2 + 1))
