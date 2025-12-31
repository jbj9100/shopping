






    client = create_minio_client(
        endpoint=settings.MINIO_ENDPOINT,
        access_key=settings.MINIO_ACCESS_KEY,
        secret_key=settings.MINIO_SECRET_KEY,
        secure=settings.MINIO_SECURE,
    )
    minio_svc = MinioService(client=client, bucket=settings.MINIO_BUCKET)


def ensure_bucket():
    # 버킷 없으면 생성
    found = minio_client.bucket_exists(MINIO_BUCKET)
    if not found:
        minio_client.make_bucket(MINIO_BUCKET)    