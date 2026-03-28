-- title: Query find_failed_payment_attempts
-- source_type: db_query
-- module: payments
-- database_name: acme_checkout
-- query_name: find_failed_payment_attempts
-- table_name: payment_attempts
-- service_name: PaymentReportingQuery
-- updated_at: 2026-03-16

SELECT
    attempt_id,
    order_id,
    status,
    failure_reason,
    retry_count,
    created_at
FROM payment_attempts
WHERE status = 'failed'
ORDER BY created_at DESC;

-- Purpose: used to inspect payment attempts that still failed after retry logic completed.