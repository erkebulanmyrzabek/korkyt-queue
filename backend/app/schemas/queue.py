from __future__ import annotations

from pydantic import BaseModel, ConfigDict


class DashboardSummary(BaseModel):
    total_people_in_queue: int
    active_instructors: int
    available_instructors: int
    users_served_today: int


class TvQueueRow(BaseModel):
    queue_number: str
    status: str
    instructor_number: int | None = None


class CurrentEntry(BaseModel):
    queue_number: str
    iin: str | None = None
    photo_url: str | None = None


class InstructorActionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    instructor_id: int
    instructor_number: int
    status: str
    message: str
    current_entry: CurrentEntry | None = None

