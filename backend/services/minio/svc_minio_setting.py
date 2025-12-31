from minio import Minio
import os


@dataclass(frozen=True)
class MinioSettings:
    minio_endpoint: str
    minio_access_key: str
    minio_secret_key: str
    minio_bucket: str
    minio_secure: bool
    minio_public_base_url: str

    @staticmethod
    def from_env() -> "MinioSettings":
        secure = os.getenv("MINIO_SECURE", "false").lower() == "true"
        return MinioSettings(
            minio_endpoint=os.getenv("MINIO_ENDPOINT", "localhost:9000"),
            minio_access_key=os.getenv("MINIO_ACCESS_KEY", "minio"),
            minio_secret_key=os.getenv("MINIO_SECRET_KEY", "minio123"),
            minio_bucket=os.getenv("MINIO_BUCKET", "product"),
            minio_secure=secure,
            minio_public_base_url=os.getenv("MINIO_PUBLIC_BASE_URL", "http://localhost:9000").rstrip("/"),
        )
ImageContentType = Literal["image/jpeg", "image/png", "image/webp", "image/gif"]

@dataclass(frozen=True)
class MinioObjectRef:
    bucket: str
    object_name: str


@dataclass(frozen=True)
class UploadResult:
    ref: MinioObjectRef
    url: str
    content_type: str
    size: int