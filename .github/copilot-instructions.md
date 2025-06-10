# AZURE SDK FOR PYTHON - COPILOT INSTRUCTIONS

---

## CORE PRINCIPLES

### RULE 1: DO NOT REPEAT INSTRUCTIONS
**NEVER repeat instructions when guiding users. Users should follow instructions independently.**

### RULE 2: REFERENCE OFFICIAL DOCUMENTATION
**ALWAYS** reference the [Azure SDK Python Design Guidelines](https://azure.github.io/azure-sdk/python_design.html)
- Link to specific pages when answering guidelines questions
- Use this as the authoritative source for SDK development guidance

### RULE 3: VERIFY ENVIRONMENT FIRST
**BEFORE any commands:**
1. Get path to azure-sdk-for-python repo root, and path to tox.ini file
2. Use `verify_setup` tool from azure-sdk-python-mcp server
3. Ensure Python virtual environment is active

**Virtual Environment Setup:**
```bash
# Create new environment
python -m venv <env_name>

# Activate environment
# Linux/macOS:
source <env_name>/bin/activate
# Windows:
<env_name>\Scripts\activate
```

---

## TYPESPEC SDK GENERATION - COMPLETE WORKFLOW

### PHASE 1: CONTEXT ASSESSMENT

**ACTION:** Determine TypeSpec project location
```
IF TypeSpec project paths exist in context:
    USE local paths to generate SDK from tspconfig.yaml
ELSE:
    ASK user for tspconfig.yaml file path
```

### PHASE 2: PREREQUISITES CHECK

**REQUIRED CONDITIONS:**
1. GitHub CLI authenticated: `gh auth login`
2. User on feature branch (NOT main)
   ```bash
   git checkout -b <branch_name>
   ```

### PHASE 3: TSP-CLIENT RULES

**CRITICAL RULES:**
- **LOCAL REPO:** Do NOT grab commit hash
- **DIRECTORIES:** Let commands auto-create directories
- **PACKAGE GENERATION:** Find tsp-location.yaml in azure-sdk-for-python repo
- **URL REFERENCES:** Use commit hash (NOT branch name) for tspconfig.yaml URLs

**Get latest commit hash:**
```bash
curl -s "https://api.github.com/repos/Azure/azure-rest-api-specs/commits?path=<path_to_tspconfig.yaml>&per_page=1"
```

**DEPENDENCIES:** Verify installation of: node, python, tox

---

## EXECUTION SEQUENCE - 7 MANDATORY STEPS

**ESTIMATED TOTAL TIME: 10-15 minutes**
- SDK Generation: 5-6 minutes
- Static Validation: 3-5 minutes  
- Documentation & Commit: 2-4 minutes

**ALWAYS inform users of time expectations before starting any long-running operations.**

### STEP 1: ENVIRONMENT VERIFICATION
```
ACTION: Run verify_setup mcp tool
IF missing dependencies:
    STOP and install missing dependencies
    THEN proceed to Step 2
```

### STEP 2: SDK GENERATION
```
ACTION: Use azure-sdk-python-mcp sdk generation server tools (init, init_local)
TIMING: ALWAYS inform user before starting: "This SDK generation step will take approximately 5-6 minutes to complete."
IF local path provided:
    USE local mcp tools with tspconfig.yaml path
IF commands fail:
    ANALYZE error messages
    DIRECT user to fix TypeSpec errors in source repo
```

### STEP 3: STATIC VALIDATION (SEQUENTIAL)
```
TIMING: Inform user: "Static validation will take approximately 3-5 minutes for each step."
FOR EACH validation step:
    RUN validation (tox mcp tool)
    IF errors/warnings found:
        FIX issues
        RERUN same step
    ONLY proceed to next step when current step passes
```

**Validation Commands:**
```bash
# Step 3a: Pylint
tox -e pylint -c [path to tox.ini] --root .

# Step 3b: MyPy  
tox -e mypy -c [path to tox.ini] --root .

# Step 3c: Pyright
tox -e pyright -c [path to tox.ini] --root .

# Step 3d: Verifytypes
tox -e verifytypes -c [path to tox.ini] --root .
```

**REQUIREMENTS:**
- Provide summary after each validation step
- Edit ONLY files with validation errors/warnings
- Fix each issue before proceeding

### STEP 4: DOCUMENTATION UPDATE
```
REQUIRED ACTIONS:
1. CREATE/UPDATE CHANGELOG.md with changes
2. VERIFY package version matches API spec version
3. IF version incorrect: UPDATE _version.py AND CHANGELOG
4. SET CHANGELOG entry date to TODAY
```

### STEP 5: COMMIT AND PUSH
```
ACTION: Show changed files (ignore .github, .vscode)
IF user confirms:
    git add <changed_files>
    git commit -m "<commit_message>"
    git push -u origin <branch_name>
IF authentication fails:
    PROMPT: gh auth login
IF user rejects:
    GUIDE to fix issues and revalidate
```

### STEP 6: PULL REQUEST MANAGEMENT
```
CHECK: Does PR exist for current branch?
IF PR exists:
    SHOW PR details
IF NO PR exists:
    VERIFY branch != "main"
    PUSH changes to remote
    GENERATE PR title and description
    CREATE PR in DRAFT mode
    RETURN PR link
ALWAYS: Display PR summary with status, checks, action items
```

### STEP 7: HANDOFF
```
FINAL ACTIONS:
1. RETURN PR URL for review
2. PROMPT user with exact text:
   "Use the azure-rest-api-specs agent to handle the rest of the process and provide it the pull request."
```

---

## PYLINT OPERATIONS

### RUNNING PYLINT

**REFERENCE DOCUMENTATION:**
- [Official pylint guide](https://github.com/Azure/azure-sdk-for-python/blob/main/doc/dev/pylint_checking.md)
- [Tox formatting guide](https://github.com/Azure/azure-sdk-for-python/blob/main/doc/dev/tests.md#tox)

**COMMAND:**
```bash
tox -e pylint --c <path_to_tox.ini> --root .
```

**DEFAULT PATH:** `azure-sdk-for-python/eng/tox/tox.ini`

### FIXING PYLINT WARNINGS

**REFERENCE SOURCES:**
- [Azure pylint guidelines](https://github.com/Azure/azure-sdk-tools/blob/main/tools/pylint-extensions/azure-pylint-guidelines-checker/README.md)
- [Pylint documentation](https://pylint.readthedocs.io/en/stable/user_guide/checkers/features.html)

**ALLOWED ACTIONS:**
✅ Fix warnings with 100% confidence
✅ Use existing file for all solutions
✅ Reference official guidelines

**FORBIDDEN ACTIONS:**
❌ Fix warnings without complete confidence
❌ Create new files for solutions
❌ Import non-existent modules
❌ Add new dependencies/imports
❌ Make unnecessary large changes
❌ Change code style without reason
❌ Delete code without clear justification

---

## MYPY OPERATIONS

### RUNNING AND FIXING MYPY

**REFERENCE DOCUMENTATION:**
- [Tox guidance](https://github.com/Azure/azure-sdk-for-python/blob/main/doc/dev/tests.md#tox)
- [MyPy fixing guide](https://github.com/Azure/azure-sdk-for-python/blob/main/doc/dev/static_type_checking_cheat_sheet.md)

**REQUIREMENTS:**
- Use Python 3.9 compatible environment
- Follow official fixing guidelines
- Use tox mcp tool for running MyPy

---

## Python SDK Health tool

- Use the azure-sdk-python-mcp mcp tool to lookup a library's health status.
- Always include the date of last update based on the Last Refresh date.
- Explanation of statuses can be found here: https://github.com/Azure/azure-sdk-for-python/blob/main/doc/repo_health_status.md
- Release blocking checks are MyPy, Pylint, Sphinx, and Tests - CI. These checks should all PASS. If not PASS, mention that the library is blocked for release.
- If links are available in the table, make the statuses (e.g. PASS, WARNING, etc) you report linked. Avoid telling the user to check the links in the report themselves.
- Don't share information like SDK Owned

### Example

As of <Last Refresh date>, here is the health status for azure-ai-projects:

Overall Status: ⚠️ NEEDS_ACTION

✅ Passing Checks:

Pyright: PASS
Sphinx: PASS
Type Checked Samples: ENABLED
SLA Questions and Bugs: 0

⚠️ Areas Needing Attention:

Pylint: WARNING
Tests - Live: ❓ UNKNOWN
Tests - Samples: ❌ DISABLED
Customer-reported issues: 🔴 5 open issues

❌ Release blocking

Mypy: FAIL
Tests - CI: FAIL

This library is failing two release blocking checks - Mypy and Tests - CI. The library needs attention primarily due to Pylint warnings, disabled sample tests, and open customer-reported issues.
