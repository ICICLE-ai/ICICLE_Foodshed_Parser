from fastapi import FastAPI
import uvicorn
import semantic_parsing_with_constrained_lm.run_instant as run_instant
from demo import canonToCmd
import json

app = FastAPI()

@app.get("/{query}")
def read_root(query: str):
    outVal = run_instant.utteranceRun(query)
    for idx, val in enumerate(outVal):
        val['rank'] = idx
        val['cmd'] = canonToCmd(val['text'])
    return json.dumps(outVal)