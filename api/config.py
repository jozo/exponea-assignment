import os

HOST = os.getenv("API_HOST", "0.0.0.0")
PORT = os.getenv("API_PORT", 8000)


REQUESTS_LIMIT = os.getenv("REQUESTS_LIMIT", 3)
"""How many times we call Exponea API during a request"""

URL = "https://exponea-engineering-assignment.appspot.com/api/work"

MAX_CONN = os.getenv("MAX_CONN", 200)
MAX_KEEP_ALIVE = os.getenv("MAX_KEEP_ALIVE", 25)
"""Limits can be tweaked, Exponea API supports keep-alive"""

MAX_TIMEOUT = os.getenv("MAX_TIMEOUT", 60)
"""Maximum timeout that can be specified for our API in url params. Seconds."""
