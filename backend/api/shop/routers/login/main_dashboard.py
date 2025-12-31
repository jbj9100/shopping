from fastapi import APIRouter
from core.deps.dep_auth_session import require_user
from fastapi import Request, Depends

router = APIRouter(prefix="/api/shop/main", tags=["main"])  

@router.get("/")
def main_page(request: Request, user=Depends(require_user)):
    
    return "main page"
