"""
Storage service that supports both local filesystem and cloud storage (R2/S3).
"""
import os
import hashlib
from typing import Optional
from io import BytesIO
from core.config import get_settings

settings = get_settings()


class StorageService:
    """Unified storage interface for local and cloud storage."""
    
    def __init__(self):
        self.use_cloud = settings.use_cloud_storage
        self._s3_client = None
        
        if self.use_cloud:
            # Validate cloud storage config
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
            # Ensure local directories exist
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
        
        Args:
            joke_id: The joke ID
            audio_bytes: The audio file content
            
        Returns:
            Public URL to access the audio file
        """
        filename = f"joke_{joke_id}_{hashlib.md5(audio_bytes).hexdigest()[:8]}.mp3"
        
        if self.use_cloud:
            # Upload to R2/S3
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
                return f"{self.public_url}/{key}"
            except ClientError as e:
                raise Exception(f"Failed to upload to cloud storage: {e}")
        else:
            # Save locally
            path = os.path.join(settings.media_dir, "audio", filename)
            with open(path, "wb") as f:
                f.write(audio_bytes)
            return f"/media/audio/{filename}"
    
    async def get_audio(self, url: str) -> Optional[bytes]:
        """
        Retrieve audio file content.
        
        Args:
            url: The URL or path to the audio file
            
        Returns:
            Audio file bytes or None if not found
        """
        if self.use_cloud:
            # Extract key from URL
            from botocore.exceptions import ClientError
            key = url.replace(f"{self.public_url}/", "")
            try:
                response = self.s3_client.get_object(Bucket=self.bucket, Key=key)
                return response['Body'].read()
            except ClientError:
                return None
        else:
            # Read from local filesystem
            path = os.path.join(settings.media_dir, "audio", os.path.basename(url))
            if os.path.exists(path):
                with open(path, "rb") as f:
                    return f.read()
            return None
    
    def get_audio_path(self, url: str) -> Optional[str]:
        """
        Get local file path for audio (only works for local storage).
        
        Args:
            url: The URL or path to the audio file
            
        Returns:
            Local file path or None
        """
        if self.use_cloud:
            return None
        return os.path.join(settings.media_dir, "audio", os.path.basename(url))


# Singleton instance
storage = StorageService()
