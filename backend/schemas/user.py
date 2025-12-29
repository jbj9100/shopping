from pydantic import BaseModel, Field , EmailStr

class Login(BaseModel):
    email: EmailStr = Field(
        ...,
        max_length=128,
    )
    password: str = Field(
        ...,
        min_length=6,          # 6자리 이상
        max_length=128,
    )

class Signup(Login):
    username: str = Field(
        ...,
        max_length=30,
        pattern=r"^[a-z]+$",   # 영문 소문자만
        description="lowercase letters only",
    )

