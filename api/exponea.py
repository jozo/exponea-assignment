import asyncio
from typing import Iterable, List

import httpx
import orjson
from logzero import logger
from pydantic import BaseModel, ValidationError

from api.config import MAX_CONN, MAX_KEEP_ALIVE, URL

client = httpx.AsyncClient(
    limits=httpx.Limits(
        max_keepalive_connections=MAX_KEEP_ALIVE, max_connections=MAX_CONN
    )
)


class TimeResponse(BaseModel):
    time: int


class ApiError(Exception):
    pass


async def call_exponea(timeout: float, api_client: httpx.AsyncClient = client):
    try:
        r = await api_client.get(URL, timeout=timeout)
        if r.status_code == 200:
            return r.text
        else:
            raise ApiError(f"Wrong status code ({r.status_code})")
    except httpx.HTTPError:
        raise ApiError("Problem with connection to API")


def collect_responses(tasks: Iterable[asyncio.Future]) -> List[dict]:
    results = []
    for t in tasks:
        data = collect_response(t)
        if data:
            results.append(data)
    return results


def collect_response(task: asyncio.Future) -> dict:
    try:
        data = orjson.loads(task.result())
        data = TimeResponse(**data)
        return data.dict()
    except ApiError as e:
        logger.error("Exponea API error. %s", e)
    except (orjson.JSONDecodeError, ValidationError) as e:
        logger.error("Can't parse response body. %s", e)
    except Exception as e:
        logger.error("Unexpected exception: %s", e)
