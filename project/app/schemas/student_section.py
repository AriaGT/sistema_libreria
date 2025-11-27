from pydantic import BaseModel, ConfigDict


class StudentSectionCreate(BaseModel):
    student_id: int


class StudentSectionUpdate(BaseModel):
    student_id: int | None = None


class StudentSectionRead(BaseModel):
    id: int
    student_id: int
    section_id: int

    model_config = ConfigDict(from_attributes=True)
