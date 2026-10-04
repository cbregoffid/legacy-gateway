# Legacy Gateway

A reverse proxy that protects legacy applications by verifying every request before it reaches them, without changing the application itself.

## The Problem

Legacy systems are technological systems that operate on outdated and sunsetted software. For instance, some MRI machines today still run on Windows XP, using software built specifically for that operating system. Many organizations can't afford to update these systems, and even when they can, the software has often been configured so heavily over so many years that replacing it is nearly impossible. Since these systems no longer receive security updates, they are easy targets for attackers.

## The Solution

The gateway acts as a secure intermediary between users and the legacy software. The legacy application is isolated on a private network, so the only place it can receive requests from is the gateway. Before forwarding any request, the gateway handles login, MFA, encryption, and logging, all without changing a single line of the legacy application's code.

## How It Works

```
                    ┌──────────── Private network ────────────┐
User ──HTTPS──▶  Gateway  ──HTTP──▶  Legacy App               │
                 (login, MFA,        (unchanged, unreachable  │
                  logging)            from outside)           │
                    └─────────────────────────────────────────┘
```

## Scope

**This term:**
For this term, I plan to create a reverse proxy that sits in front of a manually created legacy application. The reverse proxy will handle login and MFA, HTTPS encryption, and audit logging, while the legacy application stays isolated on a private Docker network with its code left untouched. If time allows, I'd also like to add an admin dashboard and suspicious activity detection.

**Future vision:**
If this project were funded with unlimited capital, it would become applicable to organizations that still rely on legacy software, such as hospitals with MRI machines. This would include support for non-web protocols like DICOM, which medical imaging devices use, as well as sign-in through an organization's existing identity provider.

## Requirements Backlog

The full backlog is tracked in [GitHub Issues](https://github.com/cbregoffid/legacy-gateway/issues), with a summary table in [`BACKLOG.md`](BACKLOG.md).

| Label | Meaning |
|---|---|
| `type:*` | Functional or non-functional requirement |
| `priority:*` | MoSCoW priority (must / should / could / won't) |
| `area:*` | Part of the system the requirement belongs to |
| `sp:*` | Story point estimate |

Each issue includes a user story, acceptance criteria, and its dependencies on other requirements.

### How the backlog was created

This backlog was generated using Claude (Anthropic) as an initial pass of requirements elicitation, based on my project proposal from Assignment 1. I reviewed the requirements before importing them into GitHub Issues using the included `create_backlog_issues.py` script.

## Planned Tech Stack

- **Gateway:** To be determined
- **Database:** To be determined
- **Deployment:** Docker Compose

## Status

🚧 Planning phase: initial requirements backlog complete.
