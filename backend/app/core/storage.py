import boto3
from botocore.client import Config
import asyncio, io, logging
from concurrent.futures import ThreadPoolExecutor
from app.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()
_executor = ThreadPoolExecutor(max_workers=4)

def _client():
    return boto3.client("s3", endpoint_url=settings.S3_ENDPOINT_URL, aws_access_key_id=settings.S3_ACCESS_KEY, aws_secret_access_key=settings.S3_SECRET_KEY, region_name=settings.S3_REGION, config=Config(signature_version="s3v4"))

def _ensure_bucket(client):
    try:
        client.head_bucket(Bucket=settings.S3_BUCKET)
    except Exception:
        client.create_bucket(Bucket=settings.S3_BUCKET)

def upload_file_sync(file_path, s3_key, content_type="video/mp4"):
    c = _client()
    _ensure_bucket(c)
    c.upload_file(file_path, settings.S3_BUCKET, s3_key, ExtraArgs={"ContentType": content_type})
    return get_public_url(s3_key)

def upload_bytes_sync(data, s3_key, content_type="image/jpeg"):
    c = _client()
    _ensure_bucket(c)
    c.upload_fileobj(io.BytesIO(data), settings.S3_BUCKET, s3_key, ExtraArgs={"ContentType": content_type})
    return get_public_url(s3_key)

async def upload_file(file_path, s3_key, content_type="video/mp4"):
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(_executor, upload_file_sync, file_path, s3_key, content_type)

def get_public_url(s3_key):
    return f"{settings.S3_ENDPOINT_URL}/{settings.S3_BUCKET}/{s3_key}"