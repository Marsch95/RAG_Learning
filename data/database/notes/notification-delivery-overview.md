---
title: Notification Delivery Database Notes
source_type: db_note
module: notifications
database_name: acme_checkout
table_name: notification_deliveries
service_name: NotificationService
updated_at: 2026-03-17
---

# Notification Delivery Database Notes

The `notification_deliveries` table stores one row for each receipt or store alert delivery attempt.

The `NotificationService` writes these rows so support tooling can inspect whether a delivery was queued, sent, or failed.

The main reason this table exists is operational visibility.

It gives the team one place to inspect notification outcomes without reading application logs directly.