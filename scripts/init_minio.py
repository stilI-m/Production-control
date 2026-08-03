import sys
import os

# Добавляем корень проекта в пути, чтобы скрипт мог импортировать из папки src
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.storage.minio_service import s3_client

def init_buckets():
    # Список всех бакетов, необходимых системе
    required_buckets = ["reports", "imports", 'exports']

    print("[MinIO-Init] Проверяю наличие бакетов...")

    for bucket_name in required_buckets:
        try:
            # Проверяем, существует ли уже бакет
            s3_client.head_bucket(Bucket=bucket_name)
            print(f"[MinIO-Init] Бакет '{bucket_name}' уже существует. Пропускаю.")
        except Exception:
            # Если упали с ошибкой — значит бакета нет, создаем его
            s3_client.create_bucket(Bucket=bucket_name)
            print(f"[MinIO-Init] Бакет '{bucket_name}' успешно создан автоматически!")

if __name__ == "__main__":
    init_buckets()