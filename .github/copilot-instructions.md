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

## EXECUTION SEQUENCE - 6 MANDATORY STEPS

### STEP 1: ENVIRONMENT VERIFICATION
```
ACTION: Run verify_setup tool
IF missing dependencies:
    STOP and install missing dependencies
    THEN proceed to Step 2
```

### STEP 2: COMMIT ID RETRIEVAL
```
ACTION: ask user provide commit id
```

### STEP 3: SDK GENERATION
```
ACTION: Use typespec-python mcp server tools
TIMING: ALWAYS inform user before starting: "This SDK generation step will take approximately 5-6 minutes to complete."
IF local path provided:
    USE local mcp tools `init_local` with tspconfig.yaml path and commit id to generate SDK
IF commands fail:
    ANALYZE error messages
    DIRECT user to fix TypeSpec errors in source repo
```

### STEP 4: COMMIT AND PUSH
```
ACTION: Show changed files in sdk repo (ignore .github, .vscode)
IF user confirms:
    git add <changed_files>
    git commit -m "<commit_message>"
    git push -u origin <branch_name>
IF authentication fails:
    PROMPT: gh auth login
IF user rejects:
    GUIDE to fix issues and revalidate
```

### STEP 5: PULL REQUEST MANAGEMENT
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

### STEP 6: HANDOFF
```
FINAL ACTIONS: return PR url for user to review.
```
