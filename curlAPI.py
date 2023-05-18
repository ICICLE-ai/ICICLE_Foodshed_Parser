from fastapi import FastAPI
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
import uvicorn
import semantic_parsing_with_constrained_lm.run_instant as run_instant
from demo import canonToCmd
import sys, os

app = FastAPI()

@app.get("/{query}")
def read_root(query: str):
    # Suppress print statements from run_instant
    sys.stdout = open(os.devnull, 'w')
    outVal = run_instant.utteranceRun(query)
    for idx, val in enumerate(outVal):
        val['rank'] = idx
        val['cmd'] = canonToCmd(val['text'])
    jsonVal = jsonable_encoder(outVal)
    return JSONResponse(content=jsonVal)
@app.get("/ping")
def ping():
    # Test connection without calling the model.
    return JSONRespone(content=jsonable_encoder({'pong': True}))
