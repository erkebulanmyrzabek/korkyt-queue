from enum import Enum


class QueueStatus(str, Enum):
    waiting = "waiting"
    assigned = "assigned"
    in_service = "in_service"
    completed = "completed"
    cancelled = "cancelled"


class InstructorStatus(str, Enum):
    available = "available"
    busy = "busy"
    offline = "offline"
    inactive = "inactive"

