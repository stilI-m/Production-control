from fastapi.responses import JSONResponse

class AppException(Exception):
    """Базовый класс для всех кастомных ошибок приложения."""
    def __init__(self, status_code: int, detail: str):
        self.status_code = status_code
        self.detail = detail

class NotFoundError(AppException):
    def __init__(self, detail: str = "Ресурс не найден"):
        super().__init__(status_code=404, detail=detail)

class ValidationError(AppException):
    def __init__(self, detail: str = "Ошибка валидации данных"):
        super().__init__(status_code=400, detail=detail)

# Этот хэндлер мы подключим в main.py
async def app_exception_handler(exc: AppException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
    )