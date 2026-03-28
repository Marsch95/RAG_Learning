-- title: Query list_notification_delivery_failures
-- source_type: db_query
-- module: notifications
-- database_name: acme_checkout
-- query_name: list_notification_delivery_failures
-- table_name: notification_deliveries
-- service_name: NotificationDeliveryReport
-- updated_at: 2026-03-16

SELECT
    delivery_id,
    order_id,
    channel,
    recipient,
    error_message,
    created_at
FROM notification_deliveries
WHERE status = 'failed'
ORDER BY created_at DESC;

-- Purpose: helps support staff review receipt or store alert deliveries that failed.