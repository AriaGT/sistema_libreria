from pydantic import BaseModel, ConfigDict


class SectionBase(BaseModel):
    name: str


class SectionCreate(SectionBase):
    grade_id: int | None = None


class SectionUpdate(BaseModel):
    name: str | None = None
    grade_id: int | None = None


class SectionRead(SectionBase):
    id: int
    grade_id: int

    model_config = ConfigDict(from_attributes=True)
