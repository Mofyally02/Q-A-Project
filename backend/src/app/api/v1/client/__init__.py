"""
Client API routes
All client endpoints with proper permissions
"""

from fastapi import APIRouter
from app.api.v1.client import dashboard, questions, wallet, notifications, settings, history, chat, achievements

# Create client router
client_router = APIRouter(prefix="/client", tags=["client"])

# Include sub-routers
client_router.include_router(dashboard.router, prefix="/dashboard", tags=["client-dashboard"])
client_router.include_router(questions.router, prefix="/questions", tags=["client-questions"])
client_router.include_router(wallet.router, prefix="/wallet", tags=["client-wallet"])
client_router.include_router(notifications.router, prefix="/notifications", tags=["client-notifications"])
client_router.include_router(settings.router, prefix="/settings", tags=["client-settings"])
client_router.include_router(achievements.router, prefix="/achievements", tags=["client-achievements"])

# Add alias routes for frontend compatibility
# Note: history router already has /history path, so we include it without prefix
# This creates /client/history endpoint
from fastapi import APIRouter
history_alias_router = APIRouter()
@history_alias_router.get("/history")
async def history_alias(*args, **kwargs):
    from app.api.v1.client.history import get_history
    return await get_history(*args, **kwargs)
client_router.include_router(history_alias_router, tags=["client"])

client_router.include_router(chat.router, prefix="/chat", tags=["client"])  # /client/chat/{id}

