DROP TABLE IF EXISTS notification_deliveries;
DROP TABLE IF EXISTS payment_attempts;

CREATE TABLE notification_deliveries (
    delivery_id INTEGER PRIMARY KEY,
    order_id INTEGER NOT NULL,
    channel TEXT NOT NULL,
    recipient TEXT NOT NULL,
    status TEXT NOT NULL,
    error_message TEXT,
    created_at TEXT NOT NULL
);

CREATE TABLE payment_attempts (
    attempt_id INTEGER PRIMARY KEY,
    order_id INTEGER NOT NULL,
    card_token TEXT NOT NULL,
    status TEXT NOT NULL,
    failure_reason TEXT,
    retry_count INTEGER NOT NULL DEFAULT 0,
    created_at TEXT NOT NULL
);

INSERT INTO payment_attempts (attempt_id, order_id, card_token, status, failure_reason, retry_count, created_at) VALUES
(1, 1001, 'card-ok-01', 'approved', NULL, 0, '2026-03-17T09:10:00'),
(2, 1002, 'timeout-card', 'failed', 'temporary network timeout', 3, '2026-03-17T09:14:00'),
(3, 1003, 'card-ok-02', 'approved', NULL, 1, '2026-03-17T09:18:00'),
(4, 1004, 'timeout-card', 'failed', 'temporary network timeout', 2, '2026-03-17T09:22:00'),
(5, 1005, 'card-declined-01', 'failed', 'card declined', 0, '2026-03-17T09:28:00');

INSERT INTO notification_deliveries (delivery_id, order_id, channel, recipient, status, error_message, created_at) VALUES
(1, 1001, 'email', 'alice@example.com', 'sent', NULL, '2026-03-17T09:12:00'),
(2, 1002, 'email', 'bob@example.com', 'failed', 'mailbox unavailable', '2026-03-17T09:16:00'),
(3, 1003, 'in-app', 'store-014', 'sent', NULL, '2026-03-17T09:19:00'),
(4, 1004, 'email', 'carol@example.com', 'failed', 'temporary smtp timeout', '2026-03-17T09:24:00');