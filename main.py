from fastapi import FastAPI
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from prometheus_client import (
    start_http_server, 
    Counter, 
    Summary,
    generate_latest,
    multiprocess,
    CONTENT_TYPE_LATEST,
    make_asgi_app,
    CollectorRegistry,
)
# from prometheus_fastapi_instrumentator import Instrumentator
# import uvicorn
import semantic_parsing_with_constrained_lm.run_instant as run_instant
from demo import canonToCmd
import sys, os

if "PROMETHEUS_MULTIPROC_DIR" not in os.environ:
    raise ValueError("PROMETHEUS_MULTIPROC_DIR must be set to existing empty dir.")

# Start the Prometheus client.
start_http_server(8001)

# Define the Prometheus metrics.
METRICS_COUNTER = Counter("metrics_counter", "Number of metrics requests")
PING_COUNTER = Counter("ping_counter", "Number of ping requests")
QUERY_COUNTER = Counter("query_counter", "Number of query requests")

METRICS_TIME = Summary("metrics_time", "Time spent processing metrics")
QUERY_TIME = Summary("query_time", "Time spent processing query")
PING_TIME = Summary("ping_time", "Time spent processing ping")


app = FastAPI(debug=False)

@app.get("/query")
def query(q: str):
    sys.stdout = open(os.devnull, 'w') # Suppress print statements from run_instant

    # Increment the query counter and time the query.
    QUERY_COUNTER.inc()
    QUERY_TIME.observe(1)

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
    # Increment the ping counter and time the ping.
    PING_COUNTER.inc()
    PING_TIME.observe(1)

    # Test connection without calling the model.
    return JSONResponse(content=jsonable_encoder({'pong': True}))

@app.get("/metrics")
def make_metrics():
    # Increment the metrics counter and time the metrics.
    METRICS_COUNTER.inc()
    METRICS_TIME.observe(1)

    # Return the metrics.
    registry = CollectorRegistry()
    multiprocess.MultiProcessCollector(registry)
    # resp = JSONResponse(content=jsonable_encoder(generate_latest(registry)))
    # return Response(prometheus_client.generate_latest())
    return make_asgi_app(registry)

metrics = make_metrics()
app.mount("/metrics", metrics)
