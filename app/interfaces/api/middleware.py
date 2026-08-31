import uuid

import structlog
from fastapi import Request


async def trace_middleware(request: Request, call_next):
    """Добавляет trace_id в каждый запрос."""
    trace_id = str(uuid.uuid4())
    request.state.trace_id = trace_id
    
    structlog.contextvars.bind_contextvars(trace_id=trace_id)
    
    response = await call_next(request)
    
    structlog.contextvars.unbind_contextvars("trace_id")
    return response