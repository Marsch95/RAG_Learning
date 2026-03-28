# Retry Logic

Retry logic was added after the team saw intermittent failures while calling a simulated payment gateway.

Before the change, a single temporary network failure could cause a checkout attempt to fail.

The retry helper now retries transient failures a small number of times with a short backoff between attempts.

The team added this behavior to improve checkout resilience without hiding persistent problems.

If all retry attempts fail, the error is still surfaced so the caller can log it and respond appropriately.

This note is useful because it records the reason the retry helper exists, not just what it does.