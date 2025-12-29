from fastapi import FastAPI
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware
from core.lifespan import lifespan
from core.middlewares.md_login_session import DBSessionMiddleware

# router import
from api.shop.routers import main_dashboard, login, signup, logout
from api.shop.routers.orders import orders 
from api.shop.routers.products import products
from api.shop.routers.carts import carts

# .env load
load_dotenv()

app = FastAPI(lifespan=lifespan)


app.add_middleware(
    DBSessionMiddleware,
    cookie_name="sid",
    path="/",
    secure=False, # 로컬 개발 환경용 (prod 배포시 True 권장 or env로 제어)
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# router
app.include_router(main_dashboard.router) 
app.include_router(login.router) 
app.include_router(signup.router) 
app.include_router(logout.router) 
app.include_router(orders.router) 
app.include_router(products.router) 
app.include_router(carts.router) 
