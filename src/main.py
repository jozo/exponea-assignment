import asyncio

import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.responses import ORJSONResponse
from logzero import logger

from src.config import HOST, MAX_TIMEOUT, PORT, REQUESTS_LIMIT
from src.exponea import call_exponea, client, collect_responses

app = FastAPI()


@app.on_event("shutdown")
async def shutdown():
    logger.info("Shutdown: closing http client")
    await client.aclose()


@app.get("/api/all/{timeout}", response_class=ORJSONResponse)
async def api_all(timeout: int):
    """Collects all successful responses from Exponea in given timeout
    :param timeout: milliseconds
    """
    timeout = timeout / 1000
    if timeout > MAX_TIMEOUT:   # TODO move to middleware
        raise HTTPException(400, detail=f"Timeout can be max {MAX_TIMEOUT*1000}")
    tasks = [call_exponea(timeout) for _ in range(REQUESTS_LIMIT)]
    done, pending = await asyncio.wait(tasks, timeout=timeout)
    for t in pending:
        t.cancel()
    logger.info("%d tasks done, %d time outed", len(done), len(pending))
    return collect_responses(done)


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
    uvicorn.run(app, host=HOST, port=PORT)
