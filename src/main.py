from fastapi import FastAPI
from src.core.config import settings
from src.api.v1.routers.work_centers import router as work_centers_router
from src.api.v1.routers.products import router as products_router
from src.api.v1.routers.batches import router as batches_router
def create_app() -> FastAPI:
    app = FastAPI(title=settings.project_name, version=settings.version)
    app.include_router(work_centers_router, prefix="/api/v1")
    app.include_router(products_router, prefix="/api/v1")
    app.include_router(batches_router, prefix="/api/v1")
    return app
app = create_app()
