"""
Client dashboard endpoints
"""

from fastapi import APIRouter, Depends
import asyncpg
from app.dependencies.client import require_client
from app.db.session import get_db
from app.services.client.dashboard_service import DashboardService
from app.schemas.client.dashboard import DashboardResponse
from app.models.user import User

router = APIRouter()
dashboard_service = DashboardService()


@router.get("", response_model=DashboardResponse, summary="Get client dashboard")
async def get_dashboard(
    current_user: User = Depends(require_client),
    db: asyncpg.Connection = Depends(get_db)
):
    """Get client dashboard data"""
    data = await dashboard_service.get_dashboard_data(db, current_user.id)
    return DashboardResponse(**data)

