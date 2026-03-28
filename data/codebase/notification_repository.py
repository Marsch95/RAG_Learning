"""Persistence helpers for notification delivery records."""

from __future__ import annotations


class NotificationDeliveryRepository:
    def record_delivery_attempt(
        self,
        order_id: int,
        channel: str,
        recipient: str,
        status: str,
        error_message: str | None = None,
    ) -> dict[str, str | int | None]:
        return build_delivery_row(order_id, channel, recipient, status, error_message)


def build_delivery_row(
    order_id: int,
    channel: str,
    recipient: str,
    status: str,
    error_message: str | None = None,
) -> dict[str, str | int | None]:
    return {
        "table": "notification_deliveries",
        "order_id": order_id,
        "channel": channel,
        "recipient": recipient,
        "status": status,
        "error_message": error_message,
    }