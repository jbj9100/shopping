from fastapi import APIRouter
from schemas.sc_user import SignupIn
from db.conn_db import get_session
from services.login.svc_signup import signup_user
from fastapi import HTTPException
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from exceptions.user_exceptions import EmailAlreadyExistsError
from sqlalchemy.exc import IntegrityError

router = APIRouter(prefix="/api/shop/signup", tags=["signup"])  


@router.get("/")
def signup_get():
    return "signup"

@router.post("/")
async def signup_post(signup_in: SignupIn, session: AsyncSession = Depends(get_session)):
    try:
        user = await signup_user(session, signup_in)
        return {"ok": True, "id": user.id, "username": user.username, "email": user.email}
    except EmailAlreadyExistsError:
        raise HTTPException(status_code=400, detail="email already exists")
    except IntegrityError:
        raise HTTPException(status_code=400, detail="duplicate user creation attempt")