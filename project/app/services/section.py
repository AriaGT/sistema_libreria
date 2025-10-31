from typing import List, Optional

from sqlalchemy.orm import Session

from app.models.section import Section
from app.schemas.section import SectionCreate, SectionUpdate


def create_section(db: Session, section_in: SectionCreate) -> Section:
    if section_in.grade_id is None:
        raise ValueError("grade_id is required to create a section")

    section = Section(**section_in.dict())
    db.add(section)
    db.commit()
    db.refresh(section)
    return section


def get_sections_by_grade(db: Session, grade_id: int) -> List[Section]:
    return db.query(Section).filter(Section.grade_id == grade_id).order_by(Section.id).all()


def get_section_by_id(db: Session, section_id: int) -> Optional[Section]:
    return db.get(Section, section_id)


def update_section(db: Session, section_id: int, section_in: SectionUpdate) -> Optional[Section]:
    section = get_section_by_id(db, section_id)
    if not section:
        return None

    for field, value in section_in.dict(exclude_unset=True).items():
        setattr(section, field, value)

    db.add(section)
    db.commit()
    db.refresh(section)
    return section


def delete_section(db: Session, section_id: int) -> Optional[Section]:
    section = get_section_by_id(db, section_id)
    if not section:
        return None

    db.delete(section)
    db.commit()
    return section
