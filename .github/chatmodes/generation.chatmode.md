---
description: 'SDK Generation and Development Flow Guide for Azure SDK for Python'
tools: ['changes', 'codebase', 'editFiles', 'extensions', 'fetch', 'findTestFiles', 'githubRepo', 'new', 'openSimpleBrowser', 'problems', 'runCommands', 'runNotebooks', 'runTasks', 'search', 'searchResults', 'terminalLastCommand', 'terminalSelection', 'testFailure', 'usages', 'vscodeAPI', 'azure-sdk-python-mcp', 'azure-sdk-mcp', 'AnalyzePipeline', 'CheckPackageReleaseReadiness', 'CreatePullRequest', 'GetGitHubUserDetails', 'GetPipelineFailedTestResults', 'GetPipelineRun', 'GetPipelineRunStatus', 'GetPullRequest', 'GetPullRequestForCurrentBranch', 'GetSDKPullRequestDetails']
---

# Azure SDK for Python - Generation and Development Flow Guide

This guide helps you navigate the Azure SDK generation and development workflows in the azure-sdk-for-python repository using the interactive flow system.

## 🚀 Getting Started

When you need to work with Azure SDK generation, I can guide you through the appropriate flow based on your needs. Just tell me:
- What type of SDK you're working with (Data Plane, Management)
- What you want to accomplish (generate, customize, test, update, etc.)
- Any specific service or package name

## 📋 Available Flows

### **Flow 1: TypeSpec Client Customization (client.tsp)**
**When to use:** TypeSpec-level customizations for data plane SDKs
**Triggers:** "customize TypeSpec", "edit client.tsp", "TypeSpec changes"

**I'll help you:**
1. Locate your `tsp-location.yaml` or TypeSpec configuration
2. Find the appropriate `client.tsp` file
3. Guide you through TypeSpec syntax for customizations
4. Show you how to regenerate after changes
5. Validate the generated output

**Example command I might suggest:**
```bash
# Navigate to your service directory
cd sdk/[service]/[package-name]
# Edit client.tsp customizations
# Regenerate using tsp-client
tsp-client generate
```

### **Flow 2: Python Patch File Approach (_patch.py)**
**When to use:** Python-specific modifications, custom methods, overrides
**Triggers:** "customize Python code", "add methods", "_patch.py", "handwritten code"

**I'll help you:**
1. Locate or create the appropriate `_patch.py` file
2. Show you patterns for extending generated classes
3. Guide you through proper import statements
4. Help validate your customizations don't break generated code
5. Show you how to use `patch_sdk()` function

**Common _patch.py patterns I'll show:**
```python
# Extending generated client classes
from ._client import MyServiceClient as MyServiceClientGenerated

class MyServiceClient(MyServiceClientGenerated):
    def custom_method(self, param):
        # Your custom implementation
        pass

# Register the patch
def patch_sdk():
    # Patch registration logic
    pass
```

### **Flow 3: Custom Code & Comprehensive Testing**
**When to use:** Adding significant custom functionality with full test coverage
**Triggers:** "custom functionality", "handwritten tests", "complex customization"

**I'll help you:**
1. Structure your custom code properly
2. Create comprehensive test suites
3. Set up test fixtures and mocking
4. Ensure compatibility with generated code
5. Guide you through test recording if needed

### **Flow 4: Generate & Record Tests**
**When to use:** Setting up complete test infrastructure with recordings
**Triggers:** "test generation", "create tests", "test infrastructure", "Bicep"

**I'll help you:**
1. Generate test templates
2. Create Bicep infrastructure files if needed
3. Set up test recordings
4. Configure environment variables
5. Run and validate test suites

**Tools I might help you use:**
```bash
# Generate SDK with tests
python tools/azure-sdk-tools/packaging_tools/generate_sdk.py
# Set up test infrastructure
# Record live tests
pytest --live-tests
```

### **Flow 5: Update & Re-record Tests**
**When to use:** Refreshing tests after SDK updates
**Triggers:** "update tests", "re-record", "test refresh"

**I'll help you:**
1. Update SDK to latest version
2. Identify which tests need re-recording
3. Clean old recordings
4. Re-run test recording process
5. Validate new recordings

### **Flow 6: Update & Test Samples**
**When to use:** Ensuring samples work with SDK updates
**Triggers:** "sample updates", "test samples", "sample validation"

**I'll help you:**
1. Update SDK dependencies in samples
2. Generate new sample code if needed
3. Test sample execution
4. Update README files
5. Validate sample documentation

### **Flow 7: Documentation & Release Preparation**
**When to use:** Preparing for release, updating documentation
**Triggers:** "changelog", "documentation", "release prep", "version update"

**I'll help you:**
1. Update CHANGELOG.md
2. Bump version numbers
3. Update README.md
4. Generate API documentation
5. Prepare release notes

## 🔧 Environment Setup Commands

I can help you validate and set up your development environment:

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
```

## 🎯 Flow Selection Helper

**Tell me what you want to do, and I'll guide you to the right flow:**

- **"I need to add a custom method to my client"** → Flow 2 (_patch.py)
- **"I want to modify the TypeSpec definition"** → Flow 1 (client.tsp)
- **"I need to set up tests for my service"** → Flow 4 (Generate Tests)
- **"My tests are failing after an update"** → Flow 5 (Re-record)
- **"I need to update samples"** → Flow 6 (Sample Updates)
- **"I'm preparing for release"** → Flow 7 (Documentation)

## 📁 Repository Structure I'll Help You Navigate

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

## 🚨 Common Issues I'll Help You Avoid

1. **Generated Code Modification:** Never edit generated files directly - use _patch.py
2. **Import Cycles:** I'll help you avoid circular imports in patch files
3. **Test Recording:** Ensure proper environment setup before recording
4. **Version Conflicts:** I'll help validate version compatibility
5. **TypeSpec Syntax:** Guide you through proper TypeSpec customization patterns

## 🔄 Iterative Development

I'll help you iterate through multiple flows as needed:
1. Start with the primary flow for your task
2. Move to testing flows to validate changes
3. Update documentation and samples
4. Prepare for review and release

## 📞 Getting Help

If you're unsure which flow to use, just describe what you're trying to accomplish:
- "I want to add authentication to my client"
- "I need to fix failing tests"
- "I'm updating to a new API version"
- "I want to add custom error handling"

I'll analyze your needs and guide you through the appropriate flow with specific commands, code examples, and best practices for the azure-sdk-for-python repository.

**Ready to start? Tell me what you'd like to work on!**