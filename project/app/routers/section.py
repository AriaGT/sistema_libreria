from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.schemas.section import SectionCreate, SectionRead, SectionUpdate
from app.services import grade as grade_service
from app.services import section as section_service

router = APIRouter(prefix="/grades/{grade_id}/sections", tags=["Sections"])


@router.get("/", response_model=List[SectionRead])
def list_sections(grade_id: int, db: Session = Depends(get_db)) -> List[SectionRead]:
    grade = grade_service.get_grade_by_id(db, grade_id)
    if not grade:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Grade not found")
    sections = section_service.get_sections_by_grade(db, grade_id)
    return sections


@router.post("/", response_model=SectionRead, status_code=status.HTTP_201_CREATED)
def create_section(grade_id: int, section_in: SectionCreate, db: Session = Depends(get_db)) -> SectionRead:
    grade = grade_service.get_grade_by_id(db, grade_id)
    if not grade:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Grade not found")

    if section_in.grade_id is not None and section_in.grade_id != grade_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="grade_id mismatch with path parameter"
        )

    payload = SectionCreate(**section_in.dict(exclude={"grade_id"}, exclude_unset=True), grade_id=grade_id)
    try:
        section = section_service.create_section(db, payload)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    return section


@router.patch("/{section_id}", response_model=SectionRead)
def update_section(
    grade_id: int, section_id: int, section_in: SectionUpdate, db: Session = Depends(get_db)
) -> SectionRead:
    grade = grade_service.get_grade_by_id(db, grade_id)
    if not grade:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Grade not found")

    section = section_service.get_section_by_id(db, section_id)
    if not section or section.grade_id != grade_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Section not found")

    if section_in.grade_id is not None and section_in.grade_id != grade_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="grade_id mismatch with path parameter"
        )

    payload = SectionUpdate(**section_in.dict(exclude={"grade_id"}, exclude_unset=True), grade_id=grade_id)
    try:
        section = section_service.update_section(db, section_id, payload)
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Unable to update section due to constraints"
        )

    if not section:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Section not found")
    return section


@router.delete("/{section_id}", response_model=SectionRead, status_code=status.HTTP_200_OK)
def delete_section(grade_id: int, section_id: int, db: Session = Depends(get_db)) -> SectionRead:
    grade = grade_service.get_grade_by_id(db, grade_id)
    if not grade:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Grade not found")

    section = section_service.get_section_by_id(db, section_id)
    if not section or section.grade_id != grade_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Section not found")

    try:
        section = section_service.delete_section(db, section_id)
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete section because related courses or enrollments exist",
        )

    if not section:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Section not found")
    return section
