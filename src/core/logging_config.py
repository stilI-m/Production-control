import logging
import os
from logging.handlers import RotatingFileHandler

# Папка для логов внутри контейнера или проекта
LOG_DIR = "logs"
LOG_FILE = os.path.join(LOG_DIR, "app.log")

def setup_logging():
    """Настройка глобального логирования приложения."""
    if not os.path.exists(LOG_DIR):
        os.makedirs(LOG_DIR)

    # Формат записи: Время | Уровень | Модуль:Функция:Строка - Сообщение
    log_format = logging.Formatter(
        "%(asctime)s | %(levelname)-8s | %(name)s:%(funcName)s:%(lineno)d - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)

    # 1. Вывод в Консоль (чтобы видеть в `docker compose logs`)
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(log_format)
    console_handler.setLevel(logging.INFO)

    # 2. Ротируемый файл логов (максимум 5MB один файл, храним 5 последних файлов)
    file_handler = RotatingFileHandler(
        LOG_FILE,
        maxBytes=5 * 1024 * 1024,  # 5 MB
        backupCount=5,
        encoding="utf-8"
    )
    file_handler.setFormatter(log_format)
    file_handler.setLevel(logging.INFO)

    # Очищаем старые хэндлеры, чтобы не дублировались логи при перезапусках
    root_logger.handlers.clear()

    root_logger.addHandler(console_handler)
    root_logger.addHandler(file_handler)

    # Приглушаем слишком частые логи сторонних библиотек (например, SQLAlchemy или httpx)
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("asyncio").setLevel(logging.WARNING)