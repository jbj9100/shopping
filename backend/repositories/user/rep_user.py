from core.auth import auth_password_hash
from models.m_user import User
from sqlalchemy.orm import Session



def verify_(db: Session, user_update_in: UserUpdateIn) -> User:
    r = db.execute(select(User).where(User.email == user_update_in.email))
    user = r.scalar_one_or_none()
    return user


def update_mypage(db: Session, user_update_in: UserUpdateIn) -> User:
    r = db.execute(select(User).where(User.email == user_update_in.email))
    user = r.scalar_one_or_none()

    if user_update_in.username:
        user.username = user_update_in.username
    if user_update_in.password:
        user.password_hash = auth_password_hash.hash_password(user_update_in.password)
    return user