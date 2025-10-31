from sqlalchemy import Column, ForeignKey, Integer, UniqueConstraint
from sqlalchemy.orm import relationship

from app.database.base import Base


class StudentSection(Base):
    __tablename__ = "student_sections"
    __table_args__ = (UniqueConstraint("student_id", "section_id", name="uq_student_section"),)

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    section_id = Column(Integer, ForeignKey("sections.id", ondelete="CASCADE"), nullable=False)

    student = relationship("User", back_populates="student_sections")
    section = relationship("Section", back_populates="student_sections")
