from fastapi import APIRouter, Request




router = APIRouter(prefix="/api/carts", tags=["carts"])


@router.get("/")
def cart_get(request: Request,
            user=Depends(require_user)):
    return {"message": "cart page"}


@router.post("/")
def cart_item_add(request: Request,
            user=Depends(require_user)):
    return {"message": "cart page"}

@router.patch("/")
def cart_item_update(request: Request,
            user=Depends(require_user)):
    return {"message": "cart page"}

@router.delete("/")
def cart_item_delete(request: Request,
            user=Depends(require_user)):
    return {"message": "cart page"}    


@router.delete("/all")
def cart_item_all_delete(request: Request,
            user=Depends(require_user)):
    return {"message": "cart page"}    