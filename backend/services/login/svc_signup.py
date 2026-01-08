from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from models.m_user import User
from core.auth.auth_password_hash import hash_password
from schemas.sc_user import SignupIn
from exceptions.user_exceptions import EmailAlreadyExistsError
from repositories.users.rep_admin import create_user
from repositories.users.rep_common import get_user_by_email


# 회원가입으로 DB에 추가하는 작업
async def signup_user(session: AsyncSession, signup: SignupIn) -> User:
    # 1) 중복 체크(친절한 에러를 주기 위해)

    email = await get_user_by_email(session, signup.email)
    if email:
        raise EmailAlreadyExistsError(signup.email)

    # 2) 비밀번호 해싱 후 저장 (pydantic -> sqlalchemy 모델 변환)
    # created_dt는 auto_now_add=True로 설정되어있어서 넣지 않아도 commit시점에 자동으로 생성됨
    user = await create_user(session, signup.username, signup.email, hash_password(signup.password))

    try:
        await session.commit()       # 여기서 자동으로 추가된다.
    except IntegrityError as e:
        await session.rollback()
        # 레이스 컨디션 대비(동시에 가입 요청 들어오면 여기 걸릴 수 있음)
        raise e

    await session.refresh(user)
    
    return user  # user 객체
