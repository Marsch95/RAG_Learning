"""Notification module used for receipts and store alerts."""

from __future__ import annotations


class NotificationService:
    def send_receipt(self, email: str, receipt_body: str) -> dict[str, str]:
        payload = self.build_message_payload("receipt", receipt_body)
        return self.deliver_email(email, payload)

    def send_store_alert(self, store_id: str, message: str) -> dict[str, str]:
        payload = self.build_message_payload("store-alert", message)
        return self.publish_in_app_alert(store_id, payload)

    def build_message_payload(self, message_type: str, body: str) -> dict[str, str]:
        return {"message_type": message_type, "body": body}

    def deliver_email(self, email: str, payload: dict[str, str]) -> dict[str, str]:
        return {"channel": "email", "target": email, "message_type": payload["message_type"]}

    def publish_in_app_alert(self, store_id: str, payload: dict[str, str]) -> dict[str, str]:
        return {"channel": "in-app", "target": store_id, "message_type": payload["message_type"]}
