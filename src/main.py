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

@asynccontextmanager
async def lifespan(fastapi_app: FastAPI):
    print("🚀 Старт сервера...")
    yield
    print("🛑 Остановка сервера...")


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