from fastapi import FastAPI
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware
from core.lifespan.lifespan import lifespan
import os
import logging

# router import
from api.shop.routers.login import login, signup, logout, my_page
from api.shop.routers.auth import refresh
from api.shop.routers.orders import orders 
from api.shop.routers.products import products
from api.shop.routers.category import category
from api.shop.routers.carts import carts
from api.shop.routers.admin import admin
from api.shop.routers.images import images
# from api.shop.routers.ai import ai_router



load_dotenv()

app = FastAPI(lifespan=lifespan)

LOG_LEVEL = os.getenv("LOG_LEVEL").upper()
LOG_FORMAT = os.getenv("LOG_FORMAT")
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL),
    format=LOG_FORMAT
)

CORS_ORIGINS = os.getenv("CORS_ORIGINS", "*").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health Check 엔드포인트 (Kubernetes Probes용)
@app.get("/health")
async def health_check():
    return {"status": "healthy"}

# router
app.include_router(login.router) 
app.include_router(signup.router) 
app.include_router(logout.router) 
app.include_router(refresh.router) 
app.include_router(my_page.router) 
app.include_router(orders.router) 
app.include_router(products.router) 
app.include_router(category.router)
app.include_router(carts.router) 
app.include_router(images.router)
# app.include_router(ai_router)
app.include_router(admin.router)
