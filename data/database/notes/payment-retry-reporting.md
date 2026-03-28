---
title: Payment Retry Reporting Notes
source_type: db_note
module: payments
database_name: acme_checkout
table_name: payment_attempts
query_name: find_failed_payment_attempts
service_name: PaymentReportingQuery
updated_at: 2026-03-17
---

# Payment Retry Reporting Notes

The `payment_attempts` table stores each payment attempt, including retries and final failure states.

The reporting query `find_failed_payment_attempts` reads from that table to show failures that still remained after retry logic finished.

This note exists so the team can connect the table design to the reporting workflow without reading the SQL alone.