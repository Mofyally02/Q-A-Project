# Notification Sound Files

This directory contains notification sound files for the Q&A Platform.

## Required Sound Files

Place the following sound files in this directory:

### R1.mp3
- **Purpose**: Expert-to-client notifications
- **Used for**:
  - Answer delivered notifications
  - Expert messages to clients
  - Expert typing indicators (optional)
  - Any notification originating from an expert

### R2.mp3
- **Purpose**: Admin-to-client and admin-to-expert notifications
- **Used for**:
  - System announcements
  - Admin messages to clients
  - Admin messages to experts
  - System-wide notifications
  - Compliance alerts
  - Account updates

## File Format

- **Format**: MP3
- **Recommended**: 
  - Bitrate: 128 kbps or higher
  - Duration: 0.5 - 2 seconds
  - Sample rate: 44.1 kHz
  - Volume: Normalized to prevent clipping

## Usage

The sounds are automatically played by the notification system based on the notification source:

```typescript
// Expert notification → R1.mp3
playNotificationSound('expert')

// Admin notification → R2.mp3
playNotificationSound('admin')
```

## Testing

To test notification sounds:
1. Ensure both R1.mp3 and R2.mp3 are in `/public/sounds/`
2. Trigger a notification from expert (should play R1.mp3)
3. Trigger a notification from admin (should play R2.mp3)

## Browser Compatibility

- Modern browsers (Chrome, Firefox, Safari, Edge) support MP3
- Sounds will fail silently if files are missing (no errors shown)
- Volume is set to 30-40% by default to avoid startling users


