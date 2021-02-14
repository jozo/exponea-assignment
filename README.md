# Exponea assignment

Implemented in Python with Fast API


Use docker to start the service or poetry

## Poetry
```shell
poetry install
cd src/
poetry run uvicorn main:app --host=0.0.0.0 --port=8000
```

## Docker
```shell
docker-compose up
```


## Docs (Open API)
http://0.0.0.0:8000/docs
