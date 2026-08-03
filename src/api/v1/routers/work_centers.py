from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

# Импортируем нашу функцию получения сессии
from src.core.dependencies import get_db
from src.data.models.work_center import WorkCenter
from src.api.v1.schemas.work_center import WorkCenterCreate, WorkCenterResponse

# Создаем роутер. Префикс означает, что все пути внутри будут начинаться с /work_centers
router = APIRouter(prefix="/work_centers", tags=["work_centers"])

@router.post("/", response_model=WorkCenterResponse)
async def create_work_center(
        work_center_in: WorkCenterCreate,
        session: AsyncSession = Depends(get_db)
):
    # 1. Превращаем Pydantic-схему обратно в питоновский словарь
    data = work_center_in.model_dump()
    # 2. Создаем объект Алхимии (распаковываем словарь через **)
    new_work_center = WorkCenter(**data)
    # 3. Добавляем объект в текущую транзакцию
    session.add(new_work_center)
    # 4. Отправляем в базу (в этот момент база генерирует id, created_at)
    await session.commit()
    # 5. Обновляем наш объект, чтобы "подтянуть" из базы сгенерированные поля
    await session.refresh(new_work_center)
    # 6. Отдаем объект (FastAPI сам прогонит его через WorkCenterResponse)
    return new_work_center
