from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from .sc_common import APIModel

class CategoryIn(APIModel):
    """카테고리 생성/수정 (요청 Body용 - id 없음)"""
    name: str = Field(..., min_length=1, max_length=50, pattern="^[a-z0-9-]+$")
    display_name: str = Field(..., min_length=1, max_length=100)
    icon: Optional[str] = Field(None, description="MinIO URL")
    description: Optional[str] = None


class CategoryOut(APIModel):
    """카테고리 응답 (id 포함)"""
    id: int
    name: str
    display_name: str
    icon: Optional[str]
    description: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
