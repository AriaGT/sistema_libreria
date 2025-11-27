from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.schemas.course import CourseCreate, CourseRead, CourseUpdate
from app.services import course as course_service
from app.services import section as section_service
from app.services import user as user_service

router = APIRouter(prefix="/sections/{section_id}/courses", tags=["Courses"])


@router.get("/", response_model=List[CourseRead])
def list_courses(section_id: int, db: Session = Depends(get_db)) -> List[CourseRead]:
    section = section_service.get_section_by_id(db, section_id)
    if not section:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Section not found")
    courses = course_service.get_courses_by_section(db, section_id)
    return courses


@router.post("/", response_model=CourseRead, status_code=status.HTTP_201_CREATED)
def create_course(section_id: int, course_in: CourseCreate, db: Session = Depends(get_db)) -> CourseRead:
    section = section_service.get_section_by_id(db, section_id)
    if not section:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Section not found")

    teacher = user_service.get_user_by_id(db, course_in.teacher_id)
    if not teacher:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Teacher not found")

    if course_in.section_id is not None and course_in.section_id != section_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="section_id mismatch with path parameter"
        )

    payload = CourseCreate(**course_in.dict(exclude={"section_id"}, exclude_unset=True), section_id=section_id)
    try:
        course = course_service.create_course(db, payload)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    return course


@router.patch("/{course_id}", response_model=CourseRead)
def update_course(
    section_id: int, course_id: int, course_in: CourseUpdate, db: Session = Depends(get_db)
) -> CourseRead:
    section = section_service.get_section_by_id(db, section_id)
    if not section:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Section not found")

    course = course_service.get_course_by_id(db, course_id)
    if not course or course.section_id != section_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Course not found")

    if course_in.section_id is not None and course_in.section_id != section_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="section_id mismatch with path parameter"
        )

    if course_in.teacher_id is not None:
        teacher = user_service.get_user_by_id(db, course_in.teacher_id)
        if not teacher:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Teacher not found")

    payload = CourseUpdate(**course_in.dict(exclude={"section_id"}, exclude_unset=True), section_id=section_id)
    try:
        course = course_service.update_course(db, course_id, payload)
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Unable to update course due to constraints"
        )

    if not course:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Course not found")
    return course


@router.delete("/{course_id}", response_model=CourseRead, status_code=status.HTTP_200_OK)
def delete_course(section_id: int, course_id: int, db: Session = Depends(get_db)) -> CourseRead:
    section = section_service.get_section_by_id(db, section_id)
    if not section:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Section not found")

    course = course_service.get_course_by_id(db, course_id)
    if not course or course.section_id != section_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Course not found")

    try:
        course = course_service.delete_course(db, course_id)
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete course because related books exist",
        )

    if not course:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Course not found")
    return course
