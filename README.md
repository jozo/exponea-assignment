# Exponea assignment

Implemented in Python with Fast API

- Settings can be changed via env variables - check `src/config.py`
- To start the service use docker or poetry


## Poetry
```shell
poetry install
poetry run python src/main.py
```

## Docker
```shell
docker-compose up
```


## Docs (Open API)
http://0.0.0.0:8000/docs


## Known problems
- Graceful shutdown of `uvicorn` in docker: https://github.com/encode/uvicorn/issues/852
