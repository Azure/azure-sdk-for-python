# AGENTS.md - Azure SDK for Python

This file describes how AI agents (e.g., GitHub Copilot, MCP servers, or LLM-based assistants) should interact with this repository.

## Repository Overview

**Purpose**: This repository contains the active development of the Azure SDK for Python, providing client libraries and management libraries for Azure services.

**Scope**: 
- 100+ Python packages for Azure services
- Client libraries for data plane operations
- Management libraries for Azure Resource Manager (ARM)
- Shared core functionality (authentication, retries, logging, transport)
- TypeSpec-based SDK generation from API specifications
- Comprehensive testing, validation, and documentation infrastructure

**Main Branch**: `main`

**Key Documentation**:
- [Azure SDK Python Design Guidelines](https://azure.github.io/azure-sdk/python_design.html)
- [Contributing Guide](https://github.com/Azure/azure-sdk-for-python/blob/main/CONTRIBUTING.md)
- [Developer Documentation](https://github.com/Azure/azure-sdk-for-python/tree/main/doc/dev)

## Repository Structure

```
azure-sdk-for-python/
├── sdk/                    # Service-specific libraries (e.g., sdk/storage/, sdk/ai/)
├── eng/                    # Engineering system tools and configurations
├── doc/                    # Developer documentation and guides
├── scripts/                # Automation scripts
├── .github/                # GitHub workflows and Copilot instructions
│   └── copilot-instructions.md  # Detailed Copilot-specific guidance
└── tools/                  # Development tools
```

## AI Agent Guidelines

### Supported Actions

AI agents can assist with the following activities:

#### Code Generation & Development
- **TypeSpec SDK Generation**: Generate Python SDKs from TypeSpec specifications
  - Follow the complete workflow in `.github/copilot-instructions.md`
  - Use MCP tools for environment verification, code generation, and validation
  - Time estimate: 10-15 minutes for full generation workflow
  
- **Code Fixes**: Address linting, type checking, and validation issues
  - Pylint, MyPy, Pyright, Verifytypes, Sphinx warnings
  - Follow official guidelines and existing patterns
  - Make minimal, surgical changes

- **Documentation**: Update CHANGELOG.md, README files, and API documentation
  - Follow existing formatting conventions
  - Include version information and release dates

#### Testing & Validation
- **Run Tests**: Execute tox-based test suites
  - Unit tests, integration tests, samples
  - Support both local and CI environments
  
- **Static Analysis**: Run and fix issues from:
  - Pylint (code quality)
  - MyPy, Pyright (type checking)
  - Bandit (security)
  - Black (formatting)
  - Sphinx (documentation)

#### Pull Request Management
- **PR Creation**: Create draft PRs with descriptive titles and descriptions
- **PR Review**: Analyze PR feedback and make requested changes
- **Status Checks**: Monitor CI/CD pipeline status and address failures

#### Issue Triage & Labeling
- **Issue Analysis**: Review and categorize issues
- **Service Labels**: Validate and create service labels (e.g., `Azure.AI.Projects`)
- **CODEOWNERS**: Validate and update CODEOWNERS entries

### Key Workflows

#### 1. TypeSpec SDK Generation Workflow

**Prerequisites**:
- GitHub CLI authenticated (`gh auth login`)
- Feature branch (not `main`)
- PowerShell installed (for MCP tools)
- Python virtual environment active

**Steps**:
1. **Environment Verification** - Use `verify_setup` MCP tool
2. **SDK Generation** - Use azure-sdk-python-mcp generation tools (~2 minutes)
3. **Static Validation** - Run sequential validation steps (~3-5 minutes each):
   - Pylint, MyPy, Pyright, Verifytypes
   - Sphinx, Mindependency, Bandit, Black
   - Samples, Breaking changes
4. **Documentation Update** - Update CHANGELOG.md and version files
5. **Commit & Push** - Stage, commit, and push changes
6. **PR Creation** - Create draft PR with generated description
7. **Handoff** - Provide PR link for azure-rest-api-specs agent

**Estimated Time**: 10-15 minutes

#### 2. Code Quality Workflow

**Running Validation**:
```bash
# Use tox with appropriate environment
tox -e <environment> -c eng/tox/tox.ini --root .

# Examples:
tox -e pylint -c eng/tox/tox.ini --root .
tox -e mypy -c eng/tox/tox.ini --root .
```

**Fixing Issues**:
- Reference official guidelines:
  - [Pylint Guidelines](https://github.com/Azure/azure-sdk-tools/blob/main/tools/pylint-extensions/azure-pylint-guidelines-checker/README.md)
  - [MyPy Type Checking Guide](https://github.com/Azure/azure-sdk-for-python/blob/main/doc/dev/static_type_checking_cheat_sheet.md)
  - [Tox Usage Guide](https://github.com/Azure/azure-sdk-for-python/blob/main/doc/dev/tests.md#tox)
- Make minimal changes that address specific warnings
- Avoid adding new dependencies or large refactoring
- Rerun validation after each fix

#### 3. SDK Release Workflow

**Check Release Readiness**:
- Use `CheckPackageReleaseReadiness` MCP tool
- Validates: API review status, changelog, package approval, release date

**Release Package**:
- Use `ReleasePackage` MCP tool
- Triggers release pipeline (requires approval)

**Release Blocking Checks**:
- MyPy: PASS
- Pylint: PASS
- Sphinx: PASS
- Tests - CI: PASS

### Automation Boundaries

#### Safe Operations
✅ Generate SDK code from TypeSpec specifications  
✅ Run linting and static analysis tools  
✅ Fix code quality warnings (with high confidence)  
✅ Update documentation (CHANGELOG, README)  
✅ Create and update PRs in draft mode  
✅ Run existing test suites  
✅ Validate CODEOWNERS entries  

#### Restricted Operations
⚠️ Modifying generated code (requires review)  
⚠️ Adding new dependencies (requires justification)  
⚠️ Changing API signatures (requires design review)  
⚠️ Disabling or removing tests (requires explanation)  
⚠️ Large-scale refactoring (requires approval)  

#### Prohibited Operations
❌ Merging PRs without human review  
❌ Releasing packages to PyPI  
❌ Modifying CI/CD pipeline definitions  
❌ Changing security or authentication logic without security review  
❌ Committing secrets or credentials  
❌ Force pushing to protected branches  

### Environment Requirements

**Required Tools**:
- Python 3.9 or later
- Node.js (for TypeSpec generation)
- Tox (test automation)
- GitHub CLI (for PR operations)
- PowerShell (for MCP server on Windows)

**MCP Server Tools**:
- `azure-sdk-python-mcp` - Python-specific SDK operations
- `azure-sdk-mcp` - Cross-language SDK operations
- `azsdk-tools` - Engineering system utilities

**Virtual Environment**:
```bash
# Create and activate virtual environment
python -m venv .venv
source .venv/bin/activate  # Linux/macOS
.venv\Scripts\activate      # Windows
```

### CI/CD Integration

**Pipeline System**: Azure DevOps

**Key Pipelines**:
- **Python CI**: Core library tests and validation
- **SDK Generation**: TypeSpec-based code generation
- **Release**: Package publication to PyPI

**Status Monitoring**:
- Use `get_pipeline_status` MCP tool
- Check build logs for failures
- Analyze failed tests with `get_failed_test_cases` tool

**Artifact Analysis**:
- Download artifacts with `get_pipeline_llm_artifacts`
- Review TRX test results
- Analyze log files with `analyze_log_file` tool

### SDK-Specific Conventions

#### Package Naming
- Client libraries: `azure-<service>-<component>` (e.g., `azure-storage-blob`)
- Management libraries: `azure-mgmt-<service>` (e.g., `azure-mgmt-compute`)

#### Version Conventions
- Semantic versioning: `MAJOR.MINOR.PATCH`
- Preview versions: `MAJOR.MINOR.PATCHbN` (e.g., `1.0.0b1`)
- Pre-release format in CHANGELOG: `## 1.0.0b1 (YYYY-MM-DD)`

#### Code Style
- Follow [PEP 8](https://peps.python.org/pep-0008/)
- Use Black for formatting
- Type hints required (PEP 484)
- Docstrings in NumPy/Google style

#### Testing
- Use pytest framework
- Separate live and recorded tests
- Test recordings in `tests/recordings/`
- Environment variables for credentials (never hardcode)

## Cross-References

**Detailed Copilot Instructions**: See [`.github/copilot-instructions.md`](https://github.com/Azure/azure-sdk-for-python/blob/main/.github/copilot-instructions.md) for:
- Complete TypeSpec SDK generation workflow
- Detailed validation steps and commands
- Pylint and MyPy fixing guidelines
- SDK health status interpretation
- SDK release procedures

**Developer Documentation**: See [`doc/dev/`](https://github.com/Azure/azure-sdk-for-python/tree/main/doc/dev) for:
- [TypeSpec Generation Guide](https://github.com/Azure/azure-sdk-for-python/blob/main/doc/dev/ai/typespec_generation.md)
- [Testing Guide](https://github.com/Azure/azure-sdk-for-python/blob/main/doc/dev/tests.md)
- [Tox Usage](https://github.com/Azure/azure-sdk-for-python/blob/main/doc/dev/tests.md#tox)
- [Pylint Checking](https://github.com/Azure/azure-sdk-for-python/blob/main/doc/dev/pylint_checking.md)
- [Type Checking Cheat Sheet](https://github.com/Azure/azure-sdk-for-python/blob/main/doc/dev/static_type_checking_cheat_sheet.md)

## Example Prompts

### SDK Generation
```
"Generate a Python SDK using TypeSpec from tspconfig.yaml at <path>"
"Start TypeSpec SDK generation workflow"
"Generate SDK from my local TypeSpec project at sdk/cognitiveservices/azure-ai-projects"
```

### Validation & Fixes
```
"Run pylint validation and fix any warnings"
"Check if my SDK passes all static validation steps"
"Fix the mypy errors in the generated SDK"
```

### Release Management
```
"Check if azure-ai-projects is ready for release"
"What is the health status of azure-storage-blob?"
"Release azure-ai-inference version 1.0.0"
```

### Repository Health
```
"Show me the health status for azure-ai-projects"
"Which checks are blocking the release of this library?"
"Are there any open customer issues for this package?"
```

## Agent Behavior Guidelines

### Best Practices
1. **Always verify environment first** - Run `verify_setup` before SDK operations
2. **Inform users of time expectations** - SDK generation takes 10-15 minutes
3. **Make minimal changes** - Only modify files with validation errors
4. **Reference official documentation** - Link to Azure SDK design guidelines
5. **Run validation iteratively** - Fix and rerun each step before proceeding
6. **Use MCP tools when available** - Leverage specialized SDK tooling
7. **Create draft PRs** - Never create PRs in ready-for-review state
8. **Report progress frequently** - Use incremental commits

### Error Handling
- For TypeSpec errors: Direct users to fix in source repository
- For authentication failures: Guide through `gh auth login`
- For missing dependencies: Provide installation instructions with links
- For validation failures: Reference specific fixing guidelines
- For pipeline failures: Analyze logs and provide actionable feedback

### Communication Style
- Don't repeat instructions - reference documentation links
- Be concise and actionable
- Use markdown formatting for commands and code
- Provide time estimates for long operations
- Highlight release-blocking issues clearly

## Reporting Issues

To report issues with AI agent interactions or suggest improvements:
- **GitHub Issues**: [Azure SDK for Python Issues](https://github.com/Azure/azure-sdk-for-python/issues)
- **Label**: Use `Agent` label for agent-related issues
- **Include**: Agent name/version, prompt used, expected vs actual behavior

## Version

**AGENTS.md Version**: 1.0.0  
**Last Updated**: 2025-01-22  
**Specification**: Follows [agents.md](https://agents.md) canonical structure
