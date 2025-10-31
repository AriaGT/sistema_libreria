from typing import List, Optional

from sqlalchemy.orm import Session

from app.models.student_section import StudentSection
from app.models.user import User
from app.schemas.student_section import StudentSectionCreate


def enroll_student(db: Session, section_id: int, enrollment_in: StudentSectionCreate) -> StudentSection:
    existing = (
        db.query(StudentSection)
        .filter(
            StudentSection.section_id == section_id,
            StudentSection.student_id == enrollment_in.student_id,
        )
        .first()
    )
    if existing:
        raise ValueError("Student already enrolled in this section")

    enrollment = StudentSection(student_id=enrollment_in.student_id, section_id=section_id)
    db.add(enrollment)
    db.commit()
    db.refresh(enrollment)
    return enrollment


def get_enrollment_by_id(db: Session, enrollment_id: int) -> Optional[StudentSection]:
    return db.get(StudentSection, enrollment_id)


def get_students_in_section(db: Session, section_id: int) -> List[User]:
    return (
        db.query(User)
        .join(StudentSection, StudentSection.student_id == User.id)
        .filter(StudentSection.section_id == section_id)
        .order_by(User.id)
        .all()
    )
