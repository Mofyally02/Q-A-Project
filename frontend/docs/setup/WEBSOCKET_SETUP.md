# WebSocket & Notification Sounds Setup

## ✅ Implementation Complete

The notification sound system is fully implemented with unique sounds for different notification sources.

## Sound Files Required

Add these files to `/public/sounds/`:

1. **R1.mp3** - Expert-to-client notifications
2. **R2.mp3** - Admin-to-client and admin-to-expert notifications

## Environment Configuration

Create `.env.local` in the frontend directory:

```env
# WebSocket URL (without /ws/client or /ws/expert)
NEXT_PUBLIC_WS_URL=ws://localhost:8000

# For production with SSL
# NEXT_PUBLIC_WS_URL=wss://your-domain.com
```

## How It Works

### Sound Selection Logic

| Notification Source | Sound File | When It Plays |
|-------------------|------------|---------------|
| Expert → Client | **R1.mp3** | Answer delivered, Expert messages |
| Admin → Client | **R2.mp3** | System announcements, Admin messages |
| Admin → Expert | **R2.mp3** | Question assignments, Admin messages |
| System | **R2.mp3** | System-wide notifications |

### Automatic Detection

The system automatically detects the notification source from the WebSocket message:

```json
{
  "type": "notification",
  "source": "expert",  // ← Determines which sound plays
  "message": "Your answer is ready!"
}
```

## Backend Integration

Your FastAPI WebSocket must include the `source` field:

### Client WebSocket (`/ws/client`)

```python
# Expert notification → R1.mp3
await websocket.send_json({
    "type": "notification",
    "source": "expert",  # ← Important!
    "message": "Answer delivered"
})

# Admin notification → R2.mp3
await websocket.send_json({
    "type": "notification",
    "source": "admin",  # ← Important!
    "message": "System maintenance"
})
```

### Expert WebSocket (`/ws/expert`)

```python
# Admin notification → R2.mp3
await websocket.send_json({
    "type": "expert_assignment",
    "question_id": "q_123",
    "subject": "Calculus"
    # Always uses R2.mp3 for admin-to-expert
})
```

## Files Created/Updated

### New Files
- ✅ `/app/client/lib/sounds.ts` - Sound utility functions
- ✅ `/app/client/hooks/useWebSocket.ts` - Client WebSocket hook
- ✅ `/app/expert/hooks/useWebSocket.ts` - Expert WebSocket hook
- ✅ `/public/sounds/README.md` - Sound files documentation
- ✅ `/docs/WEBSOCKET_INTEGRATION.md` - Complete integration guide
- ✅ `/docs/NOTIFICATION_SOUNDS_SETUP.md` - Setup instructions

### Updated Files
- ✅ `/app/client/dashboard/page.tsx` - Uses WebSocket hook
- ✅ `/stores/useRealTimeStore.ts` - Added clearNotifications method

## Testing Checklist

- [ ] Add R1.mp3 to `/public/sounds/`
- [ ] Add R2.mp3 to `/public/sounds/`
- [ ] Set `NEXT_PUBLIC_WS_URL` in `.env.local`
- [ ] Test expert notification (should play R1.mp3)
- [ ] Test admin notification (should play R2.mp3)
- [ ] Verify sounds are different
- [ ] Test on mobile devices
- [ ] Check browser console for errors

## Next Steps

1. **Add Sound Files**: Place R1.mp3 and R2.mp3 in `/public/sounds/`
2. **Configure Backend**: Ensure WebSocket messages include `source` field
3. **Test**: Send test notifications and verify correct sounds play
4. **Deploy**: Include sound files in production build

## Support

If sounds don't play:
1. Check browser console for errors
2. Verify files exist and are accessible
3. Check WebSocket connection status
4. Verify `source` field in WebSocket messages


