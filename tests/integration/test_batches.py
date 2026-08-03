import pytest

@pytest.mark.asyncio
async def test_get_batches_empty(client):
    """
    Проверяем, что эндпоинт получения партий возвращает пустой список
    на абсолютно чистой тестовой базе данных.
    """
    # Заменяем URL на актуальный путь из твоего роутера batches_router
    response = await client.get("/api/v1/batches/")

    # Ожидаем успешный ответ
    assert response.status_code == 200

    # Ожидаем пустой список (так как база только что создана и пуста)
    assert response.json() == []