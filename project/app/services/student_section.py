from typing import List, Optional

from sqlalchemy.orm import Session

from app.models.student_section import StudentSection
from app.models.user import User
from app.schemas.student_section import StudentSectionCreate, StudentSectionUpdate


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


def update_enrollment(
    db: Session, section_id: int, enrollment_id: int, enrollment_in: StudentSectionUpdate
) -> Optional[StudentSection]:
    enrollment = get_enrollment_by_id(db, enrollment_id)
    if not enrollment or enrollment.section_id != section_id:
        return None

    update_data = enrollment_in.dict(exclude_unset=True)
    new_student_id = update_data.get("student_id")

    if new_student_id is not None:
        duplicate = (
            db.query(StudentSection.id)
            .filter(
                StudentSection.section_id == section_id,
                StudentSection.student_id == new_student_id,
                StudentSection.id != enrollment_id,
            )
            .first()
        )
        if duplicate:
            raise ValueError("Student already enrolled in this section")
        enrollment.student_id = new_student_id

    db.add(enrollment)
    db.commit()
    db.refresh(enrollment)
    return enrollment


def delete_enrollment(db: Session, section_id: int, enrollment_id: int) -> Optional[StudentSection]:
    enrollment = get_enrollment_by_id(db, enrollment_id)
    if not enrollment or enrollment.section_id != section_id:
        return None

    db.delete(enrollment)
    db.commit()
    return enrollment
