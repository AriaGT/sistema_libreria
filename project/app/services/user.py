from typing import List, Optional

from sqlalchemy.orm import Session

from app.core.security import hash_password
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate


def create_user(db: Session, user_in: UserCreate) -> User:
    user_data = user_in.dict()
    password = user_data.pop("password")
    user_data["password_hash"] = hash_password(password)
    user = User(**user_data)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def get_users(db: Session) -> List[User]:
    return db.query(User).all()


def get_user_by_id(db: Session, user_id: int) -> Optional[User]:
    return db.get(User, user_id)


def update_user(db: Session, user_id: int, user_in: UserUpdate) -> Optional[User]:
    user = get_user_by_id(db, user_id)
    if not user:
        return None

    update_data = user_in.dict(exclude_unset=True)
    password = update_data.pop("password", None)
    if password is not None:
        update_data["password_hash"] = hash_password(password)

    for field, value in update_data.items():
        setattr(user, field, value)

    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def delete_user(db: Session, user_id: int) -> Optional[User]:
    user = get_user_by_id(db, user_id)
    if not user:
        return None

    db.delete(user)
    db.commit()
    return user


def get_user_by_email(db: Session, email: str) -> Optional[User]:
    return db.query(User).filter(User.email == email).first()
