---
title: Notification Module
source_type: doc
module: notifications
ticket_id: TKT-207
updated_at: 2026-03-14
---

# Notification Module

The notification module sends customer-facing and store-facing messages.

Its current responsibilities are:

- send digital receipts by email
- create in-app notifications for store managers and register operators
- provide a shared interface so other modules do not need to know delivery details

The notification module exists because the team wanted a single place to manage delivery behavior.

The design direction was tracked in ticket TKT-207.

The current design keeps message creation separate from message delivery. That means a caller can request a notification without knowing whether the final destination is email or the in-app activity feed.

This separation also makes it easier to test the module in isolation.