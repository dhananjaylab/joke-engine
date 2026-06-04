"""
Storage service that supports both local filesystem and cloud storage (R2/S3).
"""
import os
import hashlib
import time
from typing import Optional

from core.config import get_settings
from core.logging import get_logger

settings = get_settings()
log = get_logger("services.storage")


class StorageService:
    """Unified storage interface for local and cloud storage."""

    def __init__(self):
        self.use_cloud = settings.use_cloud_storage
        self._s3_client = None

        if self.use_cloud:
            if not all([
                settings.s3_endpoint_url,
                settings.s3_access_key_id,
                settings.s3_secret_access_key,
                settings.s3_bucket_name,
                settings.s3_public_url
            ]):
                raise ValueError(
                    "Cloud storage is enabled but configuration is incomplete. "
                    "Please set S3_ENDPOINT_URL, S3_ACCESS_KEY_ID, S3_SECRET_ACCESS_KEY, "
                    "S3_BUCKET_NAME, and S3_PUBLIC_URL in your .env file."
                )
            self.bucket = settings.s3_bucket_name
            self.public_url = settings.s3_public_url
        else:
            os.makedirs(settings.media_dir, exist_ok=True)
            os.makedirs(os.path.join(settings.media_dir, "audio"), exist_ok=True)

    @property
    def s3_client(self):
        """Lazy initialization of S3 client."""
        if self._s3_client is None and self.use_cloud:
            import boto3
            self._s3_client = boto3.client(
                's3',
                endpoint_url=settings.s3_endpoint_url,
                aws_access_key_id=settings.s3_access_key_id,
                aws_secret_access_key=settings.s3_secret_access_key,
            )
        return self._s3_client

    async def save_audio(self, joke_id: int, audio_bytes: bytes) -> str:
        """
        Save audio file and return the public URL.
        """
        filename = f"joke_{joke_id}_{hashlib.md5(audio_bytes).hexdigest()[:8]}.mp3"
        start = time.perf_counter()

        if self.use_cloud:
            from botocore.exceptions import ClientError
            key = f"audio/{filename}"
            try:
                self.s3_client.put_object(
                    Bucket=self.bucket,
                    Key=key,
                    Body=audio_bytes,
                    ContentType='audio/mpeg',
                    CacheControl='public, max-age=604800',
                )
                url = f"{self.public_url}/{key}"
                duration_ms = int((time.perf_counter() - start) * 1000)
                await log.info(
                    "storage_upload_complete",
                    f"Audio uploaded to cloud: {key} ({len(audio_bytes)} bytes) in {duration_ms}ms",
                    joke_id=joke_id,
                    duration_ms=duration_ms,
                    details={"key": key, "bytes": len(audio_bytes), "url": url},
                )
                return url
            except ClientError as exc:
                duration_ms = int((time.perf_counter() - start) * 1000)
                await log.error(
                    "storage_upload_failed",
                    f"Cloud upload failed for joke {joke_id}",
                    joke_id=joke_id,
                    duration_ms=duration_ms,
                    exc=exc,
                )
                raise Exception(f"Failed to upload to cloud storage: {exc}")
        else:
            path = os.path.join(settings.media_dir, "audio", filename)
            with open(path, "wb") as f:
                f.write(audio_bytes)
            url = f"/media/audio/{filename}"
            duration_ms = int((time.perf_counter() - start) * 1000)
            await log.info(
                "storage_local_save",
                f"Audio saved locally: {path} ({len(audio_bytes)} bytes) in {duration_ms}ms",
                joke_id=joke_id,
                duration_ms=duration_ms,
                details={"path": path, "bytes": len(audio_bytes)},
            )
            return url

    async def get_audio(self, url: str) -> Optional[bytes]:
        """
        Retrieve audio file content.
        """
        start = time.perf_counter()

        if self.use_cloud:
            from botocore.exceptions import ClientError
            key = url.replace(f"{self.public_url}/", "")
            try:
                response = self.s3_client.get_object(Bucket=self.bucket, Key=key)
                data = response['Body'].read()
                duration_ms = int((time.perf_counter() - start) * 1000)
                await log.debug(
                    "storage_cloud_fetch",
                    f"Audio fetched from cloud: {key} ({len(data)} bytes) in {duration_ms}ms",
                    duration_ms=duration_ms,
                    details={"key": key, "bytes": len(data)},
                )
                return data
            except ClientError as exc:
                await log.warning(
                    "storage_cloud_fetch_failed",
                    f"Cloud audio fetch failed for key derived from {url}",
                    exc=exc,
                )
                return None
        else:
            path = os.path.join(settings.media_dir, "audio", os.path.basename(url))
            if os.path.exists(path):
                with open(path, "rb") as f:
                    data = f.read()
                duration_ms = int((time.perf_counter() - start) * 1000)
                await log.debug(
                    "storage_local_fetch",
                    f"Audio fetched from disk: {path} ({len(data)} bytes) in {duration_ms}ms",
                    duration_ms=duration_ms,
                )
                return data
            await log.warning("storage_local_missing", f"Audio file not found on disk: {path}")
            return None

    def get_audio_path(self, url: str) -> Optional[str]:
        """Get local file path for audio (only works for local storage)."""
        if self.use_cloud:
            return None
        return os.path.join(settings.media_dir, "audio", os.path.basename(url))


# Singleton instance
storage = StorageService()
