from starlette.exceptions import HTTPException
import time

cache = {}


class RateLimitMiddleware:
    def __init__(self, app, max_requests: int = None, seconds: int = None) -> None:
        self.app = app
        self.seconds = seconds
        self.max_requests = max_requests

    async def __call__(self, scope, receive, send):
        ip = self._get_ip_client(scope)

        limit = self._get_limit(key=f"rate_limit:{ip}", cache=cache)

        self._validation_limit(limit)

        if limit:
            limit = self._increase_counter(limit)
        else:
            limit = self._set_counter(key=f"rate_limit:{ip}")

        start_time = limit.get("start_time", time.time())

        limit = self._reset_ttl_seconds(limit=limit, start_time=start_time)

        await self.app(scope, receive, send)

    def _get_ip_client(self, scope):
        return scope.get("client")[0]

    def _get_limit(self, key, cache):
        return cache.get(key)

    def _validation_limit(self, limit):
        if limit:
            request_count = limit.get("request_count", 1)

            if request_count >= self.max_requests:
                raise HTTPException(status_code=429, detail="Too many requests")

    def _increase_counter(self, limit):
        limit["request_count"] += 1
        return limit

    def _set_counter(self, key):
        cache[key] = {"request_count": 1, "start_time": time.time()}
        return cache[key]

    def _reset_ttl_seconds(self, start_time, limit) -> dict:
        current_time = time.time()

        if (current_time - start_time) >= self.seconds:
            limit["start_time"] = time.time()
            limit["request_count"] = 1

        return limit
