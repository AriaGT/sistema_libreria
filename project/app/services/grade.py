from typing import List, Optional

from sqlalchemy.orm import Session

from app.models.grade import Grade
from app.schemas.grade import GradeCreate, GradeUpdate


def create_grade(db: Session, grade_in: GradeCreate) -> Grade:
    grade = Grade(**grade_in.dict())
    db.add(grade)
    db.commit()
    db.refresh(grade)
    return grade


def get_grades(db: Session) -> List[Grade]:
    return db.query(Grade).order_by(Grade.id).all()


def get_grade_by_id(db: Session, grade_id: int) -> Optional[Grade]:
    return db.get(Grade, grade_id)


def update_grade(db: Session, grade_id: int, grade_in: GradeUpdate) -> Optional[Grade]:
    grade = get_grade_by_id(db, grade_id)
    if not grade:
        return None

    for field, value in grade_in.dict(exclude_unset=True).items():
        setattr(grade, field, value)

    db.add(grade)
    db.commit()
    db.refresh(grade)
    return grade


def delete_grade(db: Session, grade_id: int) -> Optional[Grade]:
    grade = get_grade_by_id(db, grade_id)
    if not grade:
        return None

    db.delete(grade)
    db.commit()
    return grade
