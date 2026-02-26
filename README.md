# Freshworks Platform 3.0 - Benchmarking Suite

Automated testing and validation system for Freshworks marketplace apps with intelligent error learning.

## 🎯 Overview

Validates Platform 3.0 compliance, Crayons UI usage, and learns from validation failures to improve app generation over time.

## 📁 Project Structure

```
benchmarking/
├── automate_test.py           # Main automation script
├── error_learner.py            # Error pattern detection & learning
├── requirements.txt            # Python dependencies
├── use-cases/                  # Test case definitions
├── test-criteria/              # Validation criteria per app
├── results/                    # Benchmarking scores & reports
├── test-apps/                  # Sample test applications
└── .dev/                       # Error learning data
    ├── comparison/error_database.json
    └── planning/AUTO_SKILL_UPDATES.md
```

## 🚀 Quick Start

### Prerequisites

```bash
pip install -r requirements.txt
npm install -g @freshworks/fdk
```

### Run Tests

```bash
cd benchmarking

# Test a specific app
python3 automate_test.py --app APP003

# View error statistics
python3 automate_test.py --show-stats

# Generate skill improvement suggestions
python3 automate_test.py --generate-skill-updates
```

## 📊 Scoring System

Apps are scored on a **100-point scale** with letter grades (A-F):

| Category | Weight | Points | Description |
|----------|--------|--------|-------------|
| **FDK Validation** | 20% | 20 | Pass/fail FDK validation |
| **File Structure** | 20% | 20 | Required files present |
| **Platform 3.0 Compliance** | 40% | 40 | 5 checks × 8 pts each |
| **Crayons Usage** | 20% | 20 | UI component library usage |

**Grade Scale**: A (90-100) • B (80-89) • C (70-79) • D (60-69) • F (<60)

## 🧠 Error Learning System

Automatically tracks validation failures and generates improvement suggestions.

**How it works:**
1. Records FDK validation errors with context
2. Identifies patterns across multiple apps
3. Generates actionable skill improvements
4. Tracks which patterns have been resolved

**Common patterns tracked:**
- `deprecated_request_api` - Using old request methods
- `async_no_await` - Async functions without await
- `request_schema_error` - Incorrect request template structure
- `invalid_location` - Wrong location placement
- `oauth_integrations` - OAuth config structure issues

**Commands:**
```bash
# View error statistics
python3 error_learner.py stats

# Generate skill improvement suggestions
python3 error_learner.py suggest

# View generated suggestions
cat .dev/planning/AUTO_SKILL_UPDATES.md
```

**Example output:**
```
📊 Error Learning Statistics
Total errors recorded: 2
Unique patterns: 4
Fixed patterns: 0
Unfixed patterns: 4

Most common patterns:
  ❌ request_schema_error: 3 occurrences
  ❌ deprecated_request_api: 2 occurrences
  ❌ async_no_await: 2 occurrences
  ❌ product_field_deprecated: 1 occurrences
```

**Data stored in:**
- Error Database: `.dev/comparison/error_database.json`
- Skill Updates: `.dev/planning/AUTO_SKILL_UPDATES.md`

## 📋 Use Cases

7 predefined test cases covering various app types:

| ID | Name | Type | Product |
|----|------|------|---------|
| APP001 | MS Teams Presence Checker | Frontend | Freshservice |
| APP002 | Freshservice-Asana Sync | Serverless | Freshservice |
| APP003 | Freshdesk-GitHub Integration | Frontend | Freshdesk |
| APP004 | Password Generator | Frontend | Freshservice |
| APP005 | Freshdesk-Zapier Contact Sync | Serverless | Freshdesk |
| APP006 | Jira-Freshdesk OAuth Sync | Serverless | Freshdesk |
| APP007 | Ticket Field Validation | Frontend | Freshdesk |

## 🛠️ Adding Custom Apps

**Step 1:** Copy app to `benchmarking/test-apps/YOUR-APP-NAME/`

**Step 2:** Add to `use-cases/use_cases.json`:
```json
{
  "id": "APP008",
  "name": "My Custom App",
  "app_type": "Frontend",
  "product": "freshdesk",
  "prompt": "Description of your app",
  "expected_files": ["manifest.json", "app/index.html", "app/scripts/app.js"]
}
```

**Step 3:** Create `test-criteria/APP008-criteria.json` (optional)

**Step 4:** Run `python3 automate_test.py --app APP008`

## 🔄 Workflow

```
Run Tests → Capture Errors → Identify Patterns → Generate Suggestions → Apply Fixes → Verify
```

## 💡 Best Practices

- Check error stats regularly after test runs
- Generate suggestions when patterns reach 2+ occurrences
- Review and apply skill updates to improve app generation
- Re-run tests to verify improvements

---

**Last Updated**: February 26, 2026 • Internal Freshworks tool for marketplace app quality assurance
