# AZURE SDK FOR PYTHON - COPILOT INSTRUCTIONS

---

## CORE PRINCIPLES

### RULE 1: DO NOT REPEAT INSTRUCTIONS
**NEVER repeat instructions when guiding users. Users should follow instructions independently.**

### RULE 2: REFERENCE OFFICIAL DOCUMENTATION
**ALWAYS** reference the [Azure SDK Python Design Guidelines](https://azure.github.io/azure-sdk/python_design.html)
- Link to specific pages when answering guidelines questions
- Use this as the authoritative source for SDK development guidance

### RULE 3: FOLLOW CODEGEN WORKFLOW
**BEFORE any TypeSpec SDK generation:**
1. Get path to azure-sdk-for-python repo root and tox.ini file
2. Verify all prerequisites: Python 3.9+, Node.js 20.x+, tsp-client CLI
3. Ensure Python virtual environment is active
4. Follow [Dataplane Codegen Quick Start](https://github.com/Azure/azure-sdk-for-python/wiki/Dataplane-Codegen-Quick-Start) workflow

**Post-Generation Process:**
1. Always reference [What to do after generating SDK code](https://github.com/Azure/azure-sdk-for-python/wiki/What-to-do-after-generating-the-SDK-code-with-codegen)
2. Use tsp-client commands as specified in wiki guidelines
3. Follow the 7-step execution sequence for complete workflow

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

Following the [Dataplane Codegen Quick Start](https://github.com/Azure/azure-sdk-for-python/wiki/Dataplane-Codegen-Quick-Start) guidelines.

### PHASE 1: PREREQUISITES AND SETUP

**REQUIRED DEPENDENCIES:**
1. **Python 3.9 or later** - Use `python --version` to verify
2. **Node.js 20.x LTS or later** - Use `node --version` to verify  
3. **GitHub CLI authenticated** - Use `gh auth login`
4. **tsp-client CLI tool** - Install with `npm install -g @azure-tools/typespec-client-generator-cli`

**REPOSITORY SETUP:**
1. User must be on feature branch (NOT main): `git checkout -b <branch_name>`
2. Ensure azure-sdk-for-python repo is forked and cloned
3. TypeSpec definition must be merged into main branch of azure-rest-api-specs repo

### PHASE 2: PROJECT CONFIGURATION

**KEY INFORMATION NEEDED:**
- `service_name`: Short name for Azure service (matches azure-rest-api-specs folder)
- `namespace`: Python namespace (e.g., azure.ai.anomalydetector)  
- `package_name`: PyPI package name (e.g., azure-ai-anomalydetector)
- `module_name`: Additional component if multiple packages needed

**FOLDER STRUCTURE:**
- SDK path: `sdk/{service_name}/{package_name}/`
- Generated code: `/azure/{service_name}/{module_name}/`
- Tests: `/tests/`
- Samples: `/samples/`

### PHASE 3: TYPESPEC CONFIGURATION

**VERIFY tspconfig.yaml contains:**
```yaml
parameters:
  "service-dir":
    default: "YOUR-SERVICE-DIRECTORY"

emit: [
  "@azure-tools/typespec-autorest",
]

options:
  "@azure-tools/typespec-python":
    package-dir: "YOUR-PACKAGE-DIR"
    namespace: "YOUR.NAMESPACE.NAME"
    flavor: "azure"
```

**TSP-CLIENT USAGE RULES:**
- **INITIAL SETUP:** Use `tsp-client init -c <REMOTE_TSPCONFIG_URL>` from repo root
- **UPDATES:** Use `tsp-client update` from SDK folder with tsp-location.yaml
- **URL FORMAT:** Use commit hash in GitHub URL (NOT branch name)
**DEPENDENCIES:** Verify installation of: node, python, tox

---

## REFERENCE DOCUMENTATION AND GUIDELINES

### CORE REFERENCES
- **[Dataplane Codegen Quick Start](https://github.com/Azure/azure-sdk-for-python/wiki/Dataplane-Codegen-Quick-Start)**: Primary workflow guide
- **[What to do after generating SDK code](https://github.com/Azure/azure-sdk-for-python/wiki/What-to-do-after-generating-the-SDK-code-with-codegen)**: Post-generation enhancements
- **[Azure SDK Design Guidelines](https://azure.github.io/azure-sdk/python_design.html)**: Official design principles
- **[Azure SDK Repo Structure](https://github.com/Azure/azure-sdk/blob/main/docs/policies/repostructure.md#sdk-directory-layout)**: Repository organization

### PROJECT STRUCTURE GUIDELINES

**Service and Package Naming:**
- `service_name`: Matches azure-rest-api-specs folder (e.g., "servicebus")  
- `namespace`: Python import path (e.g., "azure.servicebus")
- `package_name`: PyPI name (e.g., "azure-servicebus")
- `module_name`: Optional for multi-package services (e.g., "azure-synapse-artifacts")

**Folder Structure Pattern:**
```
sdk/{service_name}/{package_name}/
├── azure/{service_name}/{module_name}/     # Generated code
├── tests/                                  # Test files
├── samples/                               # Usage examples  
├── setup.py                              # Package metadata
├── README.md                             # Service documentation
├── CHANGELOG.md                          # Version history
└── _version.py                           # Version info
```

---

## EXECUTION SEQUENCE - FOLLOWING WIKI GUIDELINES

**ESTIMATED TOTAL TIME: 15-20 minutes**
- Environment Setup: 2-3 minutes
- SDK Generation: 5-6 minutes  
- Static Validation: 5-8 minutes
- Documentation & Commit: 3-5 minutes

**ALWAYS inform users of time expectations before starting any long-running operations.**

### STEP 1: ENVIRONMENT VERIFICATION

```
ACTION: Verify all prerequisites are met
DEPENDENCIES: 
  - Python 3.9+ installed and active in virtual environment
  - Node.js 20.x LTS+ installed
  - GitHub CLI authenticated (gh auth login)
  - tsp-client CLI tool installed globally
IF missing dependencies:
    STOP and guide user to install missing dependencies
    THEN proceed to Step 2
```

### STEP 2: SDK GENERATION WITH TSP-CLIENT

```
ACTION: Generate SDK using tsp-client following wiki guidelines
TIMING: ALWAYS inform user: "SDK generation will take approximately 5-6 minutes to complete."

FOR INITIAL SETUP:
  USE: tsp-client init -c <REMOTE_TSPCONFIG_URL>
  FROM: Repository root directory
  URL FORMAT: Must include commit hash (not branch name)

FOR UPDATES:  
  USE: tsp-client update
  FROM: SDK folder containing tsp-location.yaml
  VERIFY: tsp-location.yaml exists and points to correct TypeSpec project

IF commands fail:
    ANALYZE error messages
    CHECK: TypeSpec configuration in tspconfig.yaml
    DIRECT: User to fix TypeSpec errors in azure-rest-api-specs repo
```

### STEP 3: POST-GENERATION VALIDATION AND FIXES

```
TIMING: Inform user: "Post-generation validation will take approximately 5-8 minutes total."
REFERENCE: Follow "What to do after generating the SDK code with codegen" guidelines

SEQUENTIAL VALIDATION STEPS:
FOR EACH validation step:
    RUN validation using tox from azure-sdk-for-python/eng/tox/tox.ini
    IF errors/warnings found:
        FIX issues following official guidelines
        RERUN same step until it passes
    ONLY proceed to next step when current step passes
```

**Validation Commands (Sequential Order):**
```bash
# Step 3a: Code Formatting  
tox -e black -c [path to tox.ini] --root .

# Step 3b: Linting
tox -e pylint -c [path to tox.ini] --root .

# Step 3c: Type Checking - MyPy
tox -e mypy -c [path to tox.ini] --root .

# Step 3d: Type Checking - Pyright
tox -e pyright -c [path to tox.ini] --root .

# Step 3e: Type Verification
tox -e verifytypes -c [path to tox.ini] --root .

# Step 3f: Documentation Build
tox -e sphinx -c [path to tox.ini] --root .

# Step 3g: Minimum Dependencies
tox -e mindependency -c [path to tox.ini] --root .

# Step 3h: Security Scanning
tox -e bandit -c [path to tox.ini] --root .

# Step 3i: Sample Validation
tox -e samples -c [path to tox.ini] --root .

# Step 3j: Breaking Changes Check
tox -e breaking -c [path to tox.ini] --root .
```

**POST-VALIDATION REQUIREMENTS:**
- Provide summary after each validation step
- Edit ONLY files with validation errors/warnings
- Reference official Azure SDK guidelines for fixes
- Do NOT create new files or add unnecessary dependencies
- Ensure all release-blocking checks pass: MyPy, Pylint, Sphinx, Tests-CI

### STEP 4: PACKAGE ENHANCEMENT AND DOCUMENTATION

```
REFERENCE: "What to do after generating the SDK code with codegen" wiki guidelines
REQUIRED ACTIONS:
1. REVIEW and enhance generated code for better user experience
2. UPDATE README.md with service-specific information
3. CREATE/UPDATE CHANGELOG.md with version and changes
4. VERIFY package version matches API spec version in _version.py
5. VALIDATE setup.py and other package metadata
6. ENSURE samples are functional and follow Azure SDK patterns
7. SET CHANGELOG entry date to TODAY's date

POST-GENERATION ENHANCEMENTS:
- Add service-specific documentation
- Enhance code examples in docstrings  
- Verify authentication patterns follow Azure SDK guidelines
- Ensure error handling follows SDK conventions
```

### STEP 5: FINAL VALIDATION AND TESTING

```
ACTION: Run comprehensive validation before commit
TESTS TO RUN:
1. Import validation: Verify package imports correctly
2. Basic functionality tests: Run generated tests
3. Sample execution: Verify samples work as expected
4. Documentation build: Ensure docs generate without errors

COMMAND EXAMPLES:
python -c "import azure.{service_name}"
pytest tests/ --basic-validation
python samples/basic_sample.py --dry-run
```

### STEP 6: COMMIT AND PUSH CHANGES

```
ACTION: Prepare for commit following SDK repo conventions
COMMIT PROCESS:
1. SHOW changed files (ignore .github, .vscode, .tox, __pycache__)
2. VERIFY all generated files are included
3. REVIEW commit message follows conventional format
4. CONFIRM user approval before committing

IF user confirms:
    git add <changed_files>
    git commit -m "<service_name>: <action> <description>"
    git push -u origin <branch_name>
IF authentication fails:
    PROMPT: gh auth login
IF user rejects:
    GUIDE to fix issues and revalidate
```

### STEP 7: PULL REQUEST CREATION AND HANDOFF

```
PR MANAGEMENT:
CHECK: Does PR exist for current branch?
IF PR exists:
    UPDATE PR with latest changes
    SHOW PR details and status
IF NO PR exists:
    VERIFY branch != "main"
    GENERATE descriptive PR title: "[{service_name}] Initial SDK generation"
    CREATE comprehensive PR description including:
      - Service overview
      - Generated features
      - Validation status
      - Breaking changes (if any)
    CREATE PR in DRAFT mode for review
    RETURN PR link

FINAL HANDOFF:
1. PROVIDE PR URL for review
2. REFERENCE post-generation wiki: "What to do after generating the SDK code with codegen"
3. PROMPT user with exact text:
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
