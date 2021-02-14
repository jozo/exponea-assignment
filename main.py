import asyncio

import httpx
import uvicorn
from fastapi import FastAPI

URL = "https://exponea-engineering-assignment.appspot.com/api/work"
REQUESTS_LIMIT = 3      # how many times Exponea API will be called

app = FastAPI()
client = httpx.AsyncClient()


@app.on_event("shutdown")
async def shutdown():
    print("Shutdown: closing http client")
    await client.aclose()


async def call_exponea(timeout: float, api: httpx.AsyncClient = client):
    try:
        r = await api.get(URL, timeout=timeout)
        if r.status_code == 200:
            return r.json()
    except:
        return {}


@app.get("/api/all/{timeout}")
async def api_all(timeout: int):
    """Collects all successful responses from Exponea in given timeout"""
    timeout = timeout / 1000        # convert to seconds
    tasks = [call_exponea(timeout) for _ in range(REQUESTS_LIMIT)]
    done, pending = await asyncio.wait(tasks, timeout=timeout)
    return [t.result() for t in done]


@app.get("/api/first")
async def api_first():
    return {"Hello": "First"}


@app.get("/api/within-timeout")
async def api_timeout():
    return {"Hello": "Timeout"}


@app.get("/api/smart")
async def api_smart():
    return {"Hello": "Smart"}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, debug=True)
