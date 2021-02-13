from typing import Optional

from fastapi import FastAPI

app = FastAPI()


@app.get("/api/all")
async def api_all():
    return {"Hello": "All"}


@app.get("/api/first")
async def api_first():
    return {"Hello": "First"}


@app.get("/api/within-timeout")
async def api_timeout():
    return {"Hello": "Timeout"}


@app.get("/api/smart")
async def api_smart():
    return {"Hello": "Smart"}
