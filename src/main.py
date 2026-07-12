from fastapi import FastAPI
from src.core.config import settings

def create_app() -> FastAPI:
    app = FastAPI(title=settings.project_name, version=settings.version, docs_url='/api/docs')
    @app.get("/ping", tags=["Health"])
    async def health_check():
        return {"status": "ok", "project": settings.project_name}
    return app
app = create_app()
