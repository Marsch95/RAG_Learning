-- title: Table notification_deliveries
-- source_type: db_schema
-- module: notifications
-- database_name: acme_checkout
-- table_name: notification_deliveries
-- service_name: NotificationService
-- updated_at: 2026-03-15

CREATE TABLE notification_deliveries (
    delivery_id INTEGER PRIMARY KEY,
    order_id INTEGER NOT NULL,
    channel TEXT NOT NULL,
    recipient TEXT NOT NULL,
    status TEXT NOT NULL,
    error_message TEXT,
    created_at TEXT NOT NULL
);

-- Purpose: stores delivery attempts for customer receipts and store alerts.
-- Written by: NotificationService.
-- Important statuses: queued, sent, failed.