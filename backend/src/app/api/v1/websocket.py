"""
WebSocket endpoints for real-time updates
"""

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query
from typing import Optional
import jwt
import logging
from app.core.config import settings

logger = logging.getLogger(__name__)

router = APIRouter()

# Allowed origins for WebSocket connections
ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://localhost:3001",
    "http://localhost:5173",
    "http://localhost:8080",
]


async def verify_websocket_token(token: str) -> Optional[dict]:
    """Verify JWT token for WebSocket connection"""
    try:
        payload = jwt.decode(
            token,
            settings.jwt_secret_key,
            algorithms=["HS256"]
        )
        return payload
    except jwt.ExpiredSignatureError:
        logger.warning("WebSocket token expired")
        return None
    except jwt.InvalidTokenError:
        logger.warning("WebSocket token invalid")
        return None


@router.websocket("/ws/client")
async def websocket_client(websocket: WebSocket, token: Optional[str] = Query(None)):
    """
    WebSocket endpoint for client real-time updates
    
    Usage:
        ws://localhost:8000/ws/client?token=YOUR_JWT_TOKEN
    """
    # Check origin
    origin = websocket.headers.get("origin")
    if origin and origin not in ALLOWED_ORIGINS:
        logger.warning(f"WebSocket connection rejected: origin {origin} not allowed")
        await websocket.close(code=403, reason="Origin not allowed")
        return
    
    # Verify token
    if not token:
        logger.warning("WebSocket connection rejected: no token provided")
        await websocket.close(code=403, reason="Authentication required")
        return
    
    # Verify JWT token
    payload = await verify_websocket_token(token)
    if not payload:
        logger.warning("WebSocket connection rejected: invalid token")
        await websocket.close(code=403, reason="Invalid or expired token")
        return
    
    # Extract user info from token
    user_id = payload.get("sub") or payload.get("user_id")
    user_role = payload.get("role")
    
    # Verify user is a client
    if user_role != "client":
        logger.warning(f"WebSocket connection rejected: user {user_id} is not a client")
        await websocket.close(code=403, reason="Client access only")
        return
    
    # Accept connection
    await websocket.accept()
    logger.info(f"WebSocket connection established for client {user_id}")
    
    try:
        # Send welcome message
        await websocket.send_json({
            "type": "connected",
            "message": "WebSocket connection established",
            "user_id": str(user_id),
            "source": "client"
        })
        
        # Keep connection alive and handle messages
        while True:
            # Wait for messages from client
            try:
                data = await websocket.receive_text()
                logger.debug(f"Received message from client {user_id}: {data}")
                
                # Echo back (you can implement actual message handling here)
                await websocket.send_json({
                    "type": "echo",
                    "message": f"Received: {data}",
                    "source": "client"
                })
            except WebSocketDisconnect:
                logger.info(f"WebSocket disconnected for client {user_id}")
                break
                
    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected for client {user_id}")
    except Exception as e:
        logger.error(f"WebSocket error for client {user_id}: {e}")
        try:
            await websocket.close(code=1011, reason="Internal server error")
        except:
            pass


@router.websocket("/ws/expert")
async def websocket_expert(websocket: WebSocket, token: Optional[str] = Query(None)):
    """
    WebSocket endpoint for expert real-time updates
    
    Usage:
        ws://localhost:8000/ws/expert?token=YOUR_JWT_TOKEN
    """
    # Check origin
    origin = websocket.headers.get("origin")
    if origin and origin not in ALLOWED_ORIGINS:
        logger.warning(f"WebSocket connection rejected: origin {origin} not allowed")
        await websocket.close(code=403, reason="Origin not allowed")
        return
    
    # Verify token
    if not token:
        logger.warning("WebSocket connection rejected: no token provided")
        await websocket.close(code=403, reason="Authentication required")
        return
    
    # Verify JWT token
    payload = await verify_websocket_token(token)
    if not payload:
        logger.warning("WebSocket connection rejected: invalid token")
        await websocket.close(code=403, reason="Invalid or expired token")
        return
    
    # Extract user info from token
    user_id = payload.get("sub") or payload.get("user_id")
    user_role = payload.get("role")
    
    # Verify user is an expert
    if user_role != "expert":
        logger.warning(f"WebSocket connection rejected: user {user_id} is not an expert")
        await websocket.close(code=403, reason="Expert access only")
        return
    
    # Accept connection
    await websocket.accept()
    logger.info(f"WebSocket connection established for expert {user_id}")
    
    try:
        # Send welcome message
        await websocket.send_json({
            "type": "connected",
            "message": "WebSocket connection established",
            "user_id": str(user_id),
            "source": "expert"
        })
        
        # Keep connection alive and handle messages
        while True:
            # Wait for messages from expert
            try:
                data = await websocket.receive_text()
                logger.debug(f"Received message from expert {user_id}: {data}")
                
                # Echo back (you can implement actual message handling here)
                await websocket.send_json({
                    "type": "echo",
                    "message": f"Received: {data}",
                    "source": "expert"
                })
            except WebSocketDisconnect:
                logger.info(f"WebSocket disconnected for expert {user_id}")
                break
                
    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected for expert {user_id}")
    except Exception as e:
        logger.error(f"WebSocket error for expert {user_id}: {e}")
        try:
            await websocket.close(code=1011, reason="Internal server error")
        except:
            pass

