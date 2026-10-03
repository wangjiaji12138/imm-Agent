"""Request IDs, bounded per-IP API rate and structured metadata only."""

import json
import logging
from collections import defaultdict, deque
from time import monotonic, perf_counter
from uuid import uuid4

from fastapi import Request
from fastapi.responses import JSONResponse

from app.core.settings import get_settings

logger = logging.getLogger("imm_agent.requests")
_requests: dict[str, deque[float]] = defaultdict(deque)


async def add_request_id(request: Request, call_next):
    request.state.request_id = str(uuid4())
    started = perf_counter()
    if request.url.path.startswith("/api/") and get_settings().environment == "production":
        client = request.client.host if request.client else "unknown"
        now = monotonic()
        arrivals = _requests[client]
        while arrivals and arrivals[0] <= now - 60:
            arrivals.popleft()
        if len(arrivals) >= get_settings().rate_limit_per_minute:
            response = JSONResponse(status_code=429, content={"error": {
                "code": "rate_limited", "message": "请求过于频繁，请稍后再试", "request_id": request.state.request_id}})
        else:
            arrivals.append(now)
            response = await call_next(request)
    else:
        response = await call_next(request)
    response.headers["X-Request-ID"] = request.state.request_id
    logger.info(json.dumps({"event": "http_request", "request_id": request.state.request_id,
                            "path": request.url.path, "method": request.method,
                            "status": response.status_code, "duration_ms": round((perf_counter() - started) * 1000, 2)}))
    return response
