from pydantic import BaseModel, ConfigDict, EmailStr

from app.schemas.user import UserRead


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class LoginResponse(BaseModel):
    message: str
    user: UserRead

    model_config = ConfigDict(from_attributes=True)
