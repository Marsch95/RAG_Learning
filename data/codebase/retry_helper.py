"""Retry helper added after intermittent payment gateway failures."""

from __future__ import annotations

import time
from collections.abc import Callable

from payment_gateway import PaymentGatewayTimeout


def retry_payment_call(
    operation: Callable[[], dict[str, str]],
    *,
    max_attempts: int = 3,
    base_delay_seconds: float = 0.2,
) -> dict[str, str]:
    last_error: Exception | None = None

    for attempt_number in range(1, max_attempts + 1):
        try:
            return operation()
        except PaymentGatewayTimeout as error:
            last_error = error
            if attempt_number == max_attempts:
                raise
            time.sleep(base_delay_seconds * attempt_number)

    if last_error is not None:
        raise last_error

    raise RuntimeError("retry_payment_call finished without returning or raising")


def describe_retry_reason() -> str:
    return "Retry logic was introduced to handle temporary payment gateway timeouts."
