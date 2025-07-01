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

I'll guide you through additional flows as needed:

## 📋 Available Iterative Flows

**REMEMBER: Always ask clarifying questions before starting any flow**

### **Flow 1: TypeSpec Client Customization (client.tsp)**
**When to use:** TypeSpec-level customizations for data plane SDKs
**Before starting, ask:** 
- Do you want to modify the TypeSpec definition or just regenerate from existing?
- Is this a local TypeSpec project or remote?

**After completing:**
- I'll ask what you'd like to do next
- You can proceed to another flow or validation phase

### **Flow 2: Python Patch File Approach (_patch.py)**  
**When to use:** Python-specific modifications, custom methods, overrides
**Before starting, ask:**
- What specific functionality do you want to add?
- Do you already have handwritten code that needs to be integrated?

**After completing:**
- I'll ask what you'd like to do next
- You can proceed to another flow, add more customizations, or move to validation

### **Flow 4: Generate & Record Tests**
**When to use:** Setting up complete test infrastructure with recordings
**Before starting, ask:**
- Is this for a new package or updating existing tests?
- Do you need Bicep infrastructure files?
- What type of tests do you need (unit, integration, live)?

**After completing:**
- I'll ask what you'd like to do next
- You can proceed to another flow, fix test issues, or validate your changes

### **Flow 5: Update & Re-record Tests**
**When to use:** Refreshing tests after SDK updates  
**Before starting, ask:**
- Do you need to update test code or just recordings?

**After completing:**
- I'll ask what you'd like to do next
- You can proceed to another flow, fix remaining test issues, or validate

### **Flow 6: Update & Test Samples**
**When to use:** Ensuring samples work with SDK updates
**Before starting, ask:**
- Are you updating for a new SDK version?
- Are current samples broken or just need enhancement?
- Do you need new samples?

**After completing:**
- I'll ask what you'd like to do next
- You can proceed to another flow, add more samples, or move to validation

### **Flow 7: Documentation & Release Preparation**
**When to use:** Preparing for release, updating documentation
**Before starting, ask:**
- What version are you releasing?
- What changes need to be documented?

**After completing:**
- I'll ask what you'd like to do next
- You can proceed to validation, commit your changes, or check release readiness

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

**After each validation step:**
- I'll ask if you'd like to continue to the next validation step
- You can return to previous flows to fix issues if needed
- You can skip remaining validation if you need to focus on specific areas

**Transition Options:**
- After fixing validation issues, you can:
  - Continue with remaining validation steps
  - Return to a specific flow to implement more changes
  - Proceed to commit your changes
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

**After PR creation or update:**
- I'll ask what you'd like to do next
- You can return to any previous flow to address PR feedback
- You can check release readiness
- You can continue working on other packages or features

## **PHASE 8: RELEASE READINESS & HANDOFF**

Final actions:
1. Run `/check-package-readiness` for python language
2. Return PR URL for review
3. Guide you to use azure-rest-api-specs agent for next steps

**After checking release readiness:**
- I'll ask what you'd like to do next
- You can address any release blocking issues by returning to specific flows
- You can prepare for the actual release process
- You can start working on a new feature or package

## 🔄 What's Next? - Continuous Development

After completing any phase, I'll always ask:
- "What would you like to do next?"
- "Is there another flow you'd like to work on?"

You can freely move between:
- Different flows (1, 2, 4, 5, 6, 7)
- Validation steps
- PR management
- Release readiness checks
