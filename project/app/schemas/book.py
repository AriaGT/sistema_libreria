from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class BookBase(BaseModel):
    title: str
    author: str
    description: Optional[str] = None
    file_url: str
    category: Optional[str] = None


class BookCreate(BookBase):
    course_id: Optional[int] = None
    created_by: int


class BookUpdate(BaseModel):
    title: Optional[str] = None
    author: Optional[str] = None
    description: Optional[str] = None
    file_url: Optional[str] = None
    category: Optional[str] = None
    course_id: Optional[int] = None
    created_by: Optional[int] = None


class BookRead(BookBase):
    id: int
    course_id: int
    created_by: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
