from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.v1.schemas.product import ProductResponse, ProductCreate
from src.core.database import get_async_session
from src.data.models import Product

router = APIRouter(prefix="/products", tags=["products"])

@router.post('/', response_model=ProductResponse)
async def create_product(product: ProductCreate, session: AsyncSession = Depends(get_async_session)):
    data = product.model_dump()
    new_product = Product(**data)
    session.add(new_product)
    await session.commit()
    await session.refresh(new_product)
    return new_product