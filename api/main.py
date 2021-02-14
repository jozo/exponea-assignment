import asyncio
from typing import Iterable, Optional

import uvicorn
from fastapi import Depends, FastAPI, HTTPException
from fastapi.responses import ORJSONResponse
from logzero import logger

from .config import HOST, MAX_TIMEOUT, PORT, REQUESTS_LIMIT
from .exponea import call_exponea, client, collect_response, collect_responses

app = FastAPI()


@app.on_event("shutdown")
async def shutdown():
    logger.info("Shutdown: closing http client")
    await client.aclose()


async def validate_timeout(timeout: int = 1000):
    timeout = timeout / 1000
    if timeout > MAX_TIMEOUT:
        raise HTTPException(
            400, detail=f"Invalid timeout - maximum is {MAX_TIMEOUT*1000} ms"
        )
    return timeout


def cancel_tasks(tasks: Iterable):
    for t in tasks:
        t.cancel()


def prepare_response(data: Optional):
    if data is not None:
        return data
    else:
        raise HTTPException(500, detail="Internal error")


@app.get("/api/all/", response_class=ORJSONResponse)
async def api_all(timeout: float = Depends(validate_timeout)):
    """Collects all successful responses from Exponea testing HTTP server
    and returns the result as an array.

    If timeout is reached before all requests finish, or none of the responses
    were successful, the endpoint returns an error.
    """
    tasks = [call_exponea(timeout) for _ in range(REQUESTS_LIMIT)]
    done, pending = await asyncio.wait(tasks, timeout=timeout)
    cancel_tasks(pending)
    logger.info("%d tasks done, %d over timeout", len(done), len(pending))

    results = collect_responses(done)
    if pending or len(results) == 0:
        results = None
    return prepare_response(results)


@app.get("/api/first/", response_class=ORJSONResponse)
async def api_first(timeout: float = Depends(validate_timeout)):
    """Returns the first successful response that returns from Exponea testing
    HTTP server.

    If timeout is reached before any successful response was received,
    the endpoint returns an error.
    """
    tasks = [call_exponea(timeout) for _ in range(REQUESTS_LIMIT)]
    done, pending = await asyncio.wait(
        tasks, timeout=timeout, return_when=asyncio.FIRST_COMPLETED
    )
    cancel_tasks(pending)
    logger.info("%d tasks done, %d over timeout", len(done), len(pending))

    results = collect_responses(done)
    if results:
        return prepare_response(results[0])
    return prepare_response(None)


@app.get("/api/within-timeout/", response_class=ORJSONResponse)
async def api_within_timeout(timeout: float = Depends(validate_timeout)):
    """Collects all successful responses that return within a given timeout.

    If a timeout is reached before any of the 3 requests finish, the server
    should return an empty array instead of an error.
    (This means that this endpoint should never return an error).
    """
    tasks = [call_exponea(timeout) for _ in range(REQUESTS_LIMIT)]
    done, pending = await asyncio.wait(tasks, timeout=timeout)
    logger.info("%d tasks done, %d over timeout", len(done), len(pending))

    cancel_tasks(pending)
    return collect_responses(done)


@app.get("/api/smart/", response_class=ORJSONResponse)
async def api_smart(timeout: float = Depends(validate_timeout)):
    """Instead of firing all 3 requests at once, this endpoint will first fire
    only a single request to Exponea testing HTTP server.

    Then 2 scenarios can happen:
        a. Received a successful response within 300 milliseconds:
            return the response
        b. Didn't receive a response within 300 milliseconds, or the response
        was not successful:
            fire another 2 requests to Exponea testing HTTP server. Return
            the first successful response from any of those 3 requests
            (including the first one).
    """
    # Fire first task
    first_task = asyncio.create_task(call_exponea(timeout), name="first")
    done, pending = await asyncio.wait(
        [first_task], timeout=0.3, return_when=asyncio.FIRST_COMPLETED
    )
    if done:
        pending_first = []
        result = collect_response(list(done)[0])
        if result:
            return result
    else:
        pending_first = list(pending)

    # Continue with the first and fire 2 more
    tasks = [call_exponea(timeout) for _ in range(REQUESTS_LIMIT-1)]
    done, pending = await asyncio.wait(
        tasks+pending_first, timeout=timeout, return_when=asyncio.FIRST_COMPLETED
    )
    cancel_tasks(pending)
    logger.info("%d tasks done, %d over timeout", len(done), len(pending))

    results = collect_responses(done)
    return prepare_response(results[0] if results else None)


if __name__ == "__main__":
    uvicorn.run(app, host=HOST, port=PORT)
