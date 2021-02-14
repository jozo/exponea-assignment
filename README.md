# Exponea assignment

Implemented in Python with FastAPI

- Settings can be changed via env variables - check `src/config.py`
- To start the service use docker or poetry


## Poetry
```shell
poetry install
poetry run python api/main.py
```

## Docker
```shell
docker-compose up
```

## Run tests
```shell
poetry run pytest
```


## Docs (Open API)
http://0.0.0.0:8000/docs


## Known problems
- Graceful shutdown of `uvicorn` in docker: https://github.com/encode/uvicorn/issues/852


## Discussion

### Can be improved
- Write unit tests
- Better logging (structlog, better messages)
- Sentry monitoring
- More monitoring (Prometheus?)
- Health check
- Tweak configs (max_connections, max_keep_alive), number of workers
- Docker - limit memory, cpu


### Known edge cases
how it behaves in certain conditions
TODO


### Resource requirements
- 1 worker ~ 370MB of memory


### How many concurrent requests can the server handle?
- Depends on the machine :)
- To handle as many requests as possible we use:
   - asyncio when doing making/handling requests
   - FastAPI with pydantic
   - share http client with connection pool
   - keep-alive
- Results from `ab`:
   - Machine: MacBook Pro (13-inch, 2017, Two Thunderbolt 3 ports)
   - Processor: 2,3 GHz Dual-Core Intel Core i5
   - Memory: 16 GB 2133 MHz LPDDR3
   - 1 uvicorn worker
   - `ab -k -c 200 -n 10000 "http://0.0.0.0:8000/api/all/?timeout=500"`
  
```
This is ApacheBench, Version 2.3 <$Revision: 1879490 $>
Copyright 1996 Adam Twiss, Zeus Technology Ltd, http://www.zeustech.net/
Licensed to The Apache Software Foundation, http://www.apache.org/

Benchmarking 0.0.0.0 (be patient)
Completed 1000 requests
Completed 2000 requests
Completed 3000 requests
Completed 4000 requests
Completed 5000 requests
Completed 6000 requests
Completed 7000 requests
Completed 8000 requests
Completed 9000 requests
Completed 10000 requests
Finished 10000 requests


Server Software:        uvicorn
Server Hostname:        0.0.0.0
Server Port:            8000

Document Path:          /api/all/?timeout=500
Document Length:        27 bytes

Concurrency Level:      200
Time taken for tests:   27.992 seconds
Complete requests:      10000
Failed requests:        0
Non-2xx responses:      10000
Keep-Alive requests:    0
Total transferred:      1710000 bytes
HTML transferred:       270000 bytes
Requests per second:    357.25 [#/sec] (mean)
Time per request:       559.839 [ms] (mean)
Time per request:       2.799 [ms] (mean, across all concurrent requests)
Transfer rate:          59.66 [Kbytes/sec] received

Connection Times (ms)
              min  mean[+/-sd] median   max
Connect:        0    1   1.1      0      12
Processing:   501  544  40.8    532     822
Waiting:      501  540  39.0    529     818
Total:        501  544  41.1    533     828

Percentage of the requests served within a certain time (ms)
  50%    533
  66%    542
  75%    554
  80%    564
  90%    594
  95%    611
  98%    667
  99%    712
 100%    828 (longest request)
```
  
### How would you protect the server against being overloaded?
- Cloudflare or similar to protect from attacks
- Caching
- Monitor resources and then scale
