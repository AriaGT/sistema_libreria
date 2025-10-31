from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.schemas.section import SectionCreate, SectionRead
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
