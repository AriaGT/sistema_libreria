from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.schemas.student_section import StudentSectionCreate, StudentSectionRead
from app.schemas.user import UserRead
from app.services import section as section_service
from app.services import student_section as enrollment_service
from app.services import user as user_service

router = APIRouter(prefix="/sections/{section_id}", tags=["StudentSection"])


@router.post("/enroll", response_model=StudentSectionRead, status_code=status.HTTP_201_CREATED)
def enroll_student(
    section_id: int, enrollment_in: StudentSectionCreate, db: Session = Depends(get_db)
) -> StudentSectionRead:
    section = section_service.get_section_by_id(db, section_id)
    if not section:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Section not found")

    student = user_service.get_user_by_id(db, enrollment_in.student_id)
    if not student:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Student not found")

    try:
        enrollment = enrollment_service.enroll_student(db, section_id, enrollment_in)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    return enrollment


@router.get("/students", response_model=List[UserRead])
def list_students(section_id: int, db: Session = Depends(get_db)) -> List[UserRead]:
    section = section_service.get_section_by_id(db, section_id)
    if not section:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Section not found")
    students = enrollment_service.get_students_in_section(db, section_id)
    return students
