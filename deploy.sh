export PORT
uvicorn curlAPI:app --reload --host 0.0.0.0 --port PORT
