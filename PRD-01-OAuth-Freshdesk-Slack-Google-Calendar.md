# PRD-01: Freshdesk → Slack thread + Google Calendar event (OAuth)

**Version:** 1.0  
**Status:** Draft for team review  
**Benchmark program:** [PRD-00 Program Overview and Evaluation Protocol](./PRD-00-Program-Overview-and-Evaluation-Protocol.md)  
**Skills / platform context:** [Freshworks Platform 3.0 skills](https://github.com/freshworks-developers/freshworks-platform3.git) · [Developer docs](https://developers.freshworks.com/docs/)

---

## 1. Summary

When a **new Freshdesk ticket** is created, the integration shall:

1. **Create or attach a Slack thread** (e.g. new message in a configured channel that acts as the “ticket thread” anchor, or thread under a parent message — exact Slack shape is specified in §4).
2. **Create a Google Calendar meeting** linked to that ticket (title, time, attendees as specified).

The primary engineering stress is **multi-party OAuth 2.0** (Freshworks app OAuth to Slack and Google), **secure token storage**, **token refresh**, and **idempotent automation** (no duplicate Slack posts or calendar events on retries/webhook duplicates).

---

## 2. Problem statement

Support teams want a single automated workflow from **ticket intake** to **team chat visibility** and **scheduled follow-up**, without manual copy-paste. For our benchmark, the goal is to validate that **skills-guided development** can correctly implement a **dual external OAuth** architecture on the Freshworks developer platform.

---

## 3. Users and personas


| Persona               | Need                                                                                                |
| --------------------- | --------------------------------------------------------------------------------------------------- |
| **Admin / installer** | Connect Slack workspace and Google Calendar account once; map Freshdesk → channel/calendar defaults |
| **Agent**             | Sees Slack thread link and meeting link on the ticket (or in app UI)                                |


---

## 4. Scope

### 4.1 In scope

- Freshworks **Platform 3.0** Freshdesk app (manifest, serverless or hybrid per platform best practice).
- **OAuth** to **Slack** and **Google** (Calendar API) with separate client IDs per provider stored as app configuration.
- Trigger on **ticket created** (Freshdesk product event → serverless handler or equivalent documented pattern).
- **Persist** mapping: `freshdesk_ticket_id` ↔ `slack_channel_id`, `slack_message_ts` (or thread id), `google_event_id`.
- **Idempotency**: duplicate delivery of the same create event must not create a second Slack message or calendar event.
- **Failure UX**: if Slack succeeds and Calendar fails (or reverse), surface state clearly (admin logs + optional ticket private note).

### 4.2 Slack behavior (choose one — team picks before build)

**Option A (recommended for simplicity):** Post a **new top-level message** in a configured channel with ticket summary and a thread; treat that message’s thread as the discussion thread.

**Option B:** Post as a **reply in an existing “tickets parent” thread** (requires storing parent `ts`).

The PRD assumes **Option A** unless the program owner selects B before the timed run.

### 4.3 Calendar event rules


| Field           | Rule                                                                                                          |
| --------------- | ------------------------------------------------------------------------------------------------------------- |
| **Title**       | `[Freshdesk #{{ticket_id}}] {{ticket_subject}}` (truncate subject safely)                                     |
| **Start / end** | Default: start = ticket created time (UTC) + 15 minutes; duration 30 minutes (configurable in app settings)   |
| **Attendees**   | Configurable default attendee list (admin setting); no obligation to resolve requester email if not available |
| **Description** | Include Freshdesk ticket URL and Slack permalink if available                                                 |


### 4.4 Out of scope

- Bi-directional Slack → Freshdesk message sync.
- Rescheduling calendar events when ticket fields change.
- Google Meet auto-creation policies beyond what Calendar API returns by default for the workspace.

---

## 5. Functional requirements


| ID   | Requirement                                                                                                       |
| ---- | ----------------------------------------------------------------------------------------------------------------- |
| FR-1 | On **ticket create**, handler runs within Freshworks platform constraints (document event source).                |
| FR-2 | **Slack**: create message (and thread anchor) with ticket id, subject, requester (if present), priority, URL.     |
| FR-3 | **Google Calendar**: create event per §4.3.                                                                       |
| FR-4 | **Store OAuth tokens** per account/installation using platform-recommended secure storage (no plaintext in repo). |
| FR-5 | **Refresh tokens** before calls when access token expired (or on 401), with bounded retries.                      |
| FR-6 | **Idempotency key** derived from stable ticket id + event type; duplicate processing is a no-op for side effects. |
| FR-7 | **Admin UI** (minimal): status of Slack connection, Google connection, “Test connection” for each.                |
| FR-8 | **Settings**: Slack channel id or picker surrogate; timezone for calendar defaults; optional attendee list.       |


---

## 6. Non-functional requirements


| ID    | Requirement                                                                                                              |
| ----- | ------------------------------------------------------------------------------------------------------------------------ |
| NFR-1 | OAuth scopes are **least privilege** (document chosen Slack scopes + Google scopes).                                     |
| NFR-2 | No secrets committed; use platform iparams / secure storage patterns.                                                    |
| NFR-3 | Structured **logging** for: OAuth state transitions, outbound API status codes, idempotency hits.                        |
| NFR-4 | Graceful degradation: if one provider disconnected, do not partially corrupt stored mappings; fail with clear code path. |


---

## 7. Acceptance criteria (must-have)

Use as the **T3 gate** checklist in [PRD-00](./PRD-00-Program-Overview-and-Evaluation-Protocol.md).

- Creating a ticket in Freshdesk **reliably** creates **exactly one** Slack message (and defined thread behavior) under normal conditions.
- Creating a ticket creates **exactly one** Google Calendar event with correct title pattern and ticket URL in description.
- Replaying the same ticket-create payload (or simulated duplicate webhook) does **not** duplicate Slack or Calendar resources.
- Admin can complete **Slack OAuth** and **Google OAuth** independently; app shows connected/disconnected state.
- Revoking or invalidating a refresh token surfaces a **recoverable** admin-visible error path (re-authorize).
- `fdk validate` (or current platform equivalent) passes with no blocking errors.
- Security review checklist in §9 passes.

### Should-have (optional for T4)

- Ticket **private note** or custom field stores Slack permalink + Calendar event link.
- Basic retry with backoff on **429** from Slack/Google.

---

## 8. Dependencies and assumptions

- Slack app with OAuth, bot token or user token per chosen integration model (document choice).
- Google Cloud project with Calendar API enabled; OAuth consent screen appropriate for internal testing.
- Freshdesk sandbox with ability to install custom app and create tickets.

---

## 9. Security checklist (analytics: pass/fail)


| Check | Pass criteria                                              |
| ----- | ---------------------------------------------------------- |
| S-1   | No client secrets in source control                        |
| S-2   | OAuth **state** parameter validated (CSRF)                 |
| S-3   | Scopes documented and minimal                              |
| S-4   | Tokens encrypted / platform-secure per Freshworks patterns |
| S-5   | HTTPS only for redirect URLs                               |


---

## 10. Test plan (minimum)


| Case                 | Expected                                                                                         |
| -------------------- | ------------------------------------------------------------------------------------------------ |
| Happy path           | Ticket → Slack + Calendar                                                                        |
| Duplicate event      | Second delivery → no new resources                                                               |
| Slack down / 500     | Calendar may still be attempted per policy; final state documented; no orphan mapping corruption |
| Google 401           | Refresh then succeed; if refresh fails, admin reconnect                                          |
| Missing admin config | Clear error; no silent no-op                                                                     |


---

## 11. Open questions (resolve before timed benchmark)

1. Option A vs B for Slack threading?
2. Use **user** vs **bot** Slack token model?
3. Should calendar events be on a **shared** calendar id configured by admin?

---

## Document history


| Version | Date       | Changes       |
| ------- | ---------- | ------------- |
| 1.0     | 2026-03-27 | Initial draft |


