# WebSocket Integration Guide

## Overview

The frontend uses WebSocket connections for real-time updates. Different notification sounds are played based on the notification source.

## Sound Files

### Required Sound Files
Place these files in `/public/sounds/`:

- **R1.mp3**: Expert-to-client notifications
  - Answer delivered
  - Expert messages to clients
  - Expert typing indicators

- **R2.mp3**: Admin-to-client and admin-to-expert notifications
  - System announcements
  - Admin messages
  - Compliance alerts
  - Account updates

## Environment Configuration

### Client Environment (.env)

```env
# WebSocket URL for real-time updates
NEXT_PUBLIC_WS_URL=ws://localhost:8000

# Or for production with SSL
NEXT_PUBLIC_WS_URL=wss://your-domain.com
```

### Expert Environment

Experts use the same WebSocket URL but connect to `/ws/expert` endpoint.

## Backend WebSocket Event Types

### Client WebSocket Events (`/ws/client`)

#### 1. Question Submitted
```json
{
  "type": "question_submitted",
  "question_id": "q_123",
  "subject": "Calculus",
  "timestamp": "2025-01-15T10:30:00Z"
}
```

#### 2. AI Processing Started
```json
{
  "type": "ai_processing_started",
  "question_id": "q_123"
}
```

#### 3. Humanization Complete
```json
{
  "type": "humanization_complete",
  "question_id": "q_123"
}
```

#### 4. Expert Assigned
```json
{
  "type": "expert_assigned",
  "question_id": "q_123",
  "expert_name": "Dr. Sarah",
  "expert_avatar": "https://..."
}
```

#### 5. Expert Typing
```json
{
  "type": "expert_typing",
  "question_id": "q_123"
}
```

#### 6. Answer Delivered (Plays R1.mp3)
```json
{
  "type": "answer_delivered",
  "question_id": "q_123",
  "question": "What is the derivative of x²?",
  "answer": "The derivative is 2x...",
  "expert_name": "Dr. Sarah",
  "subject": "Calculus",
  "timestamp": "2025-01-15T10:35:00Z",
  "image": "https://...",
  "rating": 4.5
}
```

#### 7. Notification (Plays R1.mp3 for expert, R2.mp3 for admin)
```json
{
  "type": "notification",
  "source": "expert",  // or "admin" or "system"
  "message": "Your answer has been reviewed",
  "timestamp": "2025-01-15T10:35:00Z"
}
```

#### 8. Credit Added
```json
{
  "type": "credit_added",
  "credits": 25,
  "amount": 10
}
```

### Expert WebSocket Events (`/ws/expert`)

#### 1. Expert Assignment (Plays R2.mp3)
```json
{
  "type": "expert_assignment",
  "question_id": "q_123",
  "subject": "Calculus",
  "timestamp": "2025-01-15T10:30:00Z"
}
```

#### 2. Notification (Plays R2.mp3)
```json
{
  "type": "notification",
  "source": "admin",  // Admin notifications to experts
  "message": "System maintenance scheduled",
  "timestamp": "2025-01-15T10:30:00Z"
}
```

#### 3. Question Updated
```json
{
  "type": "question_updated",
  "question_id": "q_123",
  "status": "review",
  "timestamp": "2025-01-15T10:30:00Z"
}
```

## Backend Implementation Example

### FastAPI WebSocket Endpoint

```python
from fastapi import WebSocket, WebSocketDisconnect
import json

@app.websocket("/ws/client")
async def websocket_client(websocket: WebSocket, user_id: str):
    await websocket.accept()
    try:
        while True:
            # Send notifications to client
            notification = {
                "type": "answer_delivered",
                "question_id": "q_123",
                "source": "expert",  # Important: determines sound file
                "message": "Your answer is ready!",
                "timestamp": datetime.utcnow().isoformat()
            }
            await websocket.send_json(notification)
    except WebSocketDisconnect:
        pass

@app.websocket("/ws/expert")
async def websocket_expert(websocket: WebSocket, expert_id: str):
    await websocket.accept()
    try:
        while True:
            # Send notifications to expert
            notification = {
                "type": "expert_assignment",
                "question_id": "q_123",
                "subject": "Calculus",
                "source": "admin",  # Admin notifications use R2.mp3
                "timestamp": datetime.utcnow().isoformat()
            }
            await websocket.send_json(notification)
    except WebSocketDisconnect:
        pass
```

## Sound Selection Logic

The frontend automatically selects the correct sound based on the `source` field:

- `source: "expert"` → R1.mp3
- `source: "admin"` or `source: "system"` → R2.mp3
- No source specified → R2.mp3 (default)

## Testing

### Test Client Notifications

1. **Expert Notification (R1.mp3)**:
   ```json
   {
     "type": "notification",
     "source": "expert",
     "message": "Test expert notification"
   }
   ```

2. **Admin Notification (R2.mp3)**:
   ```json
   {
     "type": "notification",
     "source": "admin",
     "message": "Test admin notification"
   }
   ```

### Test Expert Notifications

1. **Admin to Expert (R2.mp3)**:
   ```json
   {
     "type": "expert_assignment",
     "question_id": "q_test",
     "subject": "Test Question"
   }
   ```

## Error Handling

- If sound files are missing, the app continues without errors
- WebSocket connection failures are logged but don't break the app
- Automatic reconnection can be enabled (commented in code)

## Production Checklist

- [ ] Add R1.mp3 to `/public/sounds/`
- [ ] Add R2.mp3 to `/public/sounds/`
- [ ] Set `NEXT_PUBLIC_WS_URL` in production environment
- [ ] Configure WebSocket endpoint in backend
- [ ] Test notification sounds in different browsers
- [ ] Verify WebSocket connection with authentication
- [ ] Monitor WebSocket connection stability


