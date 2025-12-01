# Notification Sounds Setup Guide

## Quick Start

1. **Add Sound Files**: Place `R1.mp3` and `R2.mp3` in `/public/sounds/`
2. **Configure WebSocket**: Set `NEXT_PUBLIC_WS_URL` in `.env`
3. **Backend Integration**: Ensure WebSocket messages include `source` field

## Sound File Mapping

| Sound File | Used For | Examples |
|------------|----------|----------|
| **R1.mp3** | Expert-to-client notifications | Answer delivered, Expert messages, Expert typing |
| **R2.mp3** | Admin notifications | System announcements, Admin messages (to clients & experts), Compliance alerts |

## Implementation Details

### Frontend Sound System

The sound system is implemented in `/app/client/lib/sounds.ts`:

```typescript
// Expert notification → R1.mp3
playNotificationSound('expert')

// Admin notification → R2.mp3  
playNotificationSound('admin')
```

### WebSocket Message Format

Backend must include `source` field in notification messages:

```json
{
  "type": "notification",
  "source": "expert",  // or "admin" or "system"
  "message": "Your answer is ready!"
}
```

### Automatic Sound Selection

- `answer_delivered` events → Always R1.mp3 (expert-to-client)
- `notification` with `source: "expert"` → R1.mp3
- `notification` with `source: "admin"` → R2.mp3
- `notification` with `source: "system"` → R2.mp3
- `expert_assignment` (expert portal) → R2.mp3

## File Requirements

### R1.mp3
- **Location**: `/public/sounds/R1.mp3`
- **Purpose**: Expert-to-client notifications
- **Recommended**: Short, pleasant notification sound (0.5-2 seconds)

### R2.mp3
- **Location**: `/public/sounds/R2.mp3`
- **Purpose**: Admin/system notifications
- **Recommended**: Distinct from R1, professional tone (0.5-2 seconds)

## Testing

### Test R1.mp3 (Expert Notifications)
1. Trigger an answer delivery event
2. Should hear R1.mp3 play
3. Check browser console for any errors

### Test R2.mp3 (Admin Notifications)
1. Send admin notification to client
2. Should hear R2.mp3 play
3. Verify different sound from R1.mp3

## Browser Compatibility

- ✅ Chrome/Edge: Full support
- ✅ Firefox: Full support
- ✅ Safari: Full support
- ⚠️ Mobile browsers: May require user interaction first

## Troubleshooting

### No Sound Playing
1. Check browser console for errors
2. Verify files exist in `/public/sounds/`
3. Check file permissions
4. Verify audio format (MP3)

### Wrong Sound Playing
1. Check `source` field in WebSocket message
2. Verify backend is sending correct `source` value
3. Check browser console for message logs

### Sound Too Loud/Quiet
- Default volume is 30-40%
- Can be adjusted in `sounds.ts`:
  ```typescript
  playNotificationSound('expert', 0.5) // 50% volume
  ```

## Production Deployment

1. ✅ Add sound files to `/public/sounds/`
2. ✅ Test in staging environment
3. ✅ Verify WebSocket URL is set correctly
4. ✅ Test notification sounds on different devices
5. ✅ Monitor for any console errors


