from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from loguru import logger

from app.api.routes import health, users
from app.core.config import get_settings
from app.core.logging import configure_logging
from app.domain.exceptions import AppError
from app.infrastructure.persistence.mongodb.database import (
    close_mongo_connection,
    init_database,
)


@asynccontextmanager
async def lifespan(_: FastAPI):
    configure_logging()
    settings = get_settings()
    logger.info("Starting {} in {} mode", settings.app_name, settings.app_env)
    await init_database()
    try:
        yield
    finally:
        await close_mongo_connection()
        logger.info("Application shutdown complete")


def create_app() -> FastAPI:
    settings = get_settings()
    application = FastAPI(
        title=settings.app_name,
        version="0.2.0",
        lifespan=lifespan,
    )
    application.include_router(health.router)
    application.include_router(users.router)

    @application.exception_handler(AppError)
    async def handle_app_error(_: Request, exc: AppError) -> JSONResponse:
        return JSONResponse(
            status_code=exc.status_code,
            content={"detail": exc.message},
        )

    return application


app = create_app()
