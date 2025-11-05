from typing import Optional

from sqlalchemy.orm import Session

from app.core.security import verify_password
from app.models.user import User
from app.services import user as user_service


def authenticate_user(db: Session, email: str, password: str) -> Optional[User]:
    user = user_service.get_user_by_email(db, email)
    if not user:
        return None
    if not verify_password(password, user.password_hash):
        return None
    return user
