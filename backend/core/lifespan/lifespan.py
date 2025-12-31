from contextlib import asynccontextmanager
from fastapi import FastAPI
from db.db_conn import dispose_engine, ping_db
from db.redis_conn import close_redis, ping_redis

@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        if not await ping_db():
            raise Exception("Database connection failed")
        else:
            print("Database connection successful")

        if not await ping_redis():
            raise Exception("Redis connection failed")
        else:
            print("Redis connection successful")

        yield
    finally:
        await close_redis()
        await dispose_engine()