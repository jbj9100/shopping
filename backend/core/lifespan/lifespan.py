from contextlib import asynccontextmanager
from fastapi import FastAPI
from db.conn_db import dispose_engine, ping_db
from db.conn_redis import close_redis, ping_redis
from db.conn_minio import ping_minio, close_minio
from services.admin.svc_admin import create_admin

@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        # Database 연결 확인
        success, error = await ping_db()
        if not success:
            raise Exception(f"❌ Database connection failed: {error}")
        print("✅ Database connection successfully")

        # Redis 연결 확인
        success, error = await ping_redis()
        if not success:
            raise Exception(f"❌ Redis connection failed: {error}")
        print("✅ Redis connection successfully")
    
        # MinIO 연결 확인
        success, error = await ping_minio()
        if not success:
            raise Exception(f"❌ MinIO connection failed: {error}")
        print("✅ MinIO connection successfully")
        
        await create_admin()
        
        yield
    finally:
        await close_redis()
        await close_minio()
        await dispose_engine()
