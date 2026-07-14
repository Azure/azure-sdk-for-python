---
name: azure-ai-projects-update-changelog
license: MIT
metadata:
  version: "1.0.0"
  distribution: local
description: "Update CHANGELOG.md by comparing public APIs between the current branch and the latest released version on PyPI. WHEN: \"update changelog\", \"generate changelog\", \"add changelog entry\", \"what changed in this version\". DO NOT USE FOR: other Azure SDK packages. INVOKES: PyPI API, GitHub API (for tags), file operations."
compatibility:
  requires: "local azure-sdk-for-python clone, git, internet access"
---

# Update azure-ai-projects Changelog

This skill guides Copilot through updating the CHANGELOG.md file for the azure-ai-projects package by comparing public APIs between the current branch and the latest released version.

**Working directory:** `sdk/ai/azure-ai-projects`

---

## Overview

The skill performs these steps:
1. Read the current version from `azure/ai/projects/_version.py`
2. Fetch the latest released version from PyPI
3. Compare public classes, methods, and properties between current branch and released version
4. Update CHANGELOG.md with a new section or update the existing "(Unreleased)" section

---

## Step 1: Read the current version

Read the current version from `azure/ai/projects/_version.py`. The file contains a line like:
```python
VERSION = "X.Y.Z"
```

Extract this version number and save it as `CURRENT_VERSION`.

---

## Step 2: Fetch the latest released version from PyPI

Use the PyPI JSON API to get the latest released version:

```
https://pypi.org/pypi/azure-ai-projects/json
```

From the JSON response:
- Extract `info.version` as `LATEST_PYPI_VERSION`
- This is the version we will compare against

---

## Step 3: Determine if CHANGELOG needs updating

Check if CHANGELOG.md already has a section for the current version:
- If there's a section `## {CURRENT_VERSION} (Unreleased)` — we will update it
- If there's a section `## {CURRENT_VERSION} (YYYY-MM-DD)` with an actual date — the version is already released, report this to the user and stop
- If there's no section for `CURRENT_VERSION` — we will create a new one

---

## Step 4: Construct the GitHub tag for the released version

The tag name for a released version follows this pattern:
```
azure-ai-projects_{VERSION}
```

For example, for version `2.2.0`, the tag is `azure-ai-projects_2.2.0`.

The source code for that release can be found at:
```
https://github.com/Azure/azure-sdk-for-python/tree/azure-ai-projects_{VERSION}/sdk/ai/azure-ai-projects
```

---

## Step 5: Compare public APIs

Compare the public APIs between the current branch and the latest released version. Focus on these locations:

### 5a. Public classes and enums in `azure/ai/projects/models/__init__.py`

Compare the `__all__` list and imports in both versions to identify:
- **New classes/enums**: Present in current branch but not in released version
- **Removed classes/enums**: Present in released version but not in current branch  
- **Renamed classes/enums**: Check if a removed class has a similar new class (likely a rename)

### 5b. Public operations in `azure/ai/projects/operations/__init__.py`

Compare the `__all__` list to identify new or removed operation classes.

### 5c. Public methods on sub-clients

For each operations class (like `AgentsOperations`, `BetaOperations`, etc.), compare the public methods:
- Look at files under `azure/ai/projects/operations/` and `azure/ai/projects/aio/operations/`
- Also check `_patch.py` files which may define additional public methods
- Public methods are those that don't start with underscore `_`

### 5d. Properties on model classes

For significant model classes, compare public properties (attributes) between versions:
- Properties are defined in `azure/ai/projects/models/_models.py`
- Look for new, removed, or renamed properties
- Pay attention to required vs optional changes

### 5e. Beta sub-clients on `BetaOperations`

The `BetaOperations` class exposes beta/preview functionality. Check for:
- New sub-client properties (like `.beta.datasets`, `.beta.models`, `.beta.routines`, etc.)
- Removed sub-client properties
- Check both `azure/ai/projects/operations/_patch.py` and the released version

### 5f. Sample files in `samples/` folder

Compare sample files between the current branch and the released version:

1. **List all `.py` files** recursively under `samples/` in both versions
2. **Identify new samples**: Files present in current branch but not in released version
3. **Identify removed samples**: Files present in released version but not in current branch
4. **Ignore async variants**: If a sample has both sync and async versions (e.g., `sample_foo.py` and `sample_foo_async.py`), only report the sync version
5. **Check existing changelog entries**: If a sample is already mentioned in the current changelog section, leave it as is
6. **Remove stale entries**: If a sample mentioned in the changelog has been removed from the codebase, remove it from the changelog

For each new sample, provide a one-line description of what it demonstrates. Read the sample file to understand its purpose — typically the docstring at the top or the `if __name__ == "__main__"` block explains what it does.

---

## Step 6: Categorize the changes

Organize detected changes into these categories:

### Features Added
- New sub-clients (e.g., "New `.beta.routines` sub-client with routine operations: `create_or_update`, `get`, `enable`, ...")
- New methods on existing sub-clients (e.g., "New methods on `.beta.agents` for optimization jobs: `create_optimization_job`, `get_optimization_job`, ...")
- New model classes that represent significant features (e.g., "Support integration of external Agents. See new `ExternalAgentDefinition` class.")
- New properties on existing classes (e.g., "New optional `force` parameter on `agents.delete` method.")
- New tools (e.g., "New Agent tool in preview `FabricIQPreviewTool`.")

### Breaking Changes
List breaking changes in beta methods and classes separately:
- Renamed methods (e.g., "Method `.beta.agents.get_session_files` renamed to `.beta.agents.list_session_files`.")
- Renamed arguments (e.g., "Argument `body` in method `.beta.skills.create_from_files()` renamed to `content`.")
- Signature changes (e.g., "Method `.beta.skills.create` signature changed — now takes `name` and keyword `inline_content: SkillInlineContent`; returns `SkillVersion`.")
- Renamed classes (e.g., "Renamed class `AgentEndpoint` to `AgentEndpointConfig`.")
- Property changes (e.g., "Required property `isolation_key_source` removed from class `EntraAuthorizationScheme`.")
- Renamed properties (e.g., "Property `skill_id` renamed to `id` on class `SkillDetails`.")

**Format for beta changes:**
```markdown
Breaking changes in beta methods:
* ...

Breaking changes in beta classes:
* ...
```

### Bugs Fixed
This section typically contains bug fixes. Leave empty unless you have specific bug fix information to add.

### Sample updates
List new sample files that were added, with a one-line description of what they demonstrate:
- Compare sample files in the `samples/` folder between current branch and released version
- Only report the sync version — do not list async samples separately (files ending with `_async.py`)
- If a sample is already mentioned in the existing changelog section, preserve that entry
- If a sample mentioned in the changelog has been removed from the codebase, remove it from the changelog
- Group related samples together (e.g., all agent samples, all evaluation samples)
- Use format: `Added \`sample_name.py\` demonstrating [brief description].`

---

## Step 7: Format the changelog entry

Use this format for the changelog entry:

```markdown
## {CURRENT_VERSION} (Unreleased)

### Features Added

* [List each feature on its own bullet point]

### Breaking Changes

Breaking changes in beta methods:
* [List method changes]

Breaking changes in beta classes:
* [List class changes]

### Bugs Fixed

* [List bug fixes, if any]

### Sample updates

* [List sample updates, if any]
```

**Guidelines for writing entries:**
- For new methods: mention the sub-client and method name, briefly describe what it does. Only report the sync version — do not list both sync and async versions separately.
- For new sub-clients: list all the methods it provides (sync versions only)
- For new tools: just mention the class name
- For property changes: mention the class name and the affected property
- For renames: show "X renamed to Y" format
- Use backticks for code references: `.beta.agents`, `create_version()`, `AgentDetails`

---

## Step 8: Update CHANGELOG.md

Insert or update the changelog entry in `CHANGELOG.md`:

1. If updating an existing "(Unreleased)" section:
   - Replace the existing section content with the new content
   - Preserve any manually-added entries that aren't API-related (like "Sample updates" written by developers)

2. If creating a new section:
   - Insert the new section immediately after the `# Release History` header
   - Keep all previous version sections intact

---

## Step 9: Report to user

After updating the changelog, report:
1. The current version and latest PyPI version compared
2. Summary of changes detected:
   - Number of new classes/enums
   - Number of new methods
   - Number of breaking changes
   - Number of removed items
3. Remind the user to:
   - Review the generated changelog for accuracy
   - Add any bug fixes that were made
   - Review sample descriptions for accuracy
   - Verify method descriptions are accurate

---

## Tips for API Comparison

### Using git to compare files

You can compare files between the current branch and a tag:
```bash
git diff azure-ai-projects_{VERSION} -- azure/ai/projects/models/__init__.py
```

### Using GitHub raw URLs

To fetch files from the released version:
```
https://raw.githubusercontent.com/Azure/azure-sdk-for-python/azure-ai-projects_{VERSION}/sdk/ai/azure-ai-projects/azure/ai/projects/models/__init__.py
```

### Identifying renames vs additions/removals

If a class was removed and a similar class was added, it's likely a rename. Look for:
- Similar names (e.g., `SkillObject` → `SkillDetails`)
- Similar structure/properties
- Check if there's a corresponding note in the TypeSpec changes

---

## Example Output

Here's an example of a well-formatted changelog entry:

```markdown
## 2.3.0 (Unreleased)

### Features Added

* Support integration of external Agents (in preview). See new `ExternalAgentDefinition` class.
* New Agent tool in preview `FabricIQPreviewTool`.
* New Agent tool in preview `ToolboxSearchPreviewTool`.
* New methods on `.beta.agents` for 
  * Code-based hosted agents: `create_version_from_code`, `download_code`.
  * Optimization jobs: `create_optimization_job`, `get_optimization_job`, `list_optimization_jobs`, `cancel_optimization_job`, `list_optimization_candidates`.
  * Optimization candidate management: `list_optimization_candidates`, `get_optimization_candidate`, `get_optimization_candidate_config`, `get_optimization_candidate_results`, `get_candidate_file`, `promote_candidate`.
  * `stop_session` to stop a running agent session.
* New `.beta.datasets` sub-client with data generation job operations: `create_generation_job`, `get_generation_job`, `list_generation_jobs`, `cancel_generation_job`, `delete_generation_job`.
* New `.beta.models` sub-client to handle AI model weights: `create`, `list_versions`, `list`, `get`, `delete`, `update`, `pending_create_version`, `pending_upload`, `get_credentials`.
* New `.beta.routines` sub-client with routine operations: `create_or_update`, `get`, `enable`, `disable`, `list`, `delete`, `list_runs`, `dispatch`.
* New methods on `.beta.evaluators` for evaluator generation jobs: `create_generation_job`, `get_generation_job`, `list_generation_jobs`, `cancel_generation_job`, `delete_generation_job`.
* New methods on `.beta.memory_stores` to handle individual memory items: `create_memory`, `update_memory`, `list_memories`, `get_memory`, `delete_memory`.
* New methods on `.beta.skills` for versioned skill management: `create`, `list_versions`, `get_version`, `download_version`, `delete_version`.
* New optional string properties `description` and `name` added to Agent tools classes which did not have them before.
* New optional `tool_configs` added to Agent tool classes.
* New read-only property `content_hash` on `CodeConfiguration`, returning the SHA-256 hex digest of the uploaded code zip.
* New optional `force` parameter on `agents.delete` and `agents.delete_version` methods.
* New optional `blueprint_reference` parameters on `agents.create_version` method.


### Breaking Changes

Breaking changes in beta methods:
* Argument `isolation_key` in methods `.beta.agents.create_session()` and `.beta.agents.delete_session()` renamed to `user_isolation_key`.
* Argument `body` in methods `.beta.evaluation_taxonomies.create()` and `.beta.evaluation_taxonomies.update()` renamed to `taxonomy`.
* Argument `body` in method `.beta.skills.create_from_files()` renamed to `content`.
* Method `.beta.agents.get_session_files` renamed to `.beta.agents.list_session_files`.
* Method `.beta.skills.create` signature changed — now takes `name` and keyword `inline_content: SkillInlineContent`; returns `SkillVersion`.
* Method `.beta.skills.create_from_package` renamed to `.beta.skills.create_from_files`.
* Method `.beta.skills.create_from_files` signature changed — now takes `name` and `content: CreateSkillVersionFromFilesBody`; returns `SkillVersion`.
* Method `.beta.skills.update` signature changed — now only accepts keyword `default_version`; returns `SkillDetails`.

Breaking changes in beta classes:
* Required property `isolation_key_source` removed from class `EntraAuthorizationScheme`.
* Renamed class `AgentEndpoint` to `AgentEndpointConfig`.
* Renamed class `DeleteSkillResponse` to `DeleteSkillResult`.
* Renamed class `SessionDirectoryListResponse` to `SessionDirectoryListResult`.
* Renamed class `SessionFileWriteResponse` to `SessionFileWriteResult`.
* Renamed class `SkillObject` to `SkillDetails`. Property `skill_id` renamed to `id`. Properties `has_blob` and `metadata` were removed.
* Renamed class `Target` to `EvaluationTarget`.
* Renamed class `TargetConfig` to `RedTeamTargetConfig`.

### Bugs Fixed

* Fixed telemetry instrumentor to correctly call is_recording() as a method on spans, ensuring non-recording spans are properly skipped (e.g., when sampling is configured) ([GitHub issue 46544](https://github.com/Azure/azure-sdk-for-python/issues/46544)).

### Sample updates

* Added new Agent tool samples `sample_agent_work_iq.py` and `sample_agent_work_iq_async.py` demonstrating use of `WorkIQPreviewTool`.
* Added new Agent tool samples `sample_agent_fabric_iq.py` and `sample_agent_fabric_iq_async.py` demonstrating use of `FabricIQPreviewTool`.
* Hosted Agents:
  * Added Hosted Agent creation samples `sample_create_hosted_agent.py` and `sample_create_hosted_agent_async.py`, demonstrating hosted agent version creation and retrieval with `AIProjectClient`.
  * Added Hosted Agent code-upload samples `sample_create_hosted_agent_from_code.py` and `sample_create_hosted_agent_from_code_async.py`, demonstrating uploading a code package (zip) as a new hosted agent version.
  * The Hosted Agent creation sample also demonstrates assigning the hosted agent managed identity the Azure AI User RBAC role on the backing Azure AI account.
  * Updated the other Hosted Agent samples to reuse an existing Hosted Agent as a prerequisite, instead of creating a new hosted agent version in each sample.
* Added Toolbox tool-search sample `sample_toolboxes_with_search_preview.py` and `sample_toolboxes_with_search_preview_async.py`, demonstrating creating a Toolbox version with `ToolboxSearchPreviewTool` and invoking `MCPTool`.
* Added `.beta.models` samples under `samples/models/`:
  * `sample_models_basic.py` — synchronous end-to-end registration via the `create` helper (uses `azcopy`), followed by `get`, `list_versions`, `list`, `get_credentials`, `update`, and `delete`.
  * `sample_models_create_and_poll.py` — alternative synchronous registration that hand-rolls the spec's three-step flow (`pending_upload` → upload via `azure-storage-blob` → `pending_create_version` + poll), without taking a dependency on `azcopy`.
  * `sample_models_basic_async.py` — asynchronous version of the same three-step flow using `azure.ai.projects.aio.AIProjectClient` and `azure.storage.blob.aio.ContainerClient`.
* Added new evaluation sample `sample_model_evaluation_instant_model.py` demonstrating model evaluation with an instant model.
* Refreshed evaluation samples under `samples/evaluations/` and `samples/evaluations/agentic_evaluators/` (including `sample_agent_evaluation`, `sample_agent_response_evaluation`, `sample_eval_catalog_prompt_based_evaluators`, `sample_evaluations_ai_assisted`, `sample_evaluations_builtin_with_csv`, `sample_evaluations_builtin_with_dataset_id`, `sample_evaluations_builtin_with_inline_data`, `sample_evaluations_builtin_with_inline_data_oai`, `sample_scheduled_evaluations`, `sample_coherence`, `sample_fluency`, `sample_intent_resolution`, `sample_relevance`, `sample_response_completeness`, `sample_tool_call_accuracy`, `sample_tool_call_success`, `sample_tool_input_accuracy`, `sample_tool_output_utilization`, `sample_tool_selection`, and `sample_generic_agentic_evaluator`).
* New sample `sample_dataset_generation_job_simpleqna_with_prompt_source.py` showing an end-to-end flow that generates a QnA dataset via `.beta.datasets.create_generation_job` and runs an OpenAI evaluation.

```
