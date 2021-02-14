import asyncio
from typing import Set

import httpx
import orjson
from logzero import logger
from pydantic import BaseModel, ValidationError

from src.config import MAX_CONN, MAX_KEEP_ALIVE, URL


client = httpx.AsyncClient(
    limits=httpx.Limits(
        max_keepalive_connections=MAX_KEEP_ALIVE, max_connections=MAX_CONN
    )
)


class TimeResponse(BaseModel):
    time: int


class ApiError(Exception):
    pass


async def call_exponea(timeout: float, api: httpx.AsyncClient = client):
    try:
        r = await api.get(URL, timeout=timeout)
        if r.status_code == 200:
            return r.text
        else:
            raise ApiError(f"Wrong status code ({r.status_code})")
    except httpx.HTTPError:
        raise ApiError("Problem with connection to API")


def collect_responses(tasks: Set[asyncio.Future]):
    results = []
    for t in tasks:
        try:
            data = orjson.loads(t.result())
            data = TimeResponse(**data)
            results.append(data.dict())
        except ApiError as e:
            logger.error("Exponea API error. %s", e)
        except (orjson.JSONDecodeError, ValidationError) as e:
            logger.error("Can't parse response body. %s", e)
        except:
            logger.exception("Unknown error")
    return results
