from fastapi import FastAPI

from app.infrastructure.logging import setup_logging
from app.interfaces.api.middleware import trace_middleware
from app.interfaces.api.routes import router


def create_app() -> FastAPI:
    setup_logging()

    app = FastAPI(
        title="Mini-Marketplace",
        version="0.1.0",
        description="Учебный проект"
    )

    app.middleware("http")(trace_middleware)
    app.include_router(router)

    return app

app = create_app()