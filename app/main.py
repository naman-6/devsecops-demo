import os
from fastapi import FastAPI
from redis import Redis

app = FastAPI(title="DevSecOps Ultra-Lean API")

# Connect to the backend database tier dynamically via environment variables
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
redis_client = Redis(host=REDIS_HOST, port=6379, decode_responses=True)

@app.get("/")
def read_root():
    return {"status": "Online", "framework": "FastAPI", "security_scan": "Passed"}

@app.get("/hit-counter")
def get_hits():
    try:
        hits = redis_client.incr("visitor_count")
        return {"total_hits": hits, "database_tier": "Connected"}
    except Exception as e:
        return {"error": "Database connection failed", "details": str(e)}
