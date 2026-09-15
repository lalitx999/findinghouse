import os
import json
import hmac
import hashlib
import urllib.request
import urllib.parse
from django.conf import settings
from .models import WebhookConfig

def send_line_notification(message: str, token: str = None) -> bool:
    """
    Sends notification message to LINE Notify API.
    Uses LINE_NOTIFY_TOKEN from env or provided token.
    If token is not provided, logs simulated notification cleanly.
    """
    line_token = token or os.getenv("LINE_NOTIFY_TOKEN", getattr(settings, "LINE_NOTIFY_TOKEN", None))

    if not line_token:
        print(f"[LINE NOTIFY SIMULATOR] Token not set. Message:\n{message}")
        return True

    url = "https://notify-api.line.me/api/notify"
    headers = {
        "Authorization": f"Bearer {line_token}",
        "Content-Type": "application/x-www-form-urlencoded"
    }
    data = urllib.parse.urlencode({"message": message}).encode("utf-8")

    try:
        req = urllib.request.Request(url, data=data, headers=headers, method="POST")
        with urllib.request.urlopen(req, timeout=5) as resp:
            return resp.status == 200
    except Exception as e:
        print(f"[LINE NOTIFY ERROR] Failed to send notification: {e}")
        return False


def dispatch_webhook_event(event_type: str, payload: dict) -> int:
    """
    Dispatches JSON event payload to all active registered Webhooks matching event_type.
    Computes HMAC SHA256 signature if secret_token is configured.
    """
    webhooks = WebhookConfig.objects.filter(is_active=True).filter(
        event_type__in=['ALL', event_type]
    )

    dispatched_count = 0
    json_data = json.dumps(payload, ensure_ascii=False, default=str).encode("utf-8")

    for hook in webhooks:
        headers = {
            "Content-Type": "application/json",
            "User-Agent": "FindingHouse-WebhookDispatcher/1.0",
            "X-Event-Type": event_type
        }

        if hook.secret_token:
            signature = hmac.new(
                hook.secret_token.encode("utf-8"),
                json_data,
                hashlib.sha256
            ).hexdigest()
            headers["X-FindingHouse-Signature"] = f"sha256={signature}"

        try:
            req = urllib.request.Request(hook.url, data=json_data, headers=headers, method="POST")
            with urllib.request.urlopen(req, timeout=5) as resp:
                if resp.status in [200, 201, 202, 204]:
                    dispatched_count += 1
        except Exception as e:
            print(f"[WEBHOOK DISPATCH ERROR] Failed sending to {hook.name} ({hook.url}): {e}")

    return dispatched_count
