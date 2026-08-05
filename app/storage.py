import os
import shutil
import uuid
import logging

logger = logging.getLogger("storage")

STORAGE_MODE = os.getenv("STORAGE_MODE", "local") # "local" or "s3"
AWS_S3_BUCKET = os.getenv("AWS_S3_BUCKET", "healthid-ai-uploads")
LOCAL_UPLOAD_DIR = os.getenv("LOCAL_UPLOAD_DIR", "app/public/uploads")

os.makedirs(LOCAL_UPLOAD_DIR, exist_ok=True)

def upload_file(file_bytes: bytes, filename: str, content_type: str = "application/octet-stream") -> str:
    """Uploads file to configured storage engine and returns file URI/path."""
    ext = os.path.splitext(filename)[1].lower()
    unique_filename = f"{uuid.uuid4().hex}{ext}"

    if STORAGE_MODE == "s3":
        try:
            import boto3
            s3_client = boto3.client("s3")
            s3_client.put_object(
                Bucket=AWS_S3_BUCKET,
                Key=unique_filename,
                Body=file_bytes,
                ContentType=content_type
            )
            return f"s3://{AWS_S3_BUCKET}/{unique_filename}"
        except Exception as e:
            logger.error(f"S3 upload failed, falling back to local storage: {e}")

    # Local fallback
    dest_path = os.path.join(LOCAL_UPLOAD_DIR, unique_filename)
    with open(dest_path, "wb") as f:
        f.write(file_bytes)
    
    return f"/uploads/{unique_filename}"

def generate_presigned_url(file_path_or_key: str, expires_in: int = 3600) -> str:
    """Generates presigned URL for S3 or returns local file path."""
    if file_path_or_key.startswith("s3://"):
        try:
            import boto3
            parts = file_path_or_key.replace("s3://", "").split("/", 1)
            bucket, key = parts[0], parts[1]
            s3_client = boto3.client("s3")
            return s3_client.generate_presigned_url(
                "get_object",
                Params={"Bucket": bucket, "Key": key},
                ExpiresIn=expires_in
            )
        except Exception as e:
            logger.error(f"Failed to generate S3 presigned URL: {e}")
            return file_path_or_key
            
    return file_path_or_key
