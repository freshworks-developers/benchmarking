# APP006 — Jira ↔ Freshdesk/Freshservice (serverless)

Platform **3.0** serverless app for **Freshdesk**: Jira Cloud OAuth + helpdesk API key.

## Configure

1. **Atlassian OAuth app (3LO):** Callback URL per Freshworks docs; scopes in `config/oauth_config.json` (`read:jira-work`, `write:jira-work`, etc.). Use placeholder client ID/secret in the OAuth install step until your app is registered.
2. **Jira Cloud ID:** After OAuth, call `GET https://api.atlassian.com/oauth/token/accessible-resources` with the bearer token to read `id` for your site.
3. **Helpdesk:** Enter FQDN (`*.freshdesk.com` or `*.freshservice.com`) and API key. The custom install page builds **Basic** auth (`Base64(api_key:X)`).
4. **Mappings:** JSON maps Jira status names to helpdesk **status IDs** (numeric). Optional priority map reserved for future use.

## Behaviour

- **onAppInstall:** Registers recurring schedule (interval from iparams, minimum 5 minutes).
- **onScheduledEvent:** Polls Jira (`project=KEY`), creates or updates helpdesk tickets; stores `jira_fd_{ISSUE}` → ticket id in `$db`.
- **onTicketCreate:** Creates a Jira issue (issue type from iparams); stores `fd_jira_{ticketId}` → Jira key.
- **onTicketUpdate:** Adds a Jira comment when a linked ticket exists.

## Files

See `test-criteria/APP006-criteria.json` and use case **APP006** in `use-cases/use_cases.json`.

Run: `fdk validate` then `fdk run`.
