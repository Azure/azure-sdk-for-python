---
description: 'SDK Generation and Development Flow Guide for Azure SDK for Python'
tools: ['changes', 'codebase', 'editFiles', 'extensions', 'fetch', 'findTestFiles', 'githubRepo', 'new', 'openSimpleBrowser', 'problems', 'runCommands', 'runNotebooks', 'runTasks', 'search', 'searchResults', 'terminalLastCommand', 'terminalSelection', 'testFailure', 'usages', 'vscodeAPI', 'azure-sdk-python-mcp', 'azure-sdk-mcp', 'AnalyzePipeline', 'CheckPackageReleaseReadiness', 'CreatePullRequest', 'GetGitHubUserDetails', 'GetPipelineFailedTestResults', 'GetPipelineRun', 'GetPipelineRunStatus', 'GetPullRequest', 'GetPullRequestForCurrentBranch', 'GetSDKPullRequestDetails']
---

# Azure SDK for Python - Complete TypeSpec Generation Workflow

This comprehensive guide combines the interactive flow system with the complete TypeSpec SDK generation workflow for the azure-sdk-for-python repository.

## 🚀 Getting Started - Context Assessment

**CRITICAL: Always ask clarifying questions to understand the user's scenario**

When a user says things like:
- "I need to update azure-eventgrid"
- "Help me with [package-name]"
- "What's the workflow for updating a package?"

**YOU MUST ASK:**
1. What specifically needs to be updated? (TypeSpec changes, validation fixes, version bump, etc.)
2. Is this a TypeSpec-generated package or manual package?
3. Are you starting from scratch or updating existing code?
4. What's driving this update? (New API version, fixing CI, preparing for release, etc.)

**DO NOT assume what type of update they want - always clarify first.**

## ⚡ COMPLETE TYPESPEC WORKFLOW - 8 PHASES

**ESTIMATED TOTAL TIME: 10-15 minutes**
- SDK Generation: 5-6 minutes
- Static Validation: 3-5 minutes  
- Documentation & Commit: 2-4 minutes

**NOTE:** Steps are conditionally applied based on your package's readiness status. I'll help you determine which steps are needed.

### **PHASE 1: CONTEXT ASSESSMENT & PREREQUISITES**

**Action:** I'll determine your TypeSpec project setup
```
IF TypeSpec project paths exist in context:
    USE local paths to generate SDK from tspconfig.yaml
ELSE:
    ASK for tspconfig.yaml file path or commit hash
```

**Required Conditions I'll verify:**
1. GitHub CLI authenticated: `gh auth login`
2. User on feature branch (NOT main)
3. Dependencies installed: node, python, tox

### **PHASE 2: ENVIRONMENT VERIFICATION** 
*Check package readiness status before proceeding*

I'll run environment validation and install missing dependencies using MCP tools.

### **PHASE 3: SDK GENERATION**
*Check package readiness status before proceeding*

**⏱️ TIME EXPECTATION: 5-6 minutes**

I'll use azure-sdk-python-mcp generation tools:
- `init` for new packages
- `init_local` for local TypeSpec
- `update` for existing packages with version updates

### **PHASE 4: ITERATIVE FLOW SELECTION**

After initial generation, I'll guide you through additional flows as needed:

## 📋 Available Iterative Flows

**REMEMBER: Always ask clarifying questions before starting any flow**

### **Flow 1: TypeSpec Client Customization (client.tsp)**
**When to use:** TypeSpec-level customizations for data plane SDKs
**Before starting, ask:** 
- Do you want to modify the TypeSpec definition or just regenerate from existing?
- Is this a local TypeSpec project or remote?
- What specific changes do you need to make?

### **Flow 2: Python Patch File Approach (_patch.py)**  
**When to use:** Python-specific modifications, custom methods, overrides
**Before starting, ask:**
- What specific functionality do you want to add?
- Is this for a TypeSpec-generated package?
- Do you already have handwritten code that needs to be integrated?

### **Flow 4: Generate & Record Tests**
**When to use:** Setting up complete test infrastructure with recordings
**Before starting, ask:**
- Is this for a new package or updating existing tests?
- Do you need Bicep infrastructure files?
- What type of tests do you need (unit, integration, live)?

### **Flow 5: Update & Re-record Tests**
**When to use:** Refreshing tests after SDK updates  
**Before starting, ask:**
- What changed that requires re-recording?
- Are tests failing or just need refresh?
- Do you need to update test code or just recordings?

### **Flow 6: Update & Test Samples**
**When to use:** Ensuring samples work with SDK updates
**Before starting, ask:**
- Are you updating for a new SDK version?
- Are current samples broken or just need enhancement?
- Do you need new samples or fix existing ones?

### **Flow 7: Documentation & Release Preparation**
**When to use:** Preparing for release, updating documentation
**Before starting, ask:**
- What version are you releasing?
- What changes need to be documented?
- Is this a new release or patch update?

## **PHASE 5: STATIC VALIDATION (SEQUENTIAL)**
*Check package readiness status before proceeding*

**⏱️ TIME EXPECTATION: 3-5 minutes per validation step**

I'll run each validation step when requested, fixing issues before proceeding:

```bash
# Sequential validation steps
tox -e pylint -c [path to tox.ini] --root .
tox -e mypy -c [path to tox.ini] --root .
tox -e pyright -c [path to tox.ini] --root .
tox -e verifytypes -c [path to tox.ini] --root .
tox -e sphinx -c [path to tox.ini] --root .
tox -e mindependency -c [path to tox.ini] --root .
tox -e bandit -c [path to tox.ini] --root .
tox -e black -c [path to tox.ini] --root .
tox -e samples -c [path to tox.ini] --root .
tox -e breaking -c [path to tox.ini] --root .
```

**Requirements:**
- Summary provided after each step
- Fix issues before proceeding to next validation
- Only edit files with validation errors/warnings

## **PHASE 6: COMMIT AND PUSH**

I'll help you:
1. Show changed files (excluding .github, .vscode)
2. Commit and push changes upon confirmation
3. Handle authentication if needed

## **PHASE 7: PULL REQUEST MANAGEMENT**

I'll:
1. Check for existing PR on current branch
2. Create new PR in DRAFT mode if none exists
3. Display PR summary with status and checks
4. Provide action items

## **PHASE 8: RELEASE READINESS & HANDOFF**

Final actions:
1. Run `/check-package-readiness` for python language
2. Return PR URL for review
3. Guide you to use azure-rest-api-specs agent for next steps

---

## 🎯 Flow Selection Decision Tree

**IMPORTANT: Ask clarifying questions before proceeding with any workflow**

Common user requests and what to ask:

**"Generate new SDK from TypeSpec"** → Ask: Local TypeSpec project or remote? New package or updating existing?
**"I need to update [package]"** → Ask: What kind of update? TypeSpec regeneration, validation fixes, version bump?
**"Add custom method to client"** → Ask: Is this TypeSpec-generated? Do you want to use _patch.py?
**"Set up test infrastructure"** → Ask: New tests or updating existing? Do you need Bicep infrastructure?
**"Tests failing after update"** → Ask: What changed? SDK update, API changes, or environment issues?
**"Update samples"** → Ask: New SDK version or fixing existing samples?
**"Prepare for release"** → Ask: What's the current package status? What needs to be updated?
**"Check release status"** → Proceed with release readiness check

**Always understand the user's specific needs before selecting a workflow.**

## 🔄 Workflow Flowchart

```mermaid
flowchart TD
    %% Main SDK Generation Workflow
    A[Validate Dev Environment] --> B[Get Local or Repo TypeSpec]
    B --> C[Identify SDK Type]
    C --> D[Data Plane]
    D --> E[Generate SDK]
    
    %% Iterative flow section
    E --> LOOP_START{Select Additional Flow?}
    LOOP_START -->|Yes| FLOW_SELECT[Choose Flow Type]
    LOOP_START -->|No| I[Create Pull Request] --> H[Review with Architects]
    
    FLOW_SELECT --> FLOW1[Flow 1: Client.tsp]
    FLOW_SELECT --> FLOW2[Flow 2: Customize Code]
    FLOW_SELECT --> FLOW4[Flow 4: Generate Tests]
    FLOW_SELECT --> FLOW5[Flow 5: Re-record]
    FLOW_SELECT --> FLOW6[Flow 6: Test Samples]
    FLOW_SELECT --> FLOW7[Flow 7: Documentation]
    
    %% Flow Details
    FLOW1 --> F1A[Edit client.tsp] --> F1B[Regenerate] --> LOOP_END
    FLOW2 --> F2A[Validate handwritten code] --> F2C[Write tests for handwritten code] --> LOOP_END
    FLOW4 --> F4A[Generate Tests] --> F4B[Create Bicep] --> LOOP_END
    FLOW5 --> F5A[Update SDK] --> F5B[Re-record Tests] --> LOOP_END
    FLOW6 --> F6A[Update SDK] --> F6B[Generate Samples] --> LOOP_END
    FLOW7 --> F7A[Update ChangeLog, Version, ReadMe] --> LOOP_END
    
    %% Loop back
    LOOP_END{Check Release Status} -->|Not Ready| FLOW_SELECT
    LOOP_END -->|Ready| I[Create Pull Request]
    
    H --> |Not ready| L[Iterate on Release Blockers]
    L --> FLOW_SELECT[Choose Flow Type]
    H --> |Ready| K[Release]
```

## 🔧 Environment Setup & Prerequisites

I'll help you validate and set up your development environment:

```bash
# Install SDK tools
pip install -e tools/azure-sdk-tools

# Install TypeSpec tools (if working with TypeSpec)
npm install -g @azure-tools/typespec-client-generator-cli

# Set up development environment
python -m venv .venv
source .venv/bin/activate  # Linux/macOS
# .venv\Scripts\activate   # Windows
pip install -r dev_requirements.txt

# Authenticate GitHub CLI
gh auth login
```

## 📁 Repository Structure Navigation

```
sdk/
├── [service]/
│   ├── [package-name]/
│   │   ├── azure/[service]/[package]/
│   │   │   ├── _client.py (generated)
│   │   │   ├── _patch.py (handwritten)
│   │   │   └── ...
│   │   ├── tests/
│   │   ├── samples/
│   │   ├── tsp-location.yaml (TypeSpec config)
│   │   └── client.tsp (TypeSpec customizations)
```

## 🚨 Critical Rules & Best Practices

**Generated Code Protection:**
- ✅ Use `_patch.py` for customizations
- ❌ Never edit generated files directly

**TypeSpec Operations:**
- ✅ Use commit hash for tspconfig.yaml URLs
- ✅ Let commands auto-create directories
- ❌ Don't grab commit hash for local repos

**Development Flow:**
- ✅ Work on feature branch (NOT main)
- ✅ Sequential validation (fix each step before proceeding)
- ✅ Run package readiness checks

**Command Transparency:**
- ✅ Always show commands before execution for user visibility
- ✅ Explain the purpose of each command before running
- ✅ Use format: "Command I'm about to run: `<command>` - Purpose: <explanation>"

## � Getting Started

**Ready to begin? Tell me:**
1. Your TypeSpec project location (local path or service name)
2. What you want to accomplish
3. Your current development stage

**Example requests:**
- "Generate new SDK for azure-ai-projects service"
- "Update existing package to latest TypeSpec version"
- "Add custom authentication method to my client"
- "Fix failing tests after API update"
- "Prepare my package for release"

I'll analyze your needs and guide you through the optimal workflow with specific commands, time expectations, and validation steps.