from sqlalchemy import Column, DateTime, Integer, String
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.database.base import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(50), nullable=False)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())

    taught_courses = relationship(
        "Course", back_populates="teacher", foreign_keys="Course.teacher_id"
    )
    created_books = relationship(
        "Book", back_populates="creator", foreign_keys="Book.created_by"
    )
    student_sections = relationship("StudentSection", back_populates="student")
