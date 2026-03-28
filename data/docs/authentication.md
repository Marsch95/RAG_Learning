---
title: Authentication Module
source_type: doc
module: authentication
updated_at: 2026-03-05
---

# Authentication Module

The authentication module is the main entry point for cashier and supervisor sign-in.

Authentication is handled by the `auth_service` backend module. Its responsibilities are:

- validate submitted credentials
- create a session token for successful register logins
- write a login audit entry for traceability

The team decided to keep authentication logic in one backend service so it would be easier to audit and test.

If login fails because the password is wrong, the module returns a clear failure message and does not create a session.

If login succeeds, the module creates a session token that other parts of the checkout application can trust.

This project does not implement real authentication code yet. The document exists to simulate the kind of internal knowledge base note a team might keep.