# Automatic Skill Updates from FDK Validation Failures

**Generated:** February 26, 2026 at 08:57
**New Patterns Detected:** 3

---

## 📊 Error Patterns Requiring Skill Updates

## 1. Fix request_schema_error

**Pattern:** `request_schema_error`
**Occurrences:** 3
**First Seen:** 2026-02-25T23:45:00.000000
**Target Section:** General

### Examples from Apps

**TEST001:**
```
Request template 'freshdesk_get_contacts' must have required property 'schema'
```

**TEST001:**
```
Request template 'freshdesk_get_contacts' must NOT have additional properties 'protocol'
```

**TEST001:**
```
Request template 'zapier_sync_contact' must have required property 'schema'
```

### Suggested Skill Update

**Add to:** `.cursor/rules/freshworks-platform3.mdc` - General

```markdown
### Rule: Fix request_schema_error

❌ WRONG: Pattern that causes error

✅ CORRECT: Correct pattern

**Explanation:** Based on 3 occurrences
```

### Validation Checklist Addition

```markdown
- [ ] **Fix request_schema_error** ✅
  - Explanation: Based on 3 occurrences
```

---

## 2. NEVER Use Deprecated Request API Methods

**Pattern:** `deprecated_request_api`
**Occurrences:** 2
**First Seen:** 2026-02-25T23:45:00.000000
**Target Section:** Code Quality Requirements

### Examples from Apps

**TEST001:**
```
server/server.js::16: get is no longer supported in Request API
```

**TEST001:**
```
server/server.js::24: post is no longer supported in Request API
```

### Suggested Skill Update

**Add to:** `.cursor/rules/freshworks-platform3.mdc` - Code Quality Requirements

```markdown
### Rule: NEVER Use Deprecated Request API Methods

❌ WRONG: $request.post(), $request.get(), $request.put(), $request.delete()

✅ CORRECT: $request.invokeTemplate()

**Explanation:** Platform 3.0 requires using request templates defined in config/requests.json
```

### Validation Checklist Addition

```markdown
- [ ] **NEVER Use Deprecated Request API Methods** ✅
  - Explanation: Platform 3.0 requires using request templates defined in config/requests.json
```

---

## 3. Only Use async When You Actually await

**Pattern:** `async_no_await`
**Occurrences:** 2
**First Seen:** 2026-02-25T23:45:00.000000
**Target Section:** Code Quality Requirements

### Examples from Apps

**TEST001:**
```
server/server.js::10: Async function 'syncContactsToZapier' has no 'await' expression
```

**TEST001:**
```
app/scripts/app.js::1: Async function has no 'await' expression
```

### Suggested Skill Update

**Add to:** `.cursor/rules/freshworks-platform3.mdc` - Code Quality Requirements

```markdown
### Rule: Only Use async When You Actually await

❌ WRONG: async function without await inside

✅ CORRECT: Remove async keyword if no await

**Explanation:** Unnecessary async keywords cause lint errors
```

### Validation Checklist Addition

```markdown
- [ ] **Only Use async When You Actually await** ✅
  - Explanation: Unnecessary async keywords cause lint errors
```

---
