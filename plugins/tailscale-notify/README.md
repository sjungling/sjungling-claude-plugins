# tailscale-notify

Sends Claude Code notifications to a Tailscale endpoint via HTTP POST.

## Installation

```
/plugin install tailscale-notify@sjungling-plugins
```

## Configuration

The notification endpoint can be configured via environment variable:

```bash
export TAILSCALE_NOTIFY_URL="https://your-device.your-tailnet.ts.net:7080/endpoint"
```

If not set, defaults to `https://YOUR-DEVICE.YOUR-TAILNET.ts.net:7080/<hostname>` where `<hostname>` is your machine's hostname (lowercase).

## How It Works

When Claude Code sends a notification, this plugin:
1. Extracts the message content
2. POSTs it to your Tailscale endpoint
3. Silently handles failures (best-effort delivery)

The curl request has a 5-second timeout to avoid blocking.
