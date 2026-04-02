# PRD benchmark report — Freshworks \+ integrations

# **Benchmark Summary**

## **Freshworks PRD Execution (PRD-01 → PRD-04)**

**Version:** 1.2  
**Scope:** PRD-01, PRD-02, PRD-03, PRD-04  
**Context:** Freshworks Platform 3.0 · Skills-based app development

---

## **1\. Overview**

This benchmark evaluates the **end-to-end implementation and testing of four Freshdesk app use cases**, covering:

* OAuth integrations (Slack, Google Calendar)  
* Frontend-first analytics dashboards (Crayons UI)  
* Bulk operations with rate limiting  
* Multi-source data aggregation (Shopify multi-store)

The objective was to measure:

* **Execution quality (T3 readiness)**  
* **Platform compatibility (`fdk validate`)**  
* **Reliability under real constraints**

---

## **2\. PRD Coverage**

| PRD | Focus Area | Status |
| ----- | ----- | ----- |
| PRD-01 | Slack \+ Calendar OAuth automation | Implemented & validated |
| PRD-02 | Crayons UI dashboard \+ sidebar (frontend-first) | Implemented & validated |
| PRD-03 | Shopify multi-store order aggregation | Implemented & validated |
| PRD-04 | Bulk ticket creation with rate limiting | Implemented & validated |

## **3\. Execution Summary**

* **All PRDs implemented and tested successfully (T3 level)**  
* Apps validated against:  
  * Freshworks platform constraints  
  * Security best practices  
  * Functional requirements

### **Key Observation**

* **PRD-02 (Crayons UI)**:  
  * Fastest to build  
  * Most stable  
  * No timeout issues  
* **PRD-01, PRD-03, PRD-04 (integration-heavy)**:  
  * Required more iteration  
  * Involved handling:  
    * OAuth  
    * Rate limits  
    * API edge cases

---

## **4\. Results Snapshot**

### **Overall Performance**

* **Spec \+ Implementation Alignment:** \~85–90%  
* **T3 Readiness (working apps):** \~88–92%  
* **Platform Validation (`fdk validate`):** \~90–95%  
* **Functional Completeness:** \~85–92%  
* **Advanced Features (T4):** \~40–65%

---

### **By Category**

| Area | Performance |
| ----- | ----- |
| Core functionality | Strong (all PRDs working end-to-end) |
| Platform compliance | High (validation success across apps) |
| UI execution (PRD-02) | Excellent (fast, reliable, clean UX) |
| Integrations (PRD-01, 03, 04\) | Moderate complexity, handled successfully |
| Advanced features | Partially implemented (non-blocking gaps) |

---

## **5\. Time to Execution (Representative)**

| Stage | Time |
| ----- | ----- |
| Initial generation (per PRD) | \~15–30 minutes |
| Working implementation | \~1–2 hours |
| Final validation \+ fixes | Iterative (edge-case dependent) |

**Insight:**  
Skills significantly accelerate development, but **final stability depends on debugging and platform-aware decisions**.

---

## **6\. Key Learnings**

### **1\. Frontend-First Approach is a Force Multiplier (PRD-02)**

* Eliminates timeout issues  
* Reduces dependency on backend  
* Enables faster iteration and cleaner demos

---

### **2\. Integrations Drive Complexity (PRD-01, PRD-03)**

* OAuth flows and multi-source APIs introduce:  
  * Token handling  
  * Pagination  
  * Partial failure states

---

### **3\. Rate Limiting Needs Explicit Design (PRD-04)**

* Required:  
  * 429 handling  
  * Retry \+ backoff  
  * Concurrency control  
* Without this → unstable execution

---

### **4\. Platform Constraints Shape Architecture**

* Serverless limits (timeouts, execution caps)  
* Best practice:  
  * Avoid heavy backend logic  
  * Keep flows controlled and observable

---

### **5\. Skills Accelerate, Judgment Stabilizes**

* Skills → fast scaffolding  
* Engineering decisions → production readiness

---

## **7\. Risks & Gaps Observed**

* OAuth setup complexity (PRD-01)  
* Shopify pagination and token handling (PRD-03)  
* Rate-limit edge cases and retries (PRD-04)  
* Partial completion of advanced features (T4)

---

## **8\. Recommendations**

1. **Default to frontend-first (PRD-02 pattern) for UI-heavy apps**  
2. Use backend only for:  
   * Integrations  
   * Secure operations  
3. Standardize:  
   * Retry \+ backoff logic  
   * Logging and observability  
4. Treat integrations as:  
   * Independent complexity layers  
   * Not just API calls

---

## **9\. Final Takeaway**

This benchmark demonstrates:

* Strong feasibility of building **production-grade Freshdesk apps using skills**  
* High success across:  
  * Functionality  
  * Platform compliance  
  * UI execution

The winning pattern:

Combine **skills for speed** with **frontend-first design and controlled backend usage**

---

## **Document History**

| Version | Date | Notes |
| ----- | ----- | ----- |
| 1.0 | 2026-03-31 | Initial summary |
| 1.1 | 2026-03-31 | All PRDs implemented |
| 1.2 | 2026-03-31 | Corrected PRD numbering |

---

# PRD-01 (Slack \+ GCal \+ Oauth)

## **PRD-01: Freshdesk → Slack Thread \+ Google Calendar Event (OAuth)**

**Version:** 1.0  
**Status:** Draft for team review

**Benchmark Program:** PRD-00 Program Overview and Evaluation Protocol  
**Skills / Platform Context:**

* Freshworks Platform 3.0 skills  
* Freshworks Developer Documentation

---

## **1\. Summary**

Build a **Freshdesk integration app** that automates communication and scheduling when a new ticket is created.

### **Key Capabilities**

* On ticket creation:  
  * Create a **Slack message \+ thread**  
  * Create a **Google Calendar event**  
* Maintain:  
  * OAuth-based integrations with Slack and Google  
  * Secure token storage and refresh  
  * Idempotent execution (no duplicates)

---

## **2\. Problem Statement**

Support teams currently:

* Manually notify teams in Slack  
* Manually schedule follow-ups  
* Duplicate effort across tools

This leads to:

* Delayed coordination  
* Missed follow-ups  
* Operational inefficiency

**Solution:**  
Automate ticket-to-collaboration workflows by:

* Creating Slack visibility  
* Scheduling follow-ups via Calendar  
* Linking everything back to the ticket

---

## **3\. Users & Personas**

| Persona | Need |
| ----- | ----- |
| Admin / Installer | Connect Slack and Google accounts; configure defaults |
| Support Agent | Access Slack thread and meeting link from ticket |

---

## **4\. Scope**

### **4.1 In Scope**

* Freshworks Platform 3.0 app  
* Trigger on **ticket creation event**  
* OAuth integration with:  
  * Slack  
  * Google Calendar

---

### **Core Functionality**

* Create Slack message (thread anchor)  
* Create Google Calendar event  
* Store mappings:  
  * Ticket ID ↔ Slack message  
  * Ticket ID ↔ Calendar event  
* Ensure **idempotency**:  
  * No duplicate Slack messages  
  * No duplicate calendar events

---

### **Slack Behavior**

* Default: create **new message in configured channel**  
* Message acts as thread anchor  
* Includes:  
  * Ticket ID  
  * Subject  
  * Requester  
  * Priority  
  * Ticket URL

---

### **Calendar Event Rules**

| Field | Rule |
| ----- | ----- |
| Title | \[Freshdesk \#ticket\_id\] subject |
| Start Time | Ticket created time \+ 15 minutes |
| Duration | 30 minutes (configurable) |
| Attendees | Configurable default list |
| Description | Ticket URL \+ Slack link |

---

### **Configuration**

* Slack channel selection  
* Timezone  
* Default attendees  
* OAuth connection status

---

### **4.2 Out of Scope**

* Slack → Freshdesk sync  
* Calendar rescheduling on updates  
* Advanced meeting configurations

---

## **5\. Functional Requirements**

| ID | Requirement |
| ----- | ----- |
| FR-1 | Trigger executes on ticket creation |
| FR-2 | Slack message created with ticket details |
| FR-3 | Google Calendar event created |
| FR-4 | OAuth tokens stored securely |
| FR-5 | Tokens refreshed when expired |
| FR-6 | Idempotency prevents duplicate actions |
| FR-7 | Admin UI shows connection status |
| FR-8 | Settings allow configuration of channel, timezone, attendees |

---

## **6\. Non-Functional Requirements**

| ID | Requirement |
| ----- | ----- |
| NFR-1 | Least-privilege OAuth scopes |
| NFR-2 | No hardcoded secrets |
| NFR-3 | Structured logging for API calls and OAuth |
| NFR-4 | Graceful handling of partial failures |

---

## **7\. Acceptance Criteria**

### **Must-Have**

* Ticket creation triggers:  
  * One Slack message  
  * One Calendar event  
* Duplicate events do not create duplicates  
* OAuth setup works independently for Slack and Google  
* Token failures are recoverable  
* Validation passes (`fdk validate`)  
* No exposed credentials

---

### **Should-Have**

* Store Slack and Calendar links on ticket  
* Retry with backoff for API failures

---

## **8\. Dependencies & Assumptions**

* Slack app with OAuth enabled  
* Google Cloud project with Calendar API  
* Freshdesk environment with event triggers

---

## **9\. Security Checklist**

| Check | Pass Criteria |
| ----- | ----- |
| S-1 | No secrets in source control |
| S-2 | OAuth state validated |
| S-3 | Minimal scopes used |
| S-4 | Tokens stored securely |
| S-5 | HTTPS used for redirects |

---

## **10\. Test Plan**

| Scenario | Expected Result |
| ----- | ----- |
| Happy path | Slack \+ Calendar created |
| Duplicate event | No duplicate resources |
| Slack failure | Calendar handled per policy |
| Google auth failure | Token refresh or reconnect required |
| Missing config | Clear error shown |

---

## **11\. Open Questions**

1. Slack threading approach (new message vs existing thread)?  
2. Token model (user vs bot)?  
3. Shared calendar vs individual calendar?

---

## **Document History**

| Version | Date | Changes |
| ----- | ----- | ----- |
| 1.0 | 2026-03-27 | Initial draft |

---

# PRD-02 (Crayons UI)

## **PRD-02: Support Intelligence Hub (Crayons UI)**

**Version:** 1.0  
**Status:** Draft for stakeholder review

**Benchmark Program:** PRD-00 Program Overview and Evaluation Protocol  
**Skills / Platform Context:**

* Freshworks Platform 3.0 skills  
* Freshworks Developer Documentation

---

## **1\. Summary**

Build a **Freshdesk application** with two core surfaces:

* A **full-page dashboard** for managers and team leads  
* A **ticket sidebar** for agents

The app provides **operational visibility and contextual insights** directly within Freshdesk.

### **Key Capabilities**

* Dashboard for:  
  * Queue health  
  * Trends  
  * Backlog visibility  
* Sidebar for:  
  * Ticket context  
  * Related tickets  
  * Playbook guidance

Both surfaces use the **Crayons design system** to ensure consistency, accessibility, and native UX alignment.

---

## **2\. Problem Statement**

Support teams currently:

* Export data to analyze trends  
* Switch between multiple tools  
* Maintain manual reports

This leads to:

* Slower decision-making  
* Duplicate effort  
* Limited real-time visibility

**Solution:**  
Provide **in-product intelligence** via:

* A **dashboard** for planning  
* A **sidebar** for execution

---

## **3\. Users & Personas**

| Persona | Need |
| ----- | ----- |
| Support Manager | Monitor team performance and queue health |
| Team Lead | Analyze trends within team scope |
| Support Agent | Access contextual insights while handling tickets |
| Administrator | Configure and manage app settings |

---

## **4\. Scope**

### **4.1 In Scope**

* Freshworks Platform 3.0 app  
* Two UI surfaces:  
  * Full-page dashboard  
  * Ticket sidebar

---

### **Dashboard Features**

* Global filters (date, group, etc.)  
* KPI cards:  
  * Open tickets  
  * Resolved tickets  
  * Backlog  
* At least:  
  * One trend visualization  
  * One data table

---

### **Sidebar Features**

* Ticket summary  
* Related tickets (same requester)  
* Optional company-level tickets  
* Playbook / checklist

---

### **UI & Data**

* Crayons-based UI across all components  
* Secure server-side data access

---

### **4.2 Out of Scope**

* External CRM integrations  
* OAuth integrations  
* Real-time streaming updates  
* Replacement for native Freshdesk reporting

---

## **5\. Functional Requirements**

| ID | Requirement |
| ----- | ----- |
| FR-1 | Full-page dashboard loads with filters, KPIs, and tables |
| FR-2 | Sidebar loads on ticket detail view |
| FR-3 | Dashboard supports filtering (date, group, etc.) |
| FR-4 | Dashboard displays at least one trend and one table |
| FR-5 | Sidebar shows ticket summary |
| FR-6 | Sidebar shows related tickets for requester |
| FR-7 | Optional company-level tickets supported |
| FR-8 | Sidebar includes playbook checklist |
| FR-9 | Error states handled with user-friendly messaging |
| FR-10 | Admin configuration supported |

---

## **6\. Non-Functional Requirements**

| ID | Requirement |
| ----- | ----- |
| NFR-1 | Platform: Freshworks Platform 3.0 |
| NFR-2 | Performance: \<5 seconds initial load |
| NFR-3 | Accessibility: keyboard navigation and labels |
| NFR-4 | Maintainability: shared logic across surfaces |
| NFR-5 | Resilience: graceful error handling |
| NFR-6 | UI consistency: Crayons-first approach |

---

## **7\. Acceptance Criteria**

### **Must-Have**

* Dashboard loads with:  
  * Filters  
  * KPIs  
  * Table  
* Sidebar displays:  
  * Ticket summary  
  * Related tickets  
  * Playbook  
* Loading and error states implemented  
* App installs successfully  
* No exposed secrets

---

### **Should-Have**

* Company-level related tickets  
* CSV export from dashboard  
* Persistent checklist

---

## **8\. Dependencies & Assumptions**

* Freshdesk environment available  
* API access permissions configured  
* Compatible FDK and Node setup  
* KPI definitions finalized

---

## **9\. Security Checklist**

| Check | Pass Criteria |
| ----- | ----- |
| S-1 | No secrets in frontend code |
| S-2 | Data respects user permissions |
| S-3 | Approved network calls only |
| S-4 | Admin-only configuration access |

---

## **10\. Test Plan**

| Scenario | Expected Result |
| ----- | ----- |
| Dashboard loads | KPIs and data displayed correctly |
| Sidebar loads | Related tickets shown correctly |
| Empty dataset | Proper empty state |
| Restricted user | Limited data visibility |
| API failure | Graceful error handling |
| Small screen | Sidebar remains usable |

---

## **11\. Open Questions**

1. Final KPI definitions  
2. Default date range  
3. Checklist persistence strategy  
4. Charting approach  
5. Company-level ticket requirement

---

## **Document History**

| Version | Date | Changes |
| ----- | ----- | ----- |
| 1.0 | 2026-03-27 | Initial draft |

# PRD-03 (Shopify)

## **PRD-03: Sidebar App — Shopify Multi-Shop Order Details in Freshdesk Ticket Context**

**Version:** 1.0  
**Status:** Draft for team review

**Benchmark Program:** PRD-00 Program Overview and Evaluation Protocol  
**Skills / Platform Context:**

* Freshworks Platform 3.0 skills  
* Freshworks Developer Documentation

---

## **1\. Summary**

Build a **Freshdesk sidebar app** that surfaces **Shopify order details** for the ticket requester across **multiple configured shops**, directly within the ticket view.

### **Key Capabilities**

1. On load:  
   * Resolve requester email across all connected shops  
   * Fetch matching orders  
   * Display a **unified timeline** including:  
     * Order status  
     * Line items  
     * Fulfilment  
     * Refunds  
2. Enable in-context actions:  
   * Refund  
   * Cancel  
   * Create follow-up ticket  
3. Maintain:  
   * Confirmation flows  
   * Private notes on the source ticket for audit

---

## **2\. Problem Statement**

Support agents currently:

* Switch between Freshdesk and multiple Shopify dashboards  
* Spend time manually searching for customer orders  
* Lack a unified view across stores

This results in:

* Slower resolution  
* Context switching overhead  
* Risk of outdated or inconsistent data

**Solution:**  
A sidebar that federates order data across shops using requester email and enables actions directly from the ticket.

---

## **3\. Users & Personas**

| Persona | Need |
| ----- | ----- |
| Support Agent | View and act on orders without leaving ticket |
| Senior Agent / Lead | Perform refunds/cancellations with audit trail |
| Admin | Configure shops, permissions, and allowed actions |

---

## **4\. Scope**

### **4.1 In Scope**

* Freshdesk Platform 3.0 sidebar app  
* Multi-shop configuration:  
  * Store domain  
  * Secure API token  
  * Display name  
  * Active flag  
  * Allowed actions (refund, cancel, follow-up)  
* Parallel data fetching across active shops  
* Shopify Admin API integration (version pinned, e.g. 2024-01)

---

### **UI Requirements**

* Unified order list (newest first)  
* Each order displays:  
  * Shop badge  
  * Order number  
  * Date  
  * Status  
  * Fulfilment  
  * Total  
  * Line items (collapsed by default)  
  * Tracking link (if available)

---

### **Pagination**

* Initial load: up to 10 orders  
* “Load more” continues using per-shop cursors

---

### **Actions**

#### **Refund**

* Confirmation modal  
* API call  
* Private note on ticket

#### **Cancel**

* Confirmation with reason  
* API call  
* Private note

#### **Follow-up Ticket**

* Opens new Freshdesk ticket  
* Pre-filled with:  
  * Order details  
  * Shop info  
  * Link to source ticket

---

### **Error Handling**

* Per-shop errors shown inline  
* Other shops continue to function

---

### **Security**

* Tokens stored only in:  
  * Secure storage / iparams  
* Never stored in:  
  * Frontend code  
  * Local storage  
  * Ticket fields

---

### **4.2 Out of Scope**

* Real-time sync / webhooks  
* CRM integrations  
* Shopify Plus B2B features  
* Bulk actions  
* Analytics dashboards

---

## **5\. Functional Requirements**

| ID | Requirement |
| ----- | ----- |
| FR-1 | Sidebar loads only if requester email exists |
| FR-2 | Parallel shop queries with per-shop loading states |
| FR-3 | No customer in a shop → show “No orders found” |
| FR-4 | Unified timeline sorted newest first |
| FR-5 | Pagination with “Load more” |
| FR-6 | Refund flow with modal, API call, and private note |
| FR-7 | Cancel flow with confirmation and private note |
| FR-8 | Follow-up ticket pre-filled with order details |
| FR-9 | Private notes include actor, time, shop, action, outcome |
| FR-10 | Auth failure isolated per shop |
| FR-11 | Actions hidden based on allowed\_actions |
| FR-12 | Confirmation required before refund/cancel |
| FR-13 | Prevent duplicate actions for terminal states |
| FR-14 | Disable actions during API execution |

---

## **6\. Non-Functional Requirements**

| ID | Requirement |
| ----- | ----- |
| NFR-1 | Logging includes shop, status, and action outcomes |
| NFR-2 | Non-blocking UI with loading skeletons |
| NFR-3 | No hardcoded credentials; validation passes |
| NFR-4 | Document minimum Shopify scopes |

---

## **7\. Acceptance Criteria**

### **Must-Have**

* Sidebar loads with valid requester email  
* Orders displayed from all configured shops  
* Partial failures do not break overall experience  
* Refund/cancel actions:  
  * Execute successfully  
  * Add private notes  
* Follow-up ticket creation works  
* No exposed credentials  
* Validation passes  
* Documentation includes setup and scopes

---

### **Should-Have**

* Correct per-shop pagination  
* Short-term caching (e.g., 60 seconds)

---

## **8\. Dependencies & Assumptions**

* Shopify Admin API access per shop  
* Freshdesk sandbox environment  
* Test stores with matching customer data

---

## **9\. Security Checklist**

| Check | Pass Criteria |
| ----- | ----- |
| S-1 | No API tokens in source control |
| S-2 | Tokens stored securely |
| S-3 | Minimal required scopes |
| S-4 | No secrets in UI or ticket data |

---

## **10\. Test Plan**

| Scenario | Expected Result |
| ----- | ----- |
| Single shop | Orders display correctly |
| Multiple shops | Unified timeline with badges |
| Missing customer | “No orders found” per shop |
| Invalid credentials | Error only for that shop |
| Refund/Cancel | Works \+ logs private note |
| Restricted actions | Buttons hidden |
| Terminal orders | No duplicate API calls |
| Follow-up ticket | Pre-filled ticket created |
| Large dataset | Pagination works |

---

## **11\. Open Questions**

1. Authentication approach: static token vs OAuth?  
2. Refund scope: full vs partial refunds?  
3. Currency handling: per-shop currency only?  
4. API version confirmation (e.g., 2024-01)?  
5. Maximum number of shops supported?

---

## **Document History**

| Version | Date | Changes |
| ----- | ----- | ----- |
| 1.0 | 2026-03-27 | Initial draft |
| 1.1 | 2026-03-27 | Lean revision |

# PRD-04 (Rate-Limit)

## **PRD-04: Sidebar App — Bulk Ticket Creation with Rate-Limit Handling**

**Version:** 1.0  
**Status:** Draft for team review

**Benchmark Program:** PRD-00 Program Overview and Evaluation Protocol  
**Skills / Platform Context:**

* Freshworks Platform 3.0 skills  
* Freshworks Developer Documentation

---

## **1\. Summary**

Build a **Freshdesk sidebar app** that enables **bulk ticket creation** from a single action within the ticket view.

### **Core Behavior**

* A single primary button triggers bulk creation  
* Tickets are created in **batches** via Freshdesk API  
* System intentionally **hits rate limits** to test handling

### **Key Capabilities**

* Proper handling of:  
  * Rate limits (429 responses)  
  * Retry logic  
  * Backoff strategies  
* Real-time **progress visibility**  
* Run summary with outcomes

---

## **2\. Problem Statement**

Bulk ticket creation is required for:

* Internal tooling  
* Data migrations  
* Automation workflows

However, naive implementations:

* Hit API rate limits  
* Cause partial failures  
* Lack visibility into execution

**Solution:**  
A reference implementation that:

* Handles rate limits correctly  
* Provides clear progress and results  
* Demonstrates best practices for bulk operations

---

## **3\. Users & Personas**

| Persona | Need |
| ----- | ----- |
| Agent (Power User) | Trigger bulk operations, monitor progress, cancel if needed |
| Admin | Configure batch size, concurrency, and defaults |

---

## **4\. Scope**

### **4.1 In Scope**

* Freshdesk Platform 3.0 sidebar app  
* Primary action button:  
  * “Create bulk tickets”

---

### **Configuration**

* Default ticket count: **50**  
* Must support at least **100** tickets  
* Configurable parameters:  
  * Batch size (default: 10\)  
  * Concurrency strategy (documented)

---

### **Rate Limiting Behavior**

* Handle HTTP **429 responses**  
* Respect **Retry-After header**  
* Use **exponential backoff with jitter** if header missing  
* Enforce **global concurrency cap** (e.g., max 3 in-flight requests)

---

### **UI Requirements**

* Real-time progress display:  
  * Created count  
  * Failed count  
  * Current state:  
    * Running  
    * Paused (rate limit)  
    * Completed  
    * Cancelled

---

### **Run Summary**

* Display:  
  * Total requested  
  * Successfully created  
  * Failed  
  * Duration  
  * Rate-limit pause count  
* Export options:  
  * Copy as text  
  * Download JSON

---

### **Idempotency (Recommended)**

* Optional batch ID  
* Stored in:  
  * Ticket custom field OR  
  * Description footer  
* Helps prevent duplicate runs

---

### **4.2 Ticket Payload Rules**

Each ticket must be unique and traceable:

| Field | Rule |
| ----- | ----- |
| Subject | Bulk load {batch\_id} \#{index} – truncated original subject |
| Description | Include source ticket ID \+ timestamp |
| Requester | Same as source ticket (fallback if needed) |
| Priority / Status / Group | Copy from source where possible |

---

### **4.3 Out of Scope**

* Production-grade throughput guarantees  
* Multiple parallel runs  
* Full analytics dashboard

---

## **5\. Functional Requirements**

| ID | Requirement |
| ----- | ----- |
| FR-1 | Sidebar loads without errors |
| FR-2 | Button disabled during active run (unless cancel implemented) |
| FR-3 | Creates N tickets from current ticket context |
| FR-4 | Handles 429 with pause and resume |
| FR-5 | Retries on 5xx/network errors with backoff |
| FR-6 | Optional state persistence across reload |
| FR-7 | Non-retryable 4xx handled per policy (skip or abort) |

---

## **6\. Non-Functional Requirements**

| ID | Requirement |
| ----- | ----- |
| NFR-1 | Logging: batch progress, HTTP status, retry behavior |
| NFR-2 | Safety: confirmation dialog for large runs (N ≥ 20\) |
| NFR-3 | No hardcoded credentials |
| NFR-4 | Non-blocking UI (chunked execution) |

---

## **7\. Acceptance Criteria**

### **Must-Have**

* Sidebar loads and button works  
* Run with N=50:  
  * Completes OR  
  * Ends with clear summary  
* Proper rate-limit handling:  
  * No tight retry loops  
  * Backoff applied  
* Final summary includes:  
  * Requested  
  * Created  
  * Failed  
  * Duration  
  * Rate-limit pauses  
* Test path for 429 simulation documented  
* Validation passes (`fdk validate`)  
* No secrets exposed

---

### **Should-Have**

* Cancel functionality  
* Single-run mutex  
* Reload recovery

---

## **8\. Metrics for Benchmark**

| Metric | Capture Method |
| ----- | ----- |
| 429 count | Logs / summary |
| Total time (N=100) | Stopwatch \+ summary |
| Max retry depth | Logs |
| Retry-After compliance | Code review \+ logs |

---

## **9\. Test Plan**

| Scenario | Expected Result |
| ----- | ----- |
| N=10 (no throttling) | All tickets created |
| Forced 429 | Backoff works; no retry loops |
| Intermittent 500 | Retries executed; failures counted |
| Invalid requester | Fallback works; no crash |

---

## **10\. Open Questions**

1. Should default be concurrent or sequential processing?  
2. Maximum safe ticket count (e.g., 500)?  
3. API authentication approach (API key vs OAuth)?

---

## **Document History**

| Version | Date | Changes |
| ----- | ----- | ----- |
| 1.0 | 2026-03-27 | Initial draft |

---

