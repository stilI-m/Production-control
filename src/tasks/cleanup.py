from datetime import datetime, timezone, timedelta
from src.celery_app import celery_app
from src.storage.minio_service import s3_client
import logging
logger = logging.getLogger(__name__)
@celery_app.task
def cleanup_old_exports_task(days: int = 1):
    bucket_name = "exports"
    threshold_time = datetime.now(timezone.utc) - timedelta(days=days)
    deleted_count = 0

    try:
        continuation_token = None
        while True:
            list_kwargs = {"Bucket": bucket_name}
            if continuation_token:
                list_kwargs["ContinuationToken"] = continuation_token

            response = s3_client.list_objects_v2(**list_kwargs)

            if "Contents" in response:
                for obj in response["Contents"]:
                    if obj["LastModified"] < threshold_time:
                        s3_client.delete_object(Bucket=bucket_name, Key=obj["Key"])
                        deleted_count += 1

            # Проверяем, есть ли следующая страница файлов
            if response.get("IsTruncated"):
                continuation_token = response.get("NextContinuationToken")
            else:
                break

        logger.info("Успешно удалено %d старых файлов из бакета '%s'", deleted_count, bucket_name)
        return {"success": True, "deleted_count": deleted_count}
    except Exception as e:
        logger.exception("Не удалось выполнить очистку старых файлов в бакете '%s'", bucket_name)
        return {"success": False, "error": str(e)}