from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """Базовый класс для всех моделей SQLAlchemy 2.0"""
    pass
from .work_center import WorkCenter
from .batch import Batch
from .product import Product
from src.data.models.webhook import WebhookSubscription, WebhookDelivery