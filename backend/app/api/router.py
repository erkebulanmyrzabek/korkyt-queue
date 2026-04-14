from fastapi import APIRouter

from app.api.v1.admin import router as admin_router
from app.api.v1.dashboard import router as dashboard_router
from app.api.v1.health import router as health_router
from app.api.v1.instructor import router as instructor_router
from app.api.v1.queue import router as queue_router

api_router = APIRouter()
api_router.include_router(health_router, prefix="/health", tags=["health"])
api_router.include_router(dashboard_router, prefix="/dashboard", tags=["dashboard"])
api_router.include_router(queue_router, prefix="/queue", tags=["queue"])
api_router.include_router(admin_router, prefix="/admin", tags=["admin"])
api_router.include_router(instructor_router, prefix="/instructor", tags=["instructor"])
