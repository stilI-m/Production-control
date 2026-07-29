from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware import Middleware
from fastapi.middleware.cors import CORSMiddleware

from src.core.config import settings

from src.api.v1.routers.work_centers import router as work_centers_router
from src.api.v1.routers.products import router as products_router
from src.api.v1.routers.batches import router as batches_router
from src.api.v1.routers.webhooks import router as webhooks_router
from src.api.v1.routers.tasks import router as tasks_router

from src.core.exceptions import AppException, app_exception_handler

from src.core.logging_config import setup_logging
import logging

setup_logging()
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(fastapi_app: FastAPI):
    logger.info("Приложение успешно запущено и логирование настроено")
    yield
    logger.info("Приложение останавливается. Закрытие соединений...")


def create_app() -> FastAPI:
    middleware = [
        Middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
    ]

    # Передаем middleware сразу при создании приложения
    app = FastAPI(
        title=settings.project_name,
        version=settings.version,
        lifespan=lifespan,
        middleware=middleware
    )
    app.add_exception_handler(AppException, app_exception_handler)
    # Подключаем роутеры
    app.include_router(work_centers_router, prefix="/api/v1")
    app.include_router(products_router, prefix="/api/v1")
    app.include_router(batches_router, prefix="/api/v1")
    app.include_router(webhooks_router, prefix="/api/v1")
    app.include_router(tasks_router, prefix="/api/v1")


    return app


app = create_app()