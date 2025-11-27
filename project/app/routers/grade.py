from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.schemas.grade import GradeCreate, GradeRead, GradeUpdate
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


@router.patch("/{grade_id}", response_model=GradeRead)
def update_grade(grade_id: int, grade_in: GradeUpdate, db: Session = Depends(get_db)) -> GradeRead:
    try:
        grade = grade_service.update_grade(db, grade_id, grade_in)
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Grade update violated constraints"
        )

    if not grade:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Grade not found")
    return grade


@router.delete("/{grade_id}", response_model=GradeRead, status_code=status.HTTP_200_OK)
def delete_grade(grade_id: int, db: Session = Depends(get_db)) -> GradeRead:
    try:
        grade = grade_service.delete_grade(db, grade_id)
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete grade because related records still exist",
        )

    if not grade:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Grade not found")
    return grade
