# Azure SDK for Python - LLM Assistant Instructions

This document provides comprehensive instructions for an LLM assistant working with the Azure SDK for Python repository. Follow these guidelines to provide accurate, efficient assistance to developers.

## Initial Setup Requirements

### Step 1: Repository Root Detection
**CRITICAL FIRST STEP:** Always use the `get_python_repo_root` MCP tool to identify the azure-sdk-for-python repository root path. This is mandatory before executing any other operations.

- If not currently in the azure-sdk-for-python repository, prompt the user for the correct path
- All subsequent file paths and operations depend on this root directory
- Store this path for reference throughout the session

### Step 2: Environment Verification
**REQUIRED SECOND STEP:** Execute the `verify_setup` tool to confirm:
- Python virtual environment is active and properly configured
- Required development tools are installed
- Environment meets Azure SDK development requirements

### Step 3: Task Classification
Analyze the user's request and categorize it into one of these workflows:

**SDK Generation Tasks:**
- User mentions "generate SDK", "TypeSpec", "tspconfig", or "client library"
- Expected duration: 5-6 minutes
- Workflow: TypeSpec SDK Generation

**Code Quality Validation Tasks:**
- User requests "pylint", "mypy", "pyright", "verifytypes", or "static analysis"
- Expected duration: 3-5 minutes per validation type
- Workflow: Static Validation Operations

**Code Issue Resolution Tasks:**
- User has specific pylint warnings, errors, or code quality issues to fix
- Expected duration: Variable based on complexity
- Workflow: Pylint Warning Resolution

**Development Environment Tasks:**
- User needs environment setup, verification, or troubleshooting
- Expected duration: 2-3 minutes
- Workflow: Environment Setup

**Version Control Tasks:**
- User wants to commit changes, push code, or manage pull requests
- Expected duration: 2-4 minutes
- Workflow: Git and PR Operations

## Assistant Behavior Guidelines

### Principle 1: Efficient Communication
- Provide clear, actionable guidance without excessive detail repetition
- Reference specific workflow documents rather than duplicating their content
- Focus on high-level direction and let users follow detailed steps independently
- Always inform users of expected completion times before starting workflows

### Principle 2: Authoritative Documentation
**ALWAYS reference the official Azure SDK Python Design Guidelines:**
- Primary source: [Azure SDK Python Design Guidelines](https://azure.github.io/azure-sdk/python_design.html)
- Link to specific sections when answering design or guideline questions
- Use this as the definitive authority for SDK development standards
- Ensure all generated code follows these established patterns

### Principle 3: Time Transparency
**ALWAYS communicate expected completion times:**
- Inform users before starting any workflow about estimated duration
- Provide progress updates for longer operations
- Set realistic expectations to improve user experience

## Detailed Workflow Execution Instructions

### TypeSpec SDK Generation Workflow
**Trigger conditions:** User requests SDK generation from TypeSpec specifications

**Execution steps:**
1. Use `read_file` tool to load `.github/prompts/typespec-sdk-generation.prompt.md`
2. Execute each step sequentially as outlined in the loaded prompt file
3. Monitor each step for successful completion
4. If any step fails, immediately inform the user and provide specific guidance for resolution
5. Validate final output meets Azure SDK standards

**Expected completion time:** 5-6 minutes
**Key dependencies:** TypeSpec compiler, tspconfig.yaml file, network connectivity

### Static Validation Operations Workflow
**Trigger conditions:** User needs code quality validation (pylint, mypy, pyright, verifytypes)

**Execution steps:**
1. Load execution steps from `.github/prompts/static-validation.prompt.md`
2. Execute validation tools in the specified order
3. Collect and present results in a structured format
4. Highlight critical issues that require immediate attention

**Expected completion time:** 3-5 minutes per validation step
**Key dependencies:** Python environment, linting tools, source code files

### Pylint Warning Resolution Workflow
**Trigger conditions:** User has specific pylint warnings or errors to address

**Execution steps:**
1. Load resolution steps from `.github/prompts/next-pylint.prompt.md`
2. Analyze specific warnings provided by the user
3. Apply appropriate fixes following Azure SDK coding standards
4. Validate fixes don't introduce new issues

**Expected completion time:** Variable based on warning complexity and quantity
**Key dependencies:** Source code access, pylint configuration, understanding of Azure patterns

### Environment Setup Workflow
**Trigger conditions:** User needs development environment configuration or troubleshooting

**Execution steps:**
1. Load setup steps from `.github/prompts/environment-setup.prompt.md`
2. Verify current environment state
3. Execute necessary configuration changes
4. Validate environment meets all requirements

**Expected completion time:** 2-3 minutes
**Key dependencies:** System permissions, network access, Python installation

### Git and PR Operations Workflow
**Trigger conditions:** User needs version control operations (commit, push, pull request management)

**Execution steps:**
1. Load operation steps from `.github/prompts/git-operations.prompt.md`
2. Execute git commands safely with appropriate validation
3. Provide clear feedback on operation results
4. Guide user through any required manual steps

**Expected completion time:** 2-4 minutes
**Key dependencies:** Git configuration, repository permissions, network connectivity

## Azure Development Integration

### Azure Best Practices Integration
When working with Azure-specific code, commands, or operations:
- Invoke `azure_development-get_best_practices` tool when available
- Apply Azure-specific coding patterns and conventions
- Ensure compliance with Azure SDK design principles
- Use Azure-recommended libraries and approaches

### Tool Integration Requirements
- Always use absolute file paths when invoking tools that require file locations
- Handle URI schemes (like `untitled:` or `vscode-userdata:`) appropriately
- Validate tool parameters before execution
- Provide meaningful error messages when tools fail

## Error Handling and Recovery

### Common Error Scenarios
1. **Repository not found:** Guide user to correct azure-sdk-for-python path
2. **Environment issues:** Run verification and provide setup guidance
3. **Tool failures:** Diagnose issue and provide specific resolution steps
4. **Network connectivity:** Suggest offline alternatives when possible

### Recovery Procedures
- Always attempt automatic recovery before requesting user intervention
- Provide clear, actionable steps for manual resolution
- Document successful recovery methods for future reference
- Escalate complex issues with detailed context

This document serves as the comprehensive guide for LLM assistants working with the Azure SDK for Python repository. Follow these instructions to provide consistent, effective support to developers.