from typing import List, Optional

from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.core.security import hash_password
from app.models.book import Book
from app.models.course import Course
from app.models.student_section import StudentSection
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

    # Prevent orphaned records by ensuring the user is not referenced elsewhere.
    teaches_courses = db.query(Course.id).filter(Course.teacher_id == user_id).first()
    if teaches_courses:
        raise ValueError("User is assigned as a teacher to existing courses")

    created_books = db.query(Book.id).filter(Book.created_by == user_id).first()
    if created_books:
        raise ValueError("User is referenced as the creator of existing books")

    # Clean up enrollments before deleting the user to avoid NOT NULL violations.
    db.query(StudentSection).filter(StudentSection.student_id == user_id).delete(
        synchronize_session=False
    )

    db.delete(user)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise

    return user


def get_user_by_email(db: Session, email: str) -> Optional[User]:
    return db.query(User).filter(User.email == email).first()
