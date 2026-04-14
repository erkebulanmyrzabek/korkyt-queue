from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class InstructorBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    login: str
    instructor_number: int
    status: str
    accepted_count: int
    is_active: bool


class InstructorCurrentEntry(BaseModel):
    queue_number: str
    iin: str | None = None
    photo_url: str | None = None


class CreateInstructorRequest(BaseModel):
    name: str = Field(min_length=2, max_length=120)
    login: str = Field(min_length=3, max_length=64)
    instructor_number: int = Field(ge=1)


class CreateInstructorResponse(BaseModel):
    instructor: InstructorBase
    generated_password: str


class InstructorLoginRequest(BaseModel):
    login: str = Field(min_length=3, max_length=64)
    password: str = Field(min_length=6, max_length=128)


class InstructorLoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    instructor: InstructorBase


class InstructorDashboardResponse(BaseModel):
    instructor: InstructorBase
    current_entry: InstructorCurrentEntry | None = None
