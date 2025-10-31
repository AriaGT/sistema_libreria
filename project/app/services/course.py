from typing import List, Optional

from sqlalchemy.orm import Session

from app.models.course import Course
from app.schemas.course import CourseCreate, CourseUpdate


def create_course(db: Session, course_in: CourseCreate) -> Course:
    if course_in.section_id is None:
        raise ValueError("section_id is required to create a course")

    course = Course(**course_in.dict())
    db.add(course)
    db.commit()
    db.refresh(course)
    return course


def get_courses_by_section(db: Session, section_id: int) -> List[Course]:
    return db.query(Course).filter(Course.section_id == section_id).order_by(Course.id).all()


def get_course_by_id(db: Session, course_id: int) -> Optional[Course]:
    return db.get(Course, course_id)


def update_course(db: Session, course_id: int, course_in: CourseUpdate) -> Optional[Course]:
    course = get_course_by_id(db, course_id)
    if not course:
        return None

    for field, value in course_in.dict(exclude_unset=True).items():
        setattr(course, field, value)

    db.add(course)
    db.commit()
    db.refresh(course)
    return course


def delete_course(db: Session, course_id: int) -> Optional[Course]:
    course = get_course_by_id(db, course_id)
    if not course:
        return None

    db.delete(course)
    db.commit()
    return course
