from pydantic import BaseModel, ConfigDict


class GradeBase(BaseModel):
    name: str


class GradeCreate(GradeBase):
    pass


class GradeUpdate(BaseModel):
    name: str | None = None


class GradeRead(GradeBase):
    id: int

    model_config = ConfigDict(from_attributes=True)
