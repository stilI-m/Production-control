from fastapi import APIRouter
from fastapi.params import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.v1.schemas.batch import BatchResponse, BatchCreate
from src.core.database import get_async_session
from src.data.models import Batch

router = APIRouter(prefix="/batches", tags=["batches"])
@router.post("/batches", response_model=BatchResponse)
async def create_batches(batch: BatchCreate, session:AsyncSession = Depends(get_async_session)):
    data = batch.model_dump()
    new_batch = Batch(**data)
    session.add(new_batch)
    await session.commit()
    await session.refresh(new_batch)
    return new_batch
