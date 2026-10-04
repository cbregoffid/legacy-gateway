# Requirements Backlog

Initial requirements elicitation pass for the Legacy Gateway project. Each requirement is tracked as a GitHub issue with labels for type, priority (MoSCoW), area, and story points.

| Issue | ID | Requirement | Type | Priority | Points | Area | Depends on |
|---|---|---|---|---|---|---|---|
| #1 | REQ-001 | Legacy demo application | functional | Must have | 3 | legacy-app | None |
| #2 | REQ-002 | Containerized deployment | non-functional | Must have | 3 | deployment | #1 |
| #3 | REQ-003 | Network isolation of the legacy app | non-functional | Must have | 2 | isolation | #2 |
| #4 | REQ-004 | Reverse proxy request forwarding | functional | Must have | 5 | proxy | #1 |
| #5 | REQ-005 | No modifications to the legacy app | non-functional | Must have | 1 | proxy | #4 |
| #6 | REQ-006 | Upstream failure handling | functional | Should have | 2 | proxy | #4 |
| #7 | REQ-007 | User account store | functional | Must have | 3 | auth | #2 |
| #8 | REQ-008 | Secure password storage | non-functional | Must have | 2 | auth | #7 |
| #9 | REQ-009 | Login and session management | functional | Must have | 5 | auth | #4, #7, #8 |
| #10 | REQ-010 | Logout and session expiry | functional | Should have | 2 | auth | #9 |
| #11 | REQ-011 | Brute-force protection | functional | Should have | 3 | auth | #9, #19 |
| #12 | REQ-012 | MFA enrollment (TOTP) | functional | Must have | 3 | mfa | #9 |
| #13 | REQ-013 | MFA verification at login | functional | Must have | 3 | mfa | #12 |
| #14 | REQ-014 | Role-based access control | functional | Should have | 5 | authorization | #9 |
| #15 | REQ-015 | Path-level access rules | functional | Should have | 5 | authorization | #14, #18 |
| #16 | REQ-016 | HTTPS termination | non-functional | Must have | 3 | encryption | #4 |
| #17 | REQ-017 | Security response headers | non-functional | Could have | 1 | encryption | #16 |
| #18 | REQ-018 | Request audit logging | functional | Must have | 3 | logging | #4, #9 |
| #19 | REQ-019 | Authentication event logging | functional | Must have | 2 | logging | #9, #18 |
| #20 | REQ-020 | Tamper-evident log storage | non-functional | Could have | 5 | logging | #18 |
| #21 | REQ-021 | Audit log dashboard | functional | Should have | 5 | dashboard | #14, #18, #19 |
| #22 | REQ-022 | User management interface | functional | Should have | 5 | dashboard | #12, #14, #18 |
| #23 | REQ-023 | Suspicious activity detection | functional | Could have | 8 | monitoring | #18, #19 |
| #24 | REQ-024 | Security alerts on dashboard | functional | Could have | 3 | monitoring | #21, #23 |
| #25 | REQ-025 | Gateway configuration | non-functional | Must have | 2 | deployment | #4 |
| #26 | REQ-026 | Performance overhead | non-functional | Should have | 2 | proxy | #4, #9 |
| #27 | REQ-027 | Automated tests | non-functional | Should have | 3 | testing | #3, #9 |
| #28 | REQ-028 | Setup and architecture documentation | non-functional | Must have | 2 | docs | #2, #3 |
| #29 | REQ-029 | Non-HTTP protocol support (e.g., DICOM) | functional | Won't have (this term) | - | proxy | #4 |
| #30 | REQ-030 | Single sign-on with external identity providers | functional | Won't have (this term) | - | auth | #9 |
