# Freshworks Platform 3.0 - Benchmarking Suite

Automated testing and validation system for Freshworks marketplace apps with intelligent error learning.

## 🎯 Overview

Validates Platform 3.0 compliance, Crayons UI usage, and learns from validation failures to improve app generation over time.

### Quick Reference

**Two Testing Modes:**
1. **Generate & Test** - Create new apps from prompts and validate
2. **Evaluate** - Test existing apps without regeneration

**Key Features:**
- ✅ **Quick Setup Script** - Interactive criteria creation and app setup
- ✅ FDK validation with detailed error reporting
- ✅ Platform 3.0 compliance checking (5 criteria)
- ✅ Crayons UI component detection
- ✅ Automated error learning and pattern detection
- ✅ Custom requirements tracking
- ✅ 100-point scoring with letter grades (A-F)

## 📁 Project Structure

```
benchmarking/
├── automate_test.py           # Main automation script
├── setup_test.py              # Quick setup for criteria & apps
├── convert_criteria.py        # Plain text to JSON converter (NEW!)
├── error_learner.py            # Error pattern detection & learning
├── requirements.txt            # Python dependencies
├── example-criteria.json       # Example criteria template
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

# MODE 1: Generate & Test New Apps
python3 automate_test.py --app APP003

# MODE 2: Evaluate Existing Apps (Quick Setup)
# Step 1: Setup accepts BOTH plain text and JSON!
python3 setup_test.py APP001
# (paste plain text OR JSON, type 'END')

# Step 2: Run evaluation with saved criteria file
python3 automate_test.py --evaluate test-apps/APP001 --app-id APP001 --requirements test-criteria/APP001-criteria.json

# OR with comma-separated requirements
python3 automate_test.py --evaluate test-apps/APP001 --app-id APP001 --requirements "OAuth,Webhooks"

# MODE 3: Evaluate Existing Apps (Direct)
python3 automate_test.py --evaluate test-apps/zapier --app-id APP005
python3 automate_test.py --evaluate test-apps/zapier --requirements "OAuth,Events,Sync"

# Error Learning & Statistics
python3 automate_test.py --show-stats
python3 automate_test.py --generate-skill-updates
```

## 📝 How to Test - Step by Step

### Option 1: Test a New App (Generate & Validate)

**Step 1: Choose or Create a Use Case**

```bash
# View available use cases
cat use-cases/use_cases.json | grep '"id"'

# Available: APP001, APP002, APP003, APP004, APP005, APP006, APP007
```

**Step 2: Run the Test Command**

```bash
python3 automate_test.py --app APP003
```

**Step 3: Generate the App**

The script will:
- Display the prompt for the app
- Wait for you to generate the app in a separate Cursor window
- Prompt you to press ENTER when ready

**Step 4: Press ENTER to Validate**

The script will automatically:
- Run FDK validation
- Check Platform 3.0 compliance
- Detect Crayons usage
- Calculate score and grade

**Step 5: Review Results**

```bash
# View results
cat results/APP003_result.json

# Check for errors
python3 automate_test.py --show-stats
```

---

### Option 2: Test an Existing App (Quick Setup)

**Step 1: Run Setup Script**

```bash
python3 setup_test.py APP001
```

**Step 2: Paste Your Criteria**

You can paste either plain text OR JSON:

**Plain Text (Easiest):**
```
Requirements:
- OAuth 2.0
- Webhooks
- Platform 3.0

Features:
- Request templates
- Data methods

Description:
Ticket automation app

END
```

**Or JSON:**
```json
{
  "requirements": ["OAuth 2.0", "Webhooks", "Platform 3.0"],
  "expected_files": ["manifest.json", "server/server.js"],
  "description": "Ticket automation app"
}
END
```

**Step 3: Copy Your App**

```bash
# Copy your existing app to test-apps/
cp -r /path/to/your/app/* test-apps/APP001/
```

**Step 4: Run Evaluation**

```bash
# Use the command provided by setup script
python3 automate_test.py --evaluate test-apps/APP001 --app-id APP001 --requirements test-criteria/APP001-criteria.json
```

**Step 5: Review Results**

```bash
cat results/APP001_result.json
```

---

### Option 3: Test an Existing App (Direct)

**Step 1: Copy App to test-apps/**

```bash
cp -r /path/to/my-freshdesk-app test-apps/my-app
```

**Step 2: Run Evaluation**

```bash
# Basic evaluation
python3 automate_test.py --evaluate test-apps/my-app

# With custom requirements
python3 automate_test.py --evaluate test-apps/my-app --requirements "OAuth 2.0,Webhooks,Crayons UI"

# With custom app ID
python3 automate_test.py --evaluate test-apps/my-app --app-id MY_APP_001
```

**Step 3: Review Results**

```bash
# Results saved as EVAL_MY-APP_result.json or MY_APP_001_result.json
cat results/EVAL_MY-APP_result.json
```

---

### Option 4: Batch Testing Multiple Apps

**Step 1: Prepare Apps**

```bash
# Copy multiple apps
cp -r /path/to/app1 test-apps/app1
cp -r /path/to/app2 test-apps/app2
cp -r /path/to/app3 test-apps/app3
```

**Step 2: Test Each App**

```bash
python3 automate_test.py --evaluate test-apps/app1 --app-id APP_001
python3 automate_test.py --evaluate test-apps/app2 --app-id APP_002
python3 automate_test.py --evaluate test-apps/app3 --app-id APP_003
```

**Step 3: View Statistics**

```bash
# View error patterns across all tests
python3 automate_test.py --show-stats

# Generate improvement suggestions
python3 automate_test.py --generate-skill-updates
```

**Step 4: Compare Results**

```bash
# View all results
ls -lh results/

# Compare scores
grep -A 3 '"score"' results/APP_00*.json
```

---

### Understanding Test Results

**What Gets Checked:**

1. ✅ **FDK Validation** (20 points)
   - Runs `fdk validate`
   - Checks for syntax errors
   - Validates manifest.json structure

2. ✅ **File Structure** (20 points)
   - Verifies required files exist
   - Checks manifest.json, server.js (if serverless), app files

3. ✅ **Platform 3.0 Compliance** (40 points)
   - Platform version 3.0 (8 pts)
   - Uses 'modules' structure (8 pts)
   - No whitelisted-domains (8 pts)
   - Engines block present (8 pts)
   - Correct location placement (8 pts)

4. ✅ **Crayons Usage** (20 points)
   - Detects fw-* components
   - Checks for Crayons imports

**Result File Structure:**

```json
{
  "app_id": "APP001",
  "timestamp": "2026-02-26T10:30:00",
  "score": {
    "total_score": 85.0,
    "percentage": 85.0,
    "grade": "B",
    "breakdown": {
      "fdk_validation": 20,
      "file_structure": 20,
      "platform3_compliance": 32,
      "crayons_usage": 13
    }
  },
  "validation": {
    "success": true,
    "errors": [],
    "warnings": []
  },
  "platform3_compliance": {
    "platform_version_3_0": true,
    "modules_structure": true,
    "no_whitelisted_domains": true,
    "engines_present": true,
    "correct_location_placement": true
  },
  "requirements_met": {
    "OAuth 2.0": true,
    "Webhooks": true,
    "Platform 3.0": true
  }
}
```

---

### Common Testing Scenarios

**Scenario 1: Test Before Deployment**

```bash
# Copy production app
cp -r /path/to/prod-app test-apps/prod-app

# Validate
python3 automate_test.py --evaluate test-apps/prod-app --app-id PROD_V1

# Check score (should be A or B)
grep '"grade"' results/PROD_V1_result.json
```

**Scenario 2: Compare Two Versions**

```bash
# Test version 1
python3 automate_test.py --evaluate test-apps/app-v1 --app-id APP_V1

# Test version 2
python3 automate_test.py --evaluate test-apps/app-v2 --app-id APP_V2

# Compare scores
diff results/APP_V1_result.json results/APP_V2_result.json
```

**Scenario 3: Track Improvements**

```bash
# Test 1: Initial version
python3 automate_test.py --evaluate test-apps/my-app --app-id TEST_001
# Result: Grade C (75%)

# Fix issues based on results
# ... make changes ...

# Test 2: After fixes
python3 automate_test.py --evaluate test-apps/my-app --app-id TEST_002
# Result: Grade B (85%)

# Compare
diff results/TEST_001_result.json results/TEST_002_result.json
```

**Scenario 4: Validate Specific Requirements**

```bash
# Test with specific requirements
python3 automate_test.py --evaluate test-apps/oauth-app \
  --requirements "OAuth 2.0,Token refresh,Error handling,Crayons UI,Platform 3.0"

# Check which requirements were met
grep -A 10 '"requirements_met"' results/EVAL_OAUTH-APP_result.json
```

---

### Troubleshooting Test Failures

**Low Score? Check These:**

1. **FDK Validation Failed (0/20 points)**
   ```bash
   # Run FDK validate manually to see errors
   cd test-apps/my-app
   fdk validate
   ```

2. **Missing Files (0/20 points)**
   ```bash
   # Check what files are expected
   cat test-criteria/APP001-criteria.json | grep expected_files
   
   # List what you have
   ls -la test-apps/APP001/
   ```

3. **Platform 3.0 Issues (0-32/40 points)**
   ```bash
   # Check manifest.json
   cat test-apps/my-app/manifest.json | grep platform
   cat test-apps/my-app/manifest.json | grep modules
   cat test-apps/my-app/manifest.json | grep engines
   ```

4. **No Crayons (0/20 points)**
   ```bash
   # Search for Crayons components
   grep -r "fw-" test-apps/my-app/app/
   grep -r "crayons" test-apps/my-app/
   ```

---

### Quick Reference Commands

```bash
# Test predefined use case
python3 automate_test.py --app APP003

# Setup new test
python3 setup_test.py APP001

# Evaluate existing app
python3 automate_test.py --evaluate test-apps/my-app

# Evaluate with requirements
python3 automate_test.py --evaluate test-apps/my-app --requirements "OAuth,Webhooks"

# View statistics
python3 automate_test.py --show-stats

# Generate suggestions
python3 automate_test.py --generate-skill-updates

# View results
cat results/APP001_result.json

# List all results
ls -lh results/
```

## 📊 Scoring System

Apps are scored on a **100-point scale** with letter grades (A-F):

| Category | Weight | Points | Description |
|----------|--------|--------|-------------|
| **FDK Validation** | 20% | 20 | Pass/fail FDK validation |
| **File Structure** | 20% | 20 | Required files present |
| **Platform 3.0 Compliance** | 40% | 40 | 5 checks × 8 pts each |
| **Crayons Usage** | 20% | 20 | UI component library usage |

**Platform 3.0 Compliance Checks:**
1. Platform version 3.0
2. Uses 'modules' structure
3. No whitelisted-domains
4. Engines block present
5. Correct location placement (auto-pass for background/serverless apps)

**Grade Scale**: A (90-100) • B (80-89) • C (70-79) • D (60-69) • F (<60)

### Interpreting Results

**Example Result:**
```json
{
  "app_id": "APP003",
  "score": {
    "total_score": 85.0,
    "percentage": 85.0,
    "grade": "B"
  },
  "validation": {
    "success": true,
    "platform_errors": [],
    "lint_errors": []
  },
  "platform3_compliance": {
    "platform_version_3_0": true,
    "modules_structure": true,
    "no_whitelisted_domains": true,
    "engines_present": true,
    "correct_location_placement": true
  }
}
```

**What each grade means:**
- **A (90-100)**: Production-ready, follows all best practices
- **B (80-89)**: Good quality, minor improvements needed
- **C (70-79)**: Functional but needs attention to standards
- **D (60-69)**: Multiple issues, requires fixes before deployment
- **F (<60)**: Significant problems, major refactoring needed

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

## 📖 Usage Examples

### Example 1: Test a Predefined Use Case
```bash
# Test APP003 (Freshdesk-GitHub Integration)
python3 automate_test.py --app APP003

# Opens prompt, you generate in separate Cursor window, then validates
```

### Example 2: Quick Setup (Plain Text or JSON - Both Work!)
```bash
# Step 1: Setup with interactive input
python3 setup_test.py APP001

# Option A: Paste plain text (EASIEST!)
# Requirements:
# - OAuth 2.0
# - Webhooks
# - Platform 3.0
# 
# Features:
# - Request templates
# - Data methods
# - Custom iParams
# 
# Description:
# Ticket automation app
# 
# Type 'END' and press Enter

# OR Option B: Paste JSON
# {
#   "requirements": ["OAuth 2.0", "Webhooks", "Platform 3.0"],
#   "expected_files": ["manifest.json", "server/server.js"],
#   "description": "Ticket automation app"
# }
# Type 'END' and press Enter

# Step 2: Copy your app
cp -r /path/to/your/app/* test-apps/APP001/

# Step 3: Run evaluation using saved criteria file
python3 automate_test.py --evaluate test-apps/APP001 --app-id APP001 --requirements test-criteria/APP001-criteria.json
```

### Example 3: Setup with Existing App
```bash
# Setup and copy app in one command
python3 setup_test.py APP001 --app-path /path/to/your/app

# Then run evaluation
python3 automate_test.py --evaluate test-apps/APP001 --app-id APP001
```

### Example 4: Use Saved Criteria File
```bash
# After running setup_test.py, use the saved criteria file
python3 automate_test.py --evaluate test-apps/APP001 --app-id APP001 --requirements test-criteria/APP001-criteria.json

# This loads:
# - All requirements from the criteria file
# - Expected files list
# - Automatically uses them for validation

# Result: APP001_result.json with all requirements tracked
```

### Example 5: Evaluate an Existing App (Manual)
```bash
# Copy your app to test-apps/
cp -r ~/my-freshdesk-app test-apps/my-app

# Evaluate it
python3 automate_test.py --evaluate test-apps/my-app

# Result: EVAL_MY-APP_result.json with score and grade
```

### Example 6: Evaluate with Custom Requirements
```bash
# Evaluate with specific requirements
python3 automate_test.py --evaluate test-apps/oauth-app \
  --requirements "OAuth 2.0,Token refresh,Webhook support,Crayons UI"

# Requirements are tracked in the results file
```

### Example 7: Compare App Versions
```bash
# Evaluate version 1
python3 automate_test.py --evaluate test-apps/app-v1 --app-id APP_V1

# Evaluate version 2
python3 automate_test.py --evaluate test-apps/app-v2 --app-id APP_V2

# Compare results/APP_V1_result.json vs results/APP_V2_result.json
```

### Example 8: Check Error Patterns
```bash
# Run multiple tests
python3 automate_test.py --app APP001
python3 automate_test.py --app APP002
python3 automate_test.py --app APP003

# View error statistics
python3 automate_test.py --show-stats

# Generate improvement suggestions
python3 automate_test.py --generate-skill-updates
```

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

### Method 1: Quick Setup (Accepts Plain Text or JSON!)

**Interactive mode - paste your criteria in ANY format:**
```bash
python3 setup_test.py APP001

# Option A: Plain Text (EASIEST!)
# TIP: Include "Frontend" or "Serverless" to auto-detect app type!
Requirements:
- Frontend
- OAuth 2.0
- Webhooks
- Platform 3.0

Features:
- Request templates
- Data methods
- Custom iParams

Description:
Ticket automation with external API

# Type 'END' and press Enter
# Auto-detects: Frontend app (no server/server.js expected)

# Option B: JSON format (also works!)
{
  "requirements": ["OAuth 2.0", "Webhooks", "Platform 3.0"],
  "expected_files": ["manifest.json", "server/server.js"],
  "description": "Ticket automation with external API"
}
# Type 'END' and press Enter

# Script automatically:
# 1. Detects format (plain text or JSON)
# 2. Fixes common typos (erverless → Serverless, iparam → iParam, etc.)
# 3. Detects app type (Frontend/Serverless) from requirements
# 4. Generates appropriate expected files based on app type
# 5. Saves criteria to test-criteria/APP001-criteria.json
# 6. Creates test-apps/APP001/ directory
# 7. Shows evaluation command to run
```

**With existing app (one command):**
```bash
# Copy app automatically
python3 setup_test.py APP001 --app-path /path/to/your/app

# Or with criteria file
python3 setup_test.py APP001 --criteria-file my-criteria.json --app-path /path/to/app
```

**Then evaluate:**
```bash
# Use saved criteria file (RECOMMENDED)
python3 automate_test.py --evaluate test-apps/APP001 --app-id APP001 --requirements test-criteria/APP001-criteria.json

# OR use comma-separated requirements
python3 automate_test.py --evaluate test-apps/APP001 --app-id APP001 --requirements "OAuth 2.0,Webhooks,Platform 3.0"
```

### Method 2: Add to Use Cases (For Generation Mode)

**Step 1:** Add to `use-cases/use_cases.json`:
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

**Step 2:** Run `python3 automate_test.py --app APP008`

### Method 3: Manual Evaluation (No Setup Script)

**Step 1:** Copy app to `benchmarking/test-apps/YOUR-APP-NAME/`

**Step 2:** Evaluate with requirements:
```bash
# Option A: Use existing use case ID
python3 automate_test.py --evaluate test-apps/YOUR-APP-NAME --app-id APP008

# Option B: Provide custom requirements
python3 automate_test.py --evaluate test-apps/YOUR-APP-NAME --requirements "OAuth,API integration,Crayons UI"

# Option C: Just validate (no requirements)
python3 automate_test.py --evaluate test-apps/YOUR-APP-NAME
```

**Step 3:** View results in `results/` folder

## 🔄 Workflows

### Workflow 1: Generate & Test New Apps

```
┌─────────────────┐
│ Define Use Case │
│ (use_cases.json)│
└────────┬────────┘
         │
         ▼
┌─────────────────┐      ┌──────────────────┐
│ Run Test Script │─────▶│ Generate in      │
│ --app APP008    │      │ Separate Cursor  │
└────────┬────────┘      └────────┬─────────┘
         │                        │
         │◀───────────────────────┘
         │ Press ENTER
         ▼
┌─────────────────┐
│ FDK Validation  │
│ + Compliance    │
│ + Scoring       │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Results JSON    │
│ + Error Learning│
└─────────────────┘
```

**Commands:**
```bash
# 1. Add use case to use-cases/use_cases.json
# 2. Run test
python3 automate_test.py --app APP008
# 3. Generate in separate Cursor window
# 4. Press ENTER to validate
# 5. Check results in results/APP008_result.json
```

### Workflow 2: Evaluate Existing Apps (Quick Setup)

```
┌─────────────────┐
│ Run setup_test  │
│ python3 setup_  │
│ test.py APP001  │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Paste Criteria  │
│ JSON (or file)  │
└────────┬────────┘
         │
         ▼
┌─────────────────┐      ┌──────────────────┐
│ Criteria Saved  │      │ Directory Created│
│ test-criteria/  │      │ test-apps/APP001 │
└────────┬────────┘      └────────┬─────────┘
         │                        │
         └────────────┬───────────┘
                      │
                      ▼
┌─────────────────────────────────┐
│ Copy App or Generate            │
│ cp -r /path/to/app test-apps/   │
└────────┬────────────────────────┘
         │
         ▼
┌─────────────────┐
│ Run Evaluation  │
│ (command shown  │
│  by setup)      │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ FDK Validation  │
│ + Compliance    │
│ + Scoring       │
└────────┬────────┘
         │
         ▼
┌─────────────────┐      ┌──────────────┐
│ Results JSON    │─────▶│ Fix Issues   │
│ + Error Learning│      │ Re-evaluate  │
└─────────────────┘      └──────────────┘
```

**Commands:**
```bash
# 1. Quick setup with interactive criteria
python3 setup_test.py APP001
# (paste criteria JSON)

# 2. Copy your app
cp -r /path/to/my-app test-apps/APP001/

# 3. Run evaluation (command provided by setup script)
python3 automate_test.py --evaluate test-apps/APP001 --app-id APP001 --requirements "..."

# 4. Check results
cat results/APP001_result.json
```

### Workflow 3: Evaluate Existing Apps (Manual)

```
┌─────────────────┐
│ Existing App    │
│ (any source)    │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Copy to         │
│ test-apps/      │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Run Evaluation  │
│ --evaluate PATH │
│ (+ requirements)│
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ FDK Validation  │
│ + Compliance    │
│ + Scoring       │
└────────┬────────┘
         │
         ▼
┌─────────────────┐      ┌──────────────┐
│ Results JSON    │─────▶│ Fix Issues   │
│ + Error Learning│      │ Re-evaluate  │
└─────────────────┘      └──────────────┘
```

**Commands:**
```bash
# 1. Copy app to test-apps/
cp -r /path/to/my-app test-apps/my-app

# 2. Evaluate with requirements
python3 automate_test.py --evaluate test-apps/my-app --requirements "OAuth,Crayons UI,Platform 3.0"

# 3. Or use existing use case ID
python3 automate_test.py --evaluate test-apps/my-app --app-id APP005

# 4. Check results
cat results/EVAL_MY-APP_result.json
```

## 🎯 Evaluation Mode Features

The `--evaluate` flag enables testing already-generated apps without regeneration:

**Benefits:**
- ✅ Test apps from any source (manual, AI-generated, production)
- ✅ No need to regenerate or modify existing apps
- ✅ Track custom requirements alongside standard checks
- ✅ Compare multiple versions of the same app
- ✅ Validate apps before deployment

**What it checks:**
1. FDK validation (pass/fail)
2. File structure (auto-detected or from use case)
3. Platform 3.0 compliance (5 checks)
4. Crayons UI usage
5. Custom requirements (if provided)

**Example use cases:**
```bash
# Validate a production app before update
python3 automate_test.py --evaluate test-apps/prod-app

# Check if app meets specific requirements
python3 automate_test.py --evaluate test-apps/oauth-app --requirements "OAuth 2.0,Token refresh,Error handling"

# Compare two versions
python3 automate_test.py --evaluate test-apps/v1 --app-id APP_V1
python3 automate_test.py --evaluate test-apps/v2 --app-id APP_V2
```

## 💡 Best Practices

- Check error stats regularly after test runs
- Generate suggestions when patterns reach 2+ occurrences
- Review and apply skill updates to improve app generation
- Re-run tests to verify improvements
- Use evaluation mode to validate apps from any source
- Track requirements for better quality assurance

## 🎛️ Command-Line Options

```bash
python3 automate_test.py [OPTIONS]

Options:
  --app APP_ID              Test a predefined use case (e.g., APP001)
  --evaluate PATH           Evaluate an existing app at PATH
  --app-id ID               Custom app ID for evaluation results
  --requirements "R1,R2"    Comma-separated requirements to track
  --show-stats              Display error learning statistics
  --generate-skill-updates  Generate improvement suggestions
  --benchmark-dir PATH      Custom benchmark directory (default: ~/benchmark-test)
  -h, --help                Show help message
```

**Examples:**
```bash
# Generate and test
python3 automate_test.py --app APP003

# Evaluate existing
python3 automate_test.py --evaluate test-apps/my-app

# Evaluate with requirements
python3 automate_test.py --evaluate test-apps/my-app --requirements "OAuth,Webhooks"

# Custom app ID
python3 automate_test.py --evaluate test-apps/my-app --app-id CUSTOM_001

# Statistics
python3 automate_test.py --show-stats

# Generate suggestions
python3 automate_test.py --generate-skill-updates
```

## 🔧 Troubleshooting

### Common Issues

**Issue: "FDK not found"**
```bash
# Solution: Install FDK globally
npm install -g @freshworks/fdk
```

**Issue: "Use case not found"**
```bash
# Solution: Check use-cases/use_cases.json for valid IDs
cat use-cases/use_cases.json | grep '"id"'
```

**Issue: "App path not found"**
```bash
# Solution: Use relative path from benchmarking/ or absolute path
python3 automate_test.py --evaluate test-apps/my-app  # relative
python3 automate_test.py --evaluate /full/path/to/app  # absolute
```

**Issue: Validation passes but score is low**
- Check Platform 3.0 compliance (40 points)
- Verify Crayons usage (20 points)
- Ensure all expected files are present (20 points)

**Issue: Error learning not working**
```bash
# Check if error_learner.py exists
ls error_learner.py

# Check error database
cat .dev/comparison/error_database.json
```

---

**Last Updated**: February 26, 2026 • Internal Freshworks tool for marketplace app quality assurance
