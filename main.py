from fastapi import FastAPI
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from prometheus_client import (
    Counter, 
    Histogram,
    generate_latest,
    multiprocess,
    CONTENT_TYPE_LATEST,
    make_asgi_app,
    CollectorRegistry,
)
import semantic_parsing_with_constrained_lm.run_instant as run_instant
from demo import canonToCmd
import sys, os

# Check that the PROMETHEUS_MULTIPROC_DIR environment variable is set.
if "PROMETHEUS_MULTIPROC_DIR" not in os.environ:
    raise ValueError("PROMETHEUS_MULTIPROC_DIR must be set to empty dir.")

# Define the Prometheus metrics.
QUERY_HISTOGRAM = Histogram("query_time", "Time spent processing query and number of requests")
PING_HISTOGRAM = Histogram("ping_time", "Time spent processing ping and number of requests")

app = FastAPI(debug=False)

@app.get("/query")
def query(q: str):
    with QUERY_HISTOGRAM.time():
        # Suppress print statements from run_instant
        sys.stdout = open(os.devnull, 'w') 

        # Run the model and return the output.
        q = ' '.join(q.split('_'))
        outVal = run_instant.utteranceRun(q)
        for idx, val in enumerate(outVal):
            val['rank'] = idx
            val['cmd'] = canonToCmd(val['text'])
        jsonVal = jsonable_encoder(outVal)
        return JSONResponse(content=jsonVal)

@app.get("/ping")
def ping():
    with PING_HISTOGRAM.time():
        # Test connection without calling the model.
        return JSONResponse(content=jsonable_encoder({'pong': True}))

@app.get("/metrics")
def get_metrics():
    # Grab metrics from the Prometheus registry
    registry = CollectorRegistry()
    multiprocess.MultiProcessCollector(registry)
    latest = generate_latest(registry).decode().split('\n')
    # Parse the metrics into a dictionary
    response_body = dict()
    for line in latest:
        if line.startswith('#'):
            continue
        if line == '':
            continue
        key, val = line.split(' ')
        response_body[key] = float(val)
    # Return the metrics as JSON
    response = JSONResponse(content=jsonable_encoder(response_body))
    return response
