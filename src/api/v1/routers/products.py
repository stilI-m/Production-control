from pydantic import BaseModel
from fastapi import APIRouter, Depends, HTTPException, status

from src.core.dependencies import get_product_service
from src.domain.services.product_service import ProductService
from src.api.v1.schemas.product import ProductResponse

router = APIRouter(prefix="/products", tags=["Products"])

# Вспомогательная схема для входящего запроса агрегации (если её еще нет)
class AggregateRequest(BaseModel):
    batch_id: int
    code: str

@router.post("/aggregate", response_model=ProductResponse)
async def aggregate_product(
        data: AggregateRequest,
        product_service: ProductService = Depends(get_product_service),
):
    """
    Агрегирует продукт. Если код верный, пометит как агрегированный
    и автоматически очистит кэш дашборда и партии.
    """
    product = await product_service.aggregate_product(
        batch_id=data.batch_id,
        code=data.code
    )

    if not product:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Продукт не найден, не принадлежит партии или уже агрегирован"
        )

    return product