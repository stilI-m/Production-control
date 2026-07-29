from datetime import datetime, timezone, timedelta
from src.celery_app import celery_app
from src.storage.minio_service import s3_client


@celery_app.task
def cleanup_old_exports_task(days: int = 1):
    """
    Периодическая задача Celery Beat:
    Удаляет из бакета 'exports' файлы, созданные более N дней назад.
    """
    bucket_name = "exports"
    threshold_time = datetime.now(timezone.utc) - timedelta(days=days)
    deleted_count = 0

    try:
        # Получаем список всех объектов в бакете exports
        response = s3_client.list_objects_v2(Bucket=bucket_name)

        if "Contents" in response:
            for obj in response["Contents"]:
                # LastModified из boto3 уже приходит в UTC
                last_modified = obj["LastModified"]

                if last_modified < threshold_time:
                    s3_client.delete_object(Bucket=bucket_name, Key=obj["Key"])
                    deleted_count += 1


        return {"success": True, "deleted_count": deleted_count}
    except Exception as e:
        return {"success": False, "error": str(e)}