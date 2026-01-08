from contextlib import asynccontextmanager
from fastapi import FastAPI
from db.conn_db import dispose_engine, ping_db
from db.conn_redis import close_redis, ping_redis
from db.conn_minio import ping_minio, close_minio
from services.admin.svc_admin import create_admin

@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        if not await ping_db():
            raise Exception("Database connection failed")
        else:
            print("Database connection successfully")

        if not await ping_redis():
            raise Exception("Redis connection failed")
        else:
            print("Redis connection successfully")

        if not await ping_minio():
            raise Exception("MinIO connection failed")
        else:
            print("MinIO connection successfully")
        await create_admin()
        yield
    finally:
        await close_redis()
        await close_minio()
        await dispose_engine()
