from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from models.user import User
from core.password_hash import hash_password
from fastapi import HTTPException
from schemas.user import Signup

# 회원가입으로 DB에 추가하는 작업
async def signup_user(session: AsyncSession, signup: Signup) -> User:
    # 전달받은 session객체로 작업을 수행
    # AsyncSession은 DB 트랜잭션을 포함한 “작업 단위(Unit of Work)”를 관리하는 객체고,
    # 그 안에서 실제 트랜잭션이 필요할 때 시작되고(commit/rollback으로 끝남)
    # 1) 중복 체크(친절한 에러를 주기 위해)
    r1 = await session.execute(select(User).where(User.username == signup.username))
    if r1.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="USERNAME_EXISTS")

    r2 = await session.execute(select(User).where(User.email == signup.email))
    if r2.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="EMAIL_EXISTS")

    # 2) 비밀번호 해싱 후 저장 (pydantic -> sqlalchemy 모델 변환)
    # created_dt는 auto_now_add=True로 설정되어있어서 넣지 않아도 commit시점에 자동으로 생성됨
    user = User (
        username=signup.username,
        email=signup.email,
        password_hash=hash_password(signup.password)
    )

    session.add(user)          # 여전히id와 created_dt는 없는 상태

    try:
        await session.commit()       # 여기서 자동으로 추가된다.
    except IntegrityError:
        await session.rollback()
        # 레이스 컨디션 대비(동시에 가입 요청 들어오면 여기 걸릴 수 있음)
        raise HTTPException(status_code=400, detail="DUPLICATE")

    await session.refresh(user)
    
    return user  # user 객체
