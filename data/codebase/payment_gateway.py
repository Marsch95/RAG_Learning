"""Simulated payment gateway used by the retry helper examples."""

from __future__ import annotations


class PaymentGatewayTimeout(Exception):
    pass


class PaymentGatewayClient:
    def charge_card(self, amount_cents: int, card_token: str) -> dict[str, str]:
        if card_token == "timeout-card":
            raise PaymentGatewayTimeout("temporary network timeout")

        return {"status": "approved", "amount_cents": str(amount_cents)}
