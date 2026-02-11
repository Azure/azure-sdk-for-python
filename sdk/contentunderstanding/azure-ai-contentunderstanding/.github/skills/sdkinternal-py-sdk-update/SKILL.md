---
name: sdkinternal-py-sdk-update
description: "Update the azure-ai-contentunderstanding SDK from a new TypeSpec commit. Use when the TypeSpec spec has been updated and the SDK needs regeneration."
---

# Update SDK from TypeSpec Commit

This skill guides updating the `azure-ai-contentunderstanding` SDK when a new TypeSpec commit is available.

## Prerequisites

- Node.js LTS installed (>= 22.16.0)
- Python >= 3.9 with pip and venv
- tsp-client installed from `eng/common/tsp-client`
- Virtual environment activated with dev dependencies

### Check and Create Virtual Environment

```bash
cd sdk/contentunderstanding/azure-ai-contentunderstanding

# Check if venv exists, create if not
if [ -d ".venv" ]; then
    echo "Virtual environment already exists at .venv"
else
    echo "Creating virtual environment..."
    python -m venv .venv
    echo "Virtual environment created at .venv"
fi
```

### Activate Virtual Environment

**On Linux/macOS:**
```bash
source .venv/bin/activate
```

**On Windows (PowerShell):**
```powershell
.venv\Scripts\Activate.ps1
```

**On Windows (Command Prompt):**
```cmd
.venv\Scripts\activate.bat
```

Verify activation:
```bash
which python  # Should show .venv/bin/python
```

### Install Dependencies

```bash
pip install -e .
pip install -r dev_requirements.txt
pip install "tox<5" black bandit
```

### Complete Setup Script

Alternatively, run the automated setup script:

```bash
.github/skills/sdkinternal-py-setup/scripts/setup_venv.sh
```

## Workflow Steps

### Step 1: Update TypeSpec Commit Reference

Update the `commit` field in `tsp-location.yaml`:

```yaml
# File: sdk/contentunderstanding/azure-ai-contentunderstanding/tsp-location.yaml
directory: specification/ai/ContentUnderstanding
commit: <NEW_COMMIT_SHA> # Update this
repo: Azure/azure-rest-api-specs
```

### Step 2: Install tsp-client (if not already)

```bash
cd eng/common/tsp-client
npm ci
```

### Step 3: Regenerate SDK

Run from the tsp-client directory:

```bash
cd eng/common/tsp-client
npx tsp-client update -o ../../../sdk/contentunderstanding/azure-ai-contentunderstanding
```

This regenerates the SDK from the TypeSpec specification.

### Step 4: Run Black Formatting First

**Important**: Run `black` immediately after regeneration, BEFORE fixing any pyright or pylint issues.

```bash
cd sdk/contentunderstanding/azure-ai-contentunderstanding
black azure/
```

**Why this order matters**: `black` reformats code — including multi-line return type annotations in `_patch.py` files. This can move `# pyright: ignore[...]` comments from the correct line (the type annotation) to the wrong line (the closing parenthesis). If you fix pyright comments first and then run `black`, black will undo your fixes, requiring double work.

The correct sequence is:
1. Regenerate SDK (Step 3)
2. Run `black azure/` to auto-format everything (this step)
3. Fix pyright ignore comments on correct lines (Step 5b)
4. Fix pylint suppressions in generated files (Step 5c)

### Step 5: Verify Customizations Are Preserved

Python SDK customizations are applied via `_patch.py` files which are NOT overwritten during regeneration. Verify these files are intact:

Key patch files with customizations:
- `azure/ai/contentunderstanding/_patch.py` - Sync client (string_encoding, content_type defaults)
- `azure/ai/contentunderstanding/models/_patch.py` - Models (AnalyzeLROPoller, .value property, KeyFrameTimesMs, RecordMergePatchUpdate)
- `azure/ai/contentunderstanding/aio/_patch.py` - Async client (string_encoding, content_type defaults)
- `azure/ai/contentunderstanding/aio/models/_patch.py` - Async models (AnalyzeAsyncLROPoller)

Empty patch files (no current customizations):
- `azure/ai/contentunderstanding/_operations/_patch.py`
- `azure/ai/contentunderstanding/aio/_operations/_patch.py`
- `azure/ai/contentunderstanding/operations/_patch.py`
- `azure/ai/contentunderstanding/aio/operations/_patch.py`

#### Step 5a: Verify Customizations Still Work with New Generated Code

Regeneration can significantly change the generated code structure. Customizations in `_patch.py` files reference generated classes and methods — these references may break if the generated code changes. Check for:

1. **Import changes**: If generated classes are renamed, moved, or removed, `_patch.py` imports will fail. Compare the imports in each `_patch.py` file against the current generated `__init__.py` and `_models.py` files.
2. **Superclass method signature changes**: The `_patch.py` client classes override `begin_analyze` and `begin_analyze_binary` from the generated client. If the generated method signatures changed (new parameters, removed parameters, renamed parameters), update the overrides to match.
3. **Model class changes**: The `patch_sdk()` function in `models/_patch.py` patches model classes at runtime. If model classes were renamed or restructured, these patches may need updating.
4. **Run a quick smoke test**: After verifying, run `python -c "from azure.ai.contentunderstanding import ContentUnderstandingClient"` to ensure imports succeed.

#### Step 5b: Fix Pyright Ignore Comment Placement

After `black` reformats the code, `# pyright: ignore[reportInvalidTypeArguments]` comments often end up on the wrong line. The comment must be on the same line as the type annotation string, not on the closing parenthesis.

**Wrong** (after black reformats):
```python
    ) -> (
        "AnalyzeLROPoller[_models.AnalyzeResult]"
    ):  # pyright: ignore[reportInvalidTypeArguments]  <-- wrong line
```

**Correct**:
```python
    ) -> (
        "AnalyzeLROPoller[_models.AnalyzeResult]"  # pyright: ignore[reportInvalidTypeArguments]
    ):
```

Similarly for `object.__new__` calls:
```python
# Wrong:
        instance = object.__new__(
            cls
        )  # pyright: ignore[reportInvalidTypeArguments]  <-- wrong line

# Correct:
        instance = object.__new__(  # pyright: ignore[reportInvalidTypeArguments]
            cls
        )
```

Files that need this fix after every regeneration:
- `azure/ai/contentunderstanding/_patch.py` (5 return type annotations)
- `azure/ai/contentunderstanding/aio/_patch.py` (5 return type annotations)
- `azure/ai/contentunderstanding/models/_patch.py` (1 return type + 1 object.__new__)
- `azure/ai/contentunderstanding/aio/models/_patch.py` (1 return type + 1 object.__new__)

#### Step 5c: Fix Pylint Suppressions in Generated Files

Regeneration can produce significantly different code that triggers new pylint rules. The generated files may need `# pylint: disable=...` comments added or updated at the file level.

**Known pylint suppressions needed for generated files:**

| File | Pylint Rules to Suppress | Reason |
|------|--------------------------|--------|
| `models/_enums.py` | `enum-must-be-uppercase` | `GLOBALEnum = "global"` uses mixed case (Azure SDK convention) |
| `_validation.py` | `protected-access` | Accesses `_config` on client class |
| `_utils/model_base.py` | `no-member`, `comparison-with-callable` | Accesses `__mapping__` and compares callables |
| `_utils/serialization.py` | `protected-access`, `inconsistent-return-statements`, `unnecessary-lambda-assignment` | Various generated patterns |
| `_operations/_operations.py` | `name-too-long`, `inconsistent-return-statements` | Function names >40 chars, missing return expressions |

**How to add suppressions**: Add/update the `# pylint: disable=...` comment at the top of the file. The comment must appear AFTER the `# coding=utf-8` line and copyright header to avoid `file-needs-copyright-header` errors.

**Example** (correct placement):
```python
# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# Code generated by Microsoft (R) Python Code Generator.
# Changes may cause incorrect behavior and will be lost if the code is regenerated.
# --------------------------------------------------------------------------
# pylint: disable=protected-access,inconsistent-return-statements
```

**Note**: These suppressions may change between regenerations as the emitter evolves. Always run `tox -e pylint` after regeneration to identify which suppressions are needed. Some suppressions from a previous regeneration may become unnecessary (remove them to keep the code clean), while new ones may be required.

### Step 6: Check Fix Status

Verify each fix listed in the "Current Known Fixes" section below is still applied in the `_patch.py` files.

| Fix # | Description | Check Location | Verification |
|-------|-------------|----------------|--------------|
| 1 | Default `string_encoding` to "codePoint" | `_patch.py` and `aio/_patch.py` in `begin_analyze` and `begin_analyze_binary` | Has `kwargs["string_encoding"] = "codePoint"` |
| 2 | `AnalyzeLROPoller` with `.operation_id` property (sync) | `models/_patch.py` | `AnalyzeLROPoller` class exists with `operation_id` property, `from_poller()`, `from_continuation_token()` |
| 3 | `AnalyzeAsyncLROPoller` with `.operation_id` property (async) | `aio/models/_patch.py` | `AnalyzeAsyncLROPoller` class exists with `operation_id` property, `from_poller()`, `from_continuation_token()` |
| 4 | `.value` property on ContentField types | `models/_patch.py` in `patch_sdk()` | `_add_value_property_to_field` calls for all 9 field types + `ContentField` base class |
| 5 | `KeyFrameTimesMs` casing normalization | `models/_patch.py` in `patch_sdk()` | `_patched_audio_visual_content_init` handles both casings |
| 6 | `RecordMergePatchUpdate` type alias | `models/_patch.py` | `RecordMergePatchUpdate = Dict[str, str]` |
| 7 | Default `content_type` for `begin_analyze_binary` | `_patch.py` and `aio/_patch.py` | Has `content_type: str = "application/octet-stream"` |
| 8 | Parameter order for analyze methods | `_patch.py` and `aio/_patch.py` | `begin_analyze` convenience: `inputs, model_deployments, processing_location` (no `content_type`); `begin_analyze_binary`: `input_range, content_type, processing_location` |

**If a fix is now included in the generated code upstream, remove it from this skill document.**

### Step 7: Run CI Checks

All CI checks use tox with the configuration from `eng/tox/tox.ini`. Run from the package directory:

```bash
cd sdk/contentunderstanding/azure-ai-contentunderstanding
```

#### Required CI Checks

These checks run in CI and must pass:

**Pylint** (Linting)
```bash
tox -e pylint -c ../../../eng/tox/tox.ini --root .
```

**MyPy** (Type Checking)
```bash
tox -e mypy -c ../../../eng/tox/tox.ini --root .
```

**Pyright** (Type Checking)
```bash
tox -e pyright -c ../../../eng/tox/tox.ini --root .
```

**Black** (Code Formatting)
```bash
black --check azure/
# To auto-format: black azure/
```

**Bandit** (Security Linting)
```bash
bandit -r azure/ -x "azure/**/tests/**"
```

#### Release Blocking Checks

**Sphinx** (Documentation)
```bash
tox -e sphinx -c ../../../eng/tox/tox.ini --root .
```

**Tip:** Use `TOX_PIP_IMPL=uv` for faster package installation:
```bash
TOX_PIP_IMPL=uv tox -e pylint -c ../../../eng/tox/tox.ini --root .
```

### Step 8: Run Tests

Run tests in **playback mode** to verify the regenerated SDK works with existing recordings:

```bash
cd sdk/contentunderstanding/azure-ai-contentunderstanding
AZURE_TEST_RUN_LIVE=false pytest
```

Run specific test:
```bash
AZURE_TEST_RUN_LIVE=false pytest tests/test_content_understanding_content_analyzers_operations.py::TestContentUnderstandingContentAnalyzersOperations::test_content_analyzers_get
```

If tests fail:
1. Check if model/API changes broke test assertions — update tests as needed
2. If API behavior changed, re-record with `AZURE_TEST_RUN_LIVE=true AZURE_TEST_RECORD_MODE=true pytest`
3. See `tests/README.md` for detailed testing guide

### Step 9: Update This Skill Document

**Important**: Update this SKILL.md file directly with any changes:

- Add any new fixes discovered during this update
- Remove fixes that are now included in upstream generated code
- Update fix descriptions if implementation details changed

---

## Current Known Fixes

These fixes address issues in the generated code that are not yet resolved upstream in the TypeSpec emitter. Customizations are applied via `_patch.py` files, which are preserved during regeneration.

### Fix 1: Default string_encoding to "codePoint"

**Files**: 
- `azure/ai/contentunderstanding/_patch.py` (sync)
- `azure/ai/contentunderstanding/aio/_patch.py` (async)

**Problem**: The generated code does not set a default value for `string_encoding`, but Python strings use Unicode code points for `len()` and indexing.

**Why this matters**:
- Python's `str[i]` and `len(str)` operate on Unicode code points
- Without this default, span offsets and lengths returned by the service may not align correctly with Python string operations
- Users would need to remember to always pass `string_encoding="codePoint"` manually

**Fix**: Override `begin_analyze` and `begin_analyze_binary` to set the default:

```python
# In begin_analyze and begin_analyze_binary:
kwargs["string_encoding"] = "codePoint"
```

---

### Fix 2: AnalyzeLROPoller with .operation_id Property (Sync)

**File**: `azure/ai/contentunderstanding/models/_patch.py`

**Problem**: The generated LROPoller does not expose the operation ID, which is needed to call `get_result_file()`.

**Why this matters**:
- Users need the operation ID to retrieve intermediate or final result files from the service
- The operation ID is embedded in the `Operation-Location` header but not easily accessible

**Fix**: Custom `AnalyzeLROPoller` class that extracts and exposes the operation ID:

```python
class AnalyzeLROPoller(LROPoller[PollingReturnType_co]):
    @property
    def operation_id(self) -> str:
        operation_location = self.polling_method()._initial_response.http_response.headers["Operation-Location"]
        return _parse_operation_id(operation_location)

    @classmethod
    def from_poller(cls, poller: LROPoller[PollingReturnType_co]) -> "AnalyzeLROPoller[PollingReturnType_co]":
        """Wrap an existing LROPoller without re-initializing the polling method."""
        instance = object.__new__(cls)
        instance.__dict__.update(poller.__dict__)
        return instance

    @classmethod
    def from_continuation_token(cls, polling_method, continuation_token, **kwargs) -> "AnalyzeLROPoller":
        """Create a poller from a continuation token."""
        # ... implementation
```

---

### Fix 3: AnalyzeAsyncLROPoller with .operation_id Property (Async)

**File**: `azure/ai/contentunderstanding/aio/models/_patch.py`

**Problem**: Same as Fix 2, but for async operations.

**Why this matters**: Async users also need access to the operation ID for `get_result_file()`.

**Fix**: Custom `AnalyzeAsyncLROPoller` class (mirrors sync version):

```python
class AnalyzeAsyncLROPoller(AsyncLROPoller[PollingReturnType_co]):
    @property
    def operation_id(self) -> str:
        operation_location = self.polling_method()._initial_response.http_response.headers["Operation-Location"]
        return _parse_operation_id(operation_location)

    @classmethod
    def from_poller(cls, poller: AsyncLROPoller[PollingReturnType_co]) -> "AnalyzeAsyncLROPoller[PollingReturnType_co]":
        """Wrap an existing AsyncLROPoller without re-initializing the polling method."""
        instance = object.__new__(cls)
        instance.__dict__.update(poller.__dict__)
        return instance

    @classmethod
    async def from_continuation_token(cls, polling_method, continuation_token, **kwargs):
        """Create a poller from a continuation token."""
        # ... implementation
```

---

### Fix 4: Add .value Property to ContentField Types

**File**: `azure/ai/contentunderstanding/models/_patch.py`

**Problem**: The generated ContentField subtypes (StringField, NumberField, etc.) only expose typed properties like `value_string`, `value_number`, etc. This differs from other Azure SDKs which expose a convenient `value` property.

**Why this matters**:
- Improves developer experience by providing a consistent, simpler way to access field values
- Reduces boilerplate in user code (no need to check field type before accessing value)
- Simplifies samples and documentation

**Fix**: Add a `value` property to each ContentField subtype AND the base class at runtime in `patch_sdk()`:

```python
# For each specific subtype:
_add_value_property_to_field(StringField, "value_string", Optional[str])
_add_value_property_to_field(IntegerField, "value_integer", Optional[int])
_add_value_property_to_field(NumberField, "value_number", Optional[float])
_add_value_property_to_field(BooleanField, "value_boolean", Optional[bool])
_add_value_property_to_field(DateField, "value_date", Optional[str])
_add_value_property_to_field(TimeField, "value_time", Optional[str])
_add_value_property_to_field(ArrayField, "value_array", Optional[List[Any]])
_add_value_property_to_field(ObjectField, "value_object", Optional[Dict[str, Any]])
_add_value_property_to_field(JsonField, "value_json", Optional[Any])

# For the base ContentField class (dynamic lookup):
def _content_field_value_getter(self: ContentField) -> Any:
    for attr in ["value_string", "value_integer", "value_number", ...]:
        if hasattr(self, attr):
            return getattr(self, attr)
    return None
```

---

### Fix 5: KeyFrameTimesMs Property Casing Inconsistency

**File**: `azure/ai/contentunderstanding/models/_patch.py`

**Problem**: The Content Understanding service has a known issue where it returns `KeyFrameTimesMs` (PascalCase) instead of the expected `keyFrameTimesMs` (camelCase) for the `AudioVisualContent` type.

**Why this matters**: Without this fix, the SDK would fail to deserialize the `key_frame_times_ms` property when the service returns PascalCase, causing data loss for users processing video content.

**Fix**: Patch `AudioVisualContent.__init__` to normalize the casing (forward compatible):

```python
_original_audio_visual_content_init = _models.AudioVisualContent.__init__

def _patched_audio_visual_content_init(self, *args: Any, **kwargs: Any) -> None:
    if args and isinstance(args[0], dict):
        mapping = dict(args[0])
        # Forward compatible: only normalizes if incorrect casing exists and correct casing doesn't
        if "KeyFrameTimesMs" in mapping and "keyFrameTimesMs" not in mapping:
            mapping["keyFrameTimesMs"] = mapping["KeyFrameTimesMs"]
        args = (mapping,) + args[1:]
    _original_audio_visual_content_init(self, *args, **kwargs)

_models.AudioVisualContent.__init__ = _patched_audio_visual_content_init
```

---

### Fix 6: RecordMergePatchUpdate Type Alias

**File**: `azure/ai/contentunderstanding/models/_patch.py`

**Problem**: `RecordMergePatchUpdate` is a TypeSpec artifact used for model deployments that wasn't generated.

**Why this matters**: The type is referenced but missing, causing import errors.

**Fix**: Define as a type alias:

```python
RecordMergePatchUpdate = Dict[str, str]
```

---

### Fix 7: Default content_type for begin_analyze_binary

**Files**: 
- `azure/ai/contentunderstanding/_patch.py` (sync)
- `azure/ai/contentunderstanding/aio/_patch.py` (async)

**Problem**: The generated `begin_analyze_binary` method may not have the correct default `content_type` for binary uploads.

**Why this matters**: Users uploading binary files (PDFs, images, etc.) should have `application/octet-stream` as the default, not `application/json`.

**Fix**: Override `begin_analyze_binary` with correct default:

```python
def begin_analyze_binary(
    self,
    analyzer_id: str,
    binary_input: bytes,
    *,
    content_type: str = "application/octet-stream",  # Correct default for binary
    **kwargs: Any,
) -> "AnalyzeLROPoller[_models.AnalyzeResult]":
    # ...
```

---

### Fix 8: Parameter Order for Analyze Methods

**Files**: 
- `azure/ai/contentunderstanding/_patch.py` (sync)
- `azure/ai/contentunderstanding/aio/_patch.py` (async)

**Problem**: The generated code does not order parameters consistently with other Azure SDKs (e.g., Java). The expected order is to list the most commonly used parameters first.

**Expected parameter order**:
- `begin_analyze` (convenience): `analyzer_id, *, inputs, model_deployments, processing_location` (no `content_type`)
- `begin_analyze` (body overloads): `analyzer_id, body, *, processing_location, content_type`
- `begin_analyze_binary`: `analyzer_id, binary_input, *, input_range, content_type, processing_location`

**Why this matters**: Consistent parameter ordering across language SDKs improves developer experience and reduces confusion when porting code between languages. The convenience overload doesn't need `content_type` since it's always JSON.

**Note**: The generated code includes `content_type` in all `begin_analyze` overloads. We explicitly remove it from the convenience overload (with `inputs`/`model_deployments`) to match the Java SDK API. The `body` overloads retain `content_type` for advanced users who pass raw JSON or binary streams.

**Fix**: Override methods with correct parameter order:

```python
# begin_analyze (convenience overload - no content_type)
def begin_analyze(
    self,
    analyzer_id: str,
    *,
    inputs: Optional[list[_models.AnalyzeInput]] = None,
    model_deployments: Optional[dict[str, str]] = None,
    processing_location: Optional[Union[str, _models.ProcessingLocation]] = None,
    **kwargs: Any,
) -> "AnalyzeLROPoller[_models.AnalyzeResult]":
    # ...

# begin_analyze (implementation - keeps content_type internally)
def begin_analyze(
    self,
    analyzer_id: str,
    body: Union[JSON, IO[bytes]] = _Unset,
    *,
    inputs: Optional[list[_models.AnalyzeInput]] = None,
    model_deployments: Optional[dict[str, str]] = None,
    processing_location: Optional[Union[str, _models.ProcessingLocation]] = None,
    content_type: Optional[str] = None,
    **kwargs: Any,
) -> "AnalyzeLROPoller[_models.AnalyzeResult]":
    # ...

# begin_analyze_binary
def begin_analyze_binary(
    self,
    analyzer_id: str,
    binary_input: bytes,
    *,
    input_range: Optional[str] = None,
    content_type: str = "application/octet-stream",
    processing_location: Optional[Union[str, _models.ProcessingLocation]] = None,
    **kwargs: Any,
) -> "AnalyzeLROPoller[_models.AnalyzeResult]":
    # ...
```

---

## Troubleshooting

### tsp-client: command not found

Run `npx` from the `eng/common/tsp-client` directory where it's installed:

```bash
cd eng/common/tsp-client
npx tsp-client update -o ../../../sdk/contentunderstanding/azure-ai-contentunderstanding
```

### Missing pip or venv

Install Python dependencies (Ubuntu):

```bash
sudo apt install python-is-python3 python3-pip python3.12-venv
```

### Pylint/MyPy/Sphinx Failures After Regeneration

1. Check if generated code introduced new pylint violations — add suppressions per Step 5c
2. Verify `_patch.py` files weren't accidentally modified
3. May need to update customizations for new generated code structure (see Step 5a)

### Pyright Failures After Regeneration

1. Check if `# pyright: ignore` comments were moved to wrong lines by `black` — fix per Step 5b
2. New generated code may introduce new pyright errors in `_utils/` files — add `# pyright: ignore` on the correct line

### Tox Issues

1. **Missing tox**: `pip install tox`
2. **Tox version mismatch**: Requires tox >= 4.4.10. Upgrade: `pip install --upgrade tox`
3. **Slow installation**: Use uv: `TOX_PIP_IMPL=uv tox -e pylint ...`

### Tests Fail

1. Check if model/API changes broke test assertions — update tests as needed
2. If API behavior changed, re-record: `AZURE_TEST_RUN_LIVE=true AZURE_TEST_RECORD_MODE=true pytest`
3. See `tests/README.md` for test-proxy troubleshooting (connection refused errors, etc.)

### Customizations Not Applied

1. Ensure all 8 `_patch.py` files exist and weren't deleted during regeneration
2. Check that `__all__` exports include customized classes in files that have them
3. Verify `patch_sdk()` is called (happens automatically on import via `__init__.py`)
4. Compare current `_patch.py` content against this skill document to ensure all fixes are present

---

## Related Files

- `tsp-location.yaml` - TypeSpec commit reference
- `azure/ai/contentunderstanding/_patch.py` - Client customizations (sync) - **Fixes 1, 7, 8**
- `azure/ai/contentunderstanding/aio/_patch.py` - Client customizations (async) - **Fixes 1, 7, 8**
- `azure/ai/contentunderstanding/models/_patch.py` - Model customizations - **Fixes 2, 4, 5, 6**
- `azure/ai/contentunderstanding/aio/models/_patch.py` - Async poller customizations - **Fix 3**
- `azure/ai/contentunderstanding/_operations/_patch.py` - Currently empty (no customizations)
- `azure/ai/contentunderstanding/aio/_operations/_patch.py` - Currently empty (no customizations)
- `azure/ai/contentunderstanding/operations/_patch.py` - Currently empty (no customizations)
- `azure/ai/contentunderstanding/aio/operations/_patch.py` - Currently empty (no customizations)
- `tests/README.md` - Testing guide with test modes and test-proxy configuration

## Reference Documentation

- [Python SDK Customization Guide](https://aka.ms/azsdk/python/dpcodegen/python/customize)
- [Local SDK Workflow](https://github.com/Azure/azure-sdk-for-python/blob/main/eng/common/instructions/azsdk-tools/local-sdk-workflow.instructions.md)
- [Azure SDK Python Design Guidelines](https://azure.github.io/azure-sdk/python_design.html)
- [Azure SDK Python Testing Guide](https://github.com/Azure/azure-sdk-for-python/blob/main/doc/dev/tests.md)
- [Repo Health Status](https://github.com/Azure/azure-sdk-for-python/blob/main/doc/repo_health_status.md) - Required checks (MyPy, Pylint, Sphinx, Tests)
- [Pylint Guide](https://github.com/Azure/azure-sdk-for-python/blob/main/doc/dev/pylint_checking.md)
- [Static Type Checking Guide](https://github.com/Azure/azure-sdk-for-python/blob/main/doc/dev/static_type_checking.md)
