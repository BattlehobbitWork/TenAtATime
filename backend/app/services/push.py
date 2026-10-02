"""Web Push sending service using pywebpush."""

import json
from app.config import settings


async def send_push(subscription, title: str, body: str):
    """Send a web push notification to a single subscription."""
    try:
        from pywebpush import webpush, WebPushException

        keys = json.loads(subscription.keys_json)
        subscription_info = {
            "endpoint": subscription.endpoint,
            "keys": keys,
        }

        vapid_private = settings.vapid_private_key
        vapid_public = settings.vapid_public_key

        if not vapid_private or not vapid_public:
            # No VAPID keys configured -- skip silently
            return

        webpush(
            subscription_info=subscription_info,
            data=json.dumps({"title": title, "body": body}),
            vapid_private_key=vapid_private,
            vapid_public_key=vapid_public,
            vapid_claims={"sub": settings.vapid_subject},
        )
    except Exception as e:
        # Log but don't crash -- push failures are non-critical
        import logging
        logging.getLogger(__name__).warning(f"Push send failed: {e}")
