# fastapi-rate-limit

Middleware for rate limit


## Usage

```Python
from fastapi import FastAPI
from rate_limit import RateLimitMiddleware


app = FastAPI()

# Adiciona o middleware com limite de 100 requisições por 60 segundos
app.add_middleware(RateLimitMiddleware, max_requests=100, seconds=60)


@app.get("/")
async def root():
    return {"message": "Hello RateLimitMiddleware"}

```
