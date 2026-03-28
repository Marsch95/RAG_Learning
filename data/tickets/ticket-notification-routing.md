---
title: Ticket TKT-207: Route Receipts Through Shared Notification Module
source_type: ticket
module: notifications
ticket_id: TKT-207
updated_at: 2026-03-13
---
# Ticket TKT-207: Route Receipts Through Shared Notification Module

## Summary

Receipt emails and store alerts were being described in different places.

The team wanted one shared notification module so delivery behavior could be tested and changed in one location.

## Why This Work Was Needed

Without a shared module, other parts of the system would need to know too much about how messages were delivered.

That would make the design harder to test and harder to change later.

## Decision

Route customer receipts and store alerts through the notification module.

Keep message creation separate from the final delivery channel.

## Notes

This ticket explains the product and architecture reason behind the notification design.
