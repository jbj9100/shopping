from pydantic import BaseModel, Field , EmailStr
from .sc_common import APIModel
from typing import Optional

class LoginIn(APIModel):
    email: EmailStr = Field(
        ...,
        max_length=128,
        description="이메일"
    )
    password: str = Field(
        ...,
        min_length=6,          # 6자리 이상
        max_length=128,
        description="비밀번호 (6자 이상)"
    )


class SignupIn(LoginIn):
    username: str = Field(
        ...,
        max_length=30,
        pattern=r"^[a-z0-9]+$",
    )


class UserUpdateIn(APIModel):
    email: EmailStr = Field(
        ...,
        max_length=128,
        description="이메일"
    )
    username: Optional[str] = Field(
        None,
        max_length=30,
        pattern=r"^[a-z0-9]+$",
        description="사용자명 (영문 소문자와 숫자만)"
    )
    password: Optional[str] = Field(
        None,
        min_length=6,
        max_length=128,
        description="비밀번호 (6자 이상)"
    )
