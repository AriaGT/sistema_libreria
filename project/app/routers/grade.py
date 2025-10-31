from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.schemas.grade import GradeCreate, GradeRead
from app.services import grade as grade_service

router = APIRouter(prefix="/grades", tags=["Grades"])


@router.get("/", response_model=List[GradeRead])
def list_grades(db: Session = Depends(get_db)) -> List[GradeRead]:
    grades = grade_service.get_grades(db)
    return grades


@router.post("/", response_model=GradeRead, status_code=status.HTTP_201_CREATED)
def create_grade(grade_in: GradeCreate, db: Session = Depends(get_db)) -> GradeRead:
    grade = grade_service.create_grade(db, grade_in)
    return grade


@router.get("/{grade_id}", response_model=GradeRead)
def get_grade(grade_id: int, db: Session = Depends(get_db)) -> GradeRead:
    grade = grade_service.get_grade_by_id(db, grade_id)
    if not grade:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Grade not found")
    return grade
