FROM tiangolo/uvicorn-gunicorn-fastapi:python3.8-slim

# Install python packages
RUN python -m venv "/opt/venv" \
    && . "/opt/venv/bin/activate" \
    && pip install --upgrade pip \
    && pip install poetry
COPY ["pyproject.toml", "poetry.lock", "/opt/"]
RUN cd "/opt/" && . "/opt/venv/bin/activate" && poetry install

ENV PYTHONUNBUFFERED=1
ENV VIRTUAL_ENV=/opt/venv
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

COPY ./api /app

# Compile to start faster
RUN python -m compileall /app
