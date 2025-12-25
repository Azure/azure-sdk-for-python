---
description: 'SDK Review Instructions for Python Packages'
applyTo: 'sdk/**'
---

When reviewing Python SDK packages under `sdk/` directory, follow this systematic process to ensure compliance with Azure SDK guidelines.

## Scope
Apply to all packages under `sdk/` excluding `venv/`, `__pycache__/`, `tests/`, `samples/`, and `*_test.py` files.

## Review Process

### Phase 1: Inventory & Discovery
Use `file_search` and `grep_search` to:
- Find all `*.py` files in the target package
- Locate key files: `_client.py`, `_patch.py`, `_models.py`, `_operations.py`, `_enums.py`, `_exceptions.py`
- Locate documentation: `README.md`, `CHANGELOG.md`
- Locate configuration: `setup.py`, `pyproject.toml`, `ci.yml`, `tsp-location.yaml`
- Map API surface by identifying all public classes and methods

### Phase 2: API Design Review
**REQUIRED: Review ALL key files using the MCP tool**

1. **Client Files** (MUST review with MCP tool):
   - `*_client.py` - Main client class with all public methods
   - `_patch.py` - Customized/patched methods (often contains hand-written code)

2. **Operations Files** (MUST review with MCP tool):
   - `*_operations.py` - Operation class methods
   - Review operation methods for guideline compliance

3. **Model Files** (SHOULD review with MCP tool):
   - `*_models.py` or `models/_models.py` - Model class definitions
   - Review model structure, required fields, type annotations

4. **Other Files** (MAY review with MCP tool):
   - `*_enums.py` - Enumeration definitions
   - `*_exceptions.py` - Custom exception classes

**Review mcp_azure-sdk-cod_review_sdk_code Results:**
- When the tool reports issues, VERIFY if the issue actually exists in the code
- Use `read_file` or `grep_search` to check if the flagged code/pattern is truly present
- If the issue is a FALSE POSITIVE (code is correct but tool misidentified it), do NOT include it in the report
- If the issue is REAL and present in the code, include it with severity assessment:
  - 🚫 Blocker: Violates required SDK guidelines or Meeting Recording design patterns, must fix before release
  - ⚠️ Warning: Violates recommended guidelines or best practices, should fix
  - ℹ️ Informational: Suggestions for improvement, optional
- For generated code, note that some violations may be acceptable if from code generator

### Phase 3: Documentation Review
Use `read_file` and `mcp_azure-sdk-cod_review_sdk_code` tool to validate `README.md` and `CHANGELOG.md` against documentation standards.

**CHANGELOG.md Review:**
- Only review the **latest changelog entry** (the most recent version section)

**Review mcp_azure-sdk-cod_review_sdk_code Results:**
- Verify that flagged documentation issues actually exist
- Check if required sections are truly missing or if tool missed them
- Only report confirmed documentation gaps or issues

### Phase 4: Configuration Review
Use `read_file` to check `setup.py`, `pyproject.toml`, `ci.yml`, and `tsp-location.yaml` against configuration requirements.

### Phase 5: Release Readiness
Verify final checklist items and produce assessment: READY / NOT READY / CONDITIONAL

## Tools
- `file_search` - Discover files by pattern
- `grep_search` - Find patterns across multiple files
- `read_file` - Read specific files or sections (use `limit`/`offset` for large files)
- `mcp_azure-sdk-cod_review_sdk_code` - Validate code snippets against SDK guidelines including Meeting Recording design patterns (results must be verified before reporting)

## Important: Validating Code Review Results
The `mcp_azure-sdk-cod_review_sdk_code` tool validates code against both official Azure SDK Python guidelines and Meeting Recording design patterns. The tool may occasionally produce false positives. Always:
1. **Verify the issue exists**: Use `read_file` or `grep_search` to confirm the flagged code pattern is actually present
2. **Understand the context**: Some patterns may be acceptable in generated code or specific scenarios
3. **Filter false positives**: Only include issues that you can confirm exist in the actual code
4. **Check for fixes**: If the tool reports something is missing (e.g., a required parameter), verify it's not present elsewhere in the file
5. **Distinguish guideline sources**: 
   - Official Azure SDK Python guidelines violations should be marked as standard blockers/warnings
   - Meeting Recording design pattern violations should be highlighted as they represent recent architectural decisions

## Output Format
Provide structured findings with:
- ✅ Compliant areas
- ⚠️ Warnings (non-blocking issues)
- 🚫 Blockers (must fix before release)
- ℹ️ Informational notes
- 📋 Release readiness assessment
- 🎯 Prioritized next steps

## Reference Documentation

### Internal References
- `doc/dev/README.md` - Development overview
- `doc/dev/pylint_checking.md` - Pylint guidelines
- `doc/dev/static_type_checking_cheat_sheet.md` - MyPy guidelines
- `doc/dev/tests.md` - Testing guidelines
- `doc/repo_health_status.md` - Repo health status
- `CONTRIBUTING.md` - Contributing guidelines
- `eng/common/instructions/copilot/sdk-release.instructions.md` - Release process

### External References
- [Azure Python SDK Guidelines](https://azure.github.io/azure-sdk/python_design.html)
- [Release Notes Policy](https://azure.github.io/azure-sdk/policies_releasenotes.html)
- [Changelog Guidance](https://azure.github.io/azure-sdk/policies_releases.html#changelog-guidance)
