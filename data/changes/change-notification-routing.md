---
title: Change CHG-002: Centralize Notification Delivery
source_type: change
module: notifications
ticket_id: TKT-207
change_id: CHG-002
updated_at: 2026-03-14
---
# Change CHG-002: Centralize Notification Delivery

This change routed receipt emails and store alerts through the shared notification module.

The module now acts as a single interface for delivery behavior.

That keeps callers separate from channel-specific details and supports easier testing.

This change was delivered as part of ticket TKT-207.
