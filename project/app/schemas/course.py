from pydantic import BaseModel, ConfigDict


class CourseBase(BaseModel):
    name: str
    teacher_id: int


class CourseCreate(CourseBase):
    section_id: int | None = None


class CourseUpdate(BaseModel):
    name: str | None = None
    teacher_id: int | None = None
    section_id: int | None = None


class CourseRead(CourseBase):
    id: int
    section_id: int

    model_config = ConfigDict(from_attributes=True)
