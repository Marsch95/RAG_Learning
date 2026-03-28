-- title: Table payment_attempts
-- source_type: db_schema
-- module: payments
-- database_name: acme_checkout
-- table_name: payment_attempts
-- service_name: PaymentGatewayClient
-- updated_at: 2026-03-12

CREATE TABLE payment_attempts (
    attempt_id INTEGER PRIMARY KEY,
    order_id INTEGER NOT NULL,
    card_token TEXT NOT NULL,
    status TEXT NOT NULL,
    failure_reason TEXT,
    retry_count INTEGER NOT NULL DEFAULT 0,
    created_at TEXT NOT NULL
);

-- Purpose: stores each payment gateway attempt and retry count for checkout resilience analysis.
-- Written by: PaymentGatewayClient and the retry helper flow.
-- Important statuses: approved, failed, retrying.