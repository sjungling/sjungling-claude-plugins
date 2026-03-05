# tailscale-notify

Sends Claude Code notifications to a Tailscale endpoint via HTTP POST.

## Installation

```
/plugin install tailscale-notify@sjungling-plugins
```

## Configuration

Set the `TAILSCALE_NOTIFY_URL` environment variable to the base URL of your notification endpoint:

```bash
export TAILSCALE_NOTIFY_URL="https://your-device.your-tailnet.ts.net:7080"
```

The hook appends your machine's hostname (lowercase) as the path, so notifications go to `$TAILSCALE_NOTIFY_URL/<hostname>`. If `TAILSCALE_NOTIFY_URL` is not set, the hook silently does nothing.

## How It Works

When Claude Code sends a notification, this plugin:
1. Checks if the macOS screen is locked (using `ioreg` to query `CGSSessionScreenIsLocked`)
2. If locked, extracts the message content and POSTs it to your Tailscale endpoint
3. If unlocked, skips the notification (user is assumed to be actively watching)
4. Silently handles failures (best-effort delivery)

The curl request has a 5-second timeout to avoid blocking.

**Note:** This plugin only sends notifications when the screen is locked, assuming an active user doesn't need remote notifications.
