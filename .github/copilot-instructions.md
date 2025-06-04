# AZURE SDK FOR PYTHON - COPILOT INSTRUCTIONS

---

## CORE PRINCIPLES

### RULE 1: DO NOT REPEAT INSTRUCTIONS
**NEVER repeat instructions when guiding users. Users should follow instructions independently.**

### RULE 2: REFERENCE OFFICIAL DOCUMENTATION
**ALWAYS** reference the [Azure SDK Python Design Guidelines](https://azure.github.io/azure-sdk/python_design.html)
- Link to specific pages when answering guidelines questions
- Use this as the authoritative source for SDK development guidance
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

## EXECUTION SEQUENCE - 7 MANDATORY STEPS

### STEP 1: ENVIRONMENT VERIFICATION
```
ACTION: Run verify_setup tool
IF missing dependencies:
    STOP and install missing dependencies
    THEN proceed to Step 2
```

### STEP 2: SDK GENERATION
ACTION: ask user provide commit id

### STEP 2: SDK GENERATION
```
ACTION: Use typespec-python mcp server tools
TIMING: ALWAYS inform user before starting: "This SDK generation step will take approximately 5-6 minutes to complete."
IF local path provided:
    USE local mcp tools with tspconfig.yaml path and commit id
IF commands fail:
    ANALYZE error messages
    DIRECT user to fix TypeSpec errors in source repo
```

### STEP 3: COMMIT AND PUSH
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

### STEP 4: PULL REQUEST MANAGEMENT
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