import logging
import os
import boto3
from botocore.exceptions import ClientError
from botocore.client import Config

logger = logging.getLogger(__name__)
# Настройки: если переменной нет (локальный FastAPI), берем localhost.
# Если переменная есть (в контейнере воркера), берем её.
MINIO_ENDPOINT = os.getenv("MINIO_ENDPOINT", "http://minio:9000")
MINIO_ACCESS_KEY = os.getenv("MINIO_ACCESS_KEY", "admin")
MINIO_SECRET_KEY = os.getenv("MINIO_SECRET_KEY", "minioadmin123")

# Создаем единый клиент для работы с хранилищем
s3_client = boto3.client(
    "s3",
    endpoint_url=MINIO_ENDPOINT,
    aws_access_key_id=MINIO_ACCESS_KEY,
    aws_secret_access_key=MINIO_SECRET_KEY,
    region_name="us-east-1",  # Для MinIO это формальность, но boto3 требует
    config= Config(s3 = {'addressing_style' : 'path'})
)



def upload_file_to_minio(file_bytes: bytes, object_name: str, bucket_name: str = "imports") -> str:
    """Загружает байты файла в указанный бакет MinIO"""
    try:
        s3_client.put_object(
            Bucket=bucket_name,
            Key=object_name,
            Body=file_bytes,
            ContentLength=len(file_bytes)
        )
        return object_name
    except Exception:
        logger.exception("Ошибка загрузки файла %s в бакет %s", object_name, bucket_name)
        raise
def get_presigned_url(object_name: str, bucket_name: str = "exports", expires_in: int = 3600) -> str | None:
    """
    Генерирует временную ссылку (Presigned URL) для прямого скачивания файла из MinIO.
    expires_in: время жизни ссылки в секундах (по умолчанию 1 час).
    """
    try:
        url = s3_client.generate_presigned_url(
            ClientMethod='get_object',
            Params={
                'Bucket': bucket_name,
                'Key': object_name
            },
            ExpiresIn=expires_in
        )
        return url
    except Exception:
        logger.exception("Ошибка при генерации ссылки для %s", object_name)
        return None
def download_file_from_minio(file_url: str, local_path: str, bucket_name: str = "imports") -> bool:
    """
    Скачивает файл из MinIO по его URL или ключу объекта (object_name)
    и сохраняет по пути local_path.
    """
    # Если file_url - это полная ссылка (http://minio:9000/bucket/file.xlsx),
    # нам нужно вытащить из нее только имя файла (ключ объекта).
    # Если передается сразу имя файла, то object_name = file_url
    object_name = file_url.split("/")[-1] if "http" in file_url else file_url

    logger.info("Попытка скачать файл %s из бакета %s в %s...", object_name, bucket_name, local_path)

    try:
        # Убедимся, что директория для сохранения существует (например /tmp/)
        os.makedirs(os.path.dirname(local_path), exist_ok=True)

        # Скачиваем файл
        s3_client.download_file(bucket_name, object_name, local_path)
        logger.info("Файл успешно скачан: %s", local_path)
        return True

    except ClientError:
        logger.exception("Ошибка скачивания файла %s в бакет %s", object_name, bucket_name)
        raise