import uuid
from datetime import timedelta
from typing import Optional
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.concurrency import run_in_threadpool
from minio import Minio
from minio.error import S3Error
from fastapi import APIRouter





def get_minio(request: Request):
    svc = getattr(request.app.state, "minio", None)
    if svc is None:
        raise RuntimeError("MinIO not initialized")
    return svc