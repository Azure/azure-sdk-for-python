---
name: do-code-review
description: Reviews code changes in azure-ai-ml package for quality, Azure SDK compliance, and best practices. Use when reviewing code, checking pull requests, or when user asks to review changes or check code quality in azure-ai-ml.
---

# Azure AI ML Code Review

Reviews uncommitted changes (staged and unstaged files) in the azure-ai-ml package, focusing on Azure SDK Python design guidelines, type safety, testing patterns, and API consistency.

## Default Review Scope

Unless otherwise specified, review all uncommitted changes in the current branch (staged and unstaged files) within `sdk/ml/azure-ai-ml/`. This includes new files, modified files, and any pending changes that haven't been committed yet.

## Review Focus Areas

### 1. Azure SDK Design Guidelines Compliance

- **Check**: Adherence to [Azure SDK Python Design Guidelines](https://azure.github.io/azure-sdk/python_design.html)
- **Look for**: Proper client naming, method patterns, parameter order
- **Flag**: Non-compliant naming (use `create_or_update` not `create_or_replace`)
- **Example Issue**: `def get_job(name, subscription_id)` should be `def get_job(name, **kwargs)`

**Key Patterns:**
- Client methods: `begin_*` for LROs, `list_*` for paginators
- Naming: snake_case for methods, PascalCase for classes
- Parameters: Required positional, optional keyword-only
- Return types: Explicit type hints for all public APIs

### 2. Type Annotations & MyPy Compliance

- **Check**: Complete type annotations on all public APIs
- **Look for**: Proper use of `Optional`, `Union`, `TYPE_CHECKING`
- **Flag**: Missing return types, `Any` without justification, bare `dict`/`list`
- **Example Issue**: `def process_data(data)` should be `def process_data(data: Dict[str, Any]) -> ProcessedData`

**Common Fixes:**
```python
# Bad
def get_config(name):
    return config

# Good
def get_config(name: str) -> Optional[Dict[str, Any]]:
    return config
```

### 3. Pylint Compliance

- **Check**: Code passes pylint with azure-sdk-for-python rules
- **Look for**: Proper docstrings, no unused imports, correct argument names
- **Flag**: Violations of naming conventions, too many arguments (>5), long lines (>120)
- **Reference**: [Azure Pylint Guidelines](https://github.com/Azure/azure-sdk-tools/blob/main/tools/pylint-extensions/azure-pylint-guidelines-checker/README.md)

**Watch for:**
- `client-method-should-not-use-static-method`
- `missing-client-constructor-parameter-credential`
- `client-method-has-more-than-5-positional-arguments`

### 4. Async/Await Patterns

- **Check**: Proper async implementation in `_async` modules
- **Look for**: Using `async with` for clients, awaiting coroutines correctly
- **Flag**: Blocking calls in async code, missing `await`, sync code in async modules
- **Example Issue**: `self._client.get()` in async should be `await self._client.get()`

**Pattern:**
```python
# In azure/ai/ml/aio/operations/
async def create_or_update(
    self,
    entity: Job,
    **kwargs: Any
) -> Job:
    async with self._lock:
        result = await self._service_client.create_or_update(...)
        return result
```

### 5. Error Handling & Validation

- **Check**: Proper exception handling with Azure SDK exceptions
- **Look for**: Use of `HttpResponseError`, `ResourceNotFoundError`, proper validation
- **Flag**: Bare `except:`, catching `Exception` without re-raising, missing validation
- **Example Issue**: Missing parameter validation before API calls

**Pattern:**
```python
from azure.core.exceptions import ResourceNotFoundError, HttpResponseError

try:
    result = self._operation.get(name)
except ResourceNotFoundError:
    raise ResourceNotFoundError(f"Job '{name}' not found")
except HttpResponseError as e:
    raise HttpResponseError(f"Failed to retrieve job: {e.message}")
```

### 6. API Design & Operations

- **Check**: Consistent CRUD patterns across operations classes
- **Look for**: Proper separation of sync/async, operations returning correct types
- **Flag**: Business logic in client, missing operations class, inconsistent method names

**Structure:**
```
azure/ai/ml/
├── operations/          # Sync operations
│   ├── job_operations.py
│   └── model_operations.py
└── aio/operations/      # Async operations (mirror structure)
    ├── job_operations.py
    └── model_operations.py
```

### 7. Entity & Schema Patterns

- **Check**: Proper use of marshmallow schemas, correct entity inheritance
- **Look for**: Schema validation, proper serialization/deserialization
- **Flag**: Direct dict manipulation instead of entities, missing schema validation

**Entity Pattern:**
```python
@dataclass
class Job(Resource):
    """Job entity."""
    
    name: str
    experiment_name: Optional[str] = None
    
    def _to_rest_object(self) -> RestJob:
        """Convert to REST representation."""
        ...
    
    @classmethod
    def _from_rest_object(cls, obj: RestJob) -> "Job":
        """Create from REST representation."""
        ...
```

### 8. Testing Patterns

- **Check**: Proper unit tests, recorded tests for operations
- **Look for**: Use of `pytest`, proper test isolation, fixture usage
- **Flag**: Missing tests for new features, tests with external dependencies, hardcoded values

**Test Structure:**
```python
class TestJobOperations:
    """Test job operations."""
    
    def test_create_job(self, client: MLClient, mock_workspace: Mock) -> None:
        """Test job creation."""
        job = Job(name="test-job")
        result = client.jobs.create_or_update(job)
        assert result.name == "test-job"
    
    @pytest.mark.recorded
    def test_get_job_recorded(self, client: MLClient) -> None:
        """Test getting job with recording."""
        ...
```

### 9. Documentation & Docstrings

- **Check**: Complete docstrings following Google/NumPy style
- **Look for**: Parameter descriptions, return types, examples, raises
- **Flag**: Missing docstrings on public APIs, incomplete parameter docs

**Docstring Pattern:**
```python
def create_or_update(
    self,
    job: Job,
    **kwargs: Any
) -> Job:
    """Create or update a job.
    
    :param job: The job entity to create or update.
    :type job: ~azure.ai.ml.entities.Job
    :keyword bool skip_validation: Skip validation of the job.
    :return: The created or updated job.
    :rtype: ~azure.ai.ml.entities.Job
    :raises ~azure.core.exceptions.HttpResponseError: If the request fails.
    
    .. admonition:: Example:
    
        .. code-block:: python
        
            from azure.ai.ml.entities import Job
            job = Job(name="my-job")
            result = ml_client.jobs.create_or_update(job)
    """
```

### 10. Backwards Compatibility

- **Check**: No breaking changes without major version bump
- **Look for**: Deprecated parameters, migration paths, version notes
- **Flag**: Removing public methods, changing signatures, removing parameters

**Deprecation Pattern:**
```python
import warnings

def old_method(self, param: str) -> None:
    """Deprecated method.
    
    .. deprecated:: 1.2.0
        Use :meth:`new_method` instead.
    """
    warnings.warn(
        "old_method is deprecated, use new_method instead",
        DeprecationWarning,
        stacklevel=2
    )
    self.new_method(param)
```

### 11. Security & Credentials

- **Check**: Proper credential handling, no secrets in logs
- **Look for**: Use of `TokenCredential`, proper token refresh, sanitized logging
- **Flag**: Credentials in error messages, API keys in code, secrets in tests

**Pattern:**
```python
from azure.core.credentials import TokenCredential

class MLClient:
    def __init__(
        self,
        credential: TokenCredential,
        subscription_id: str,
        **kwargs: Any
    ):
        self._credential = credential  # Store, don't log
        # Never log credential or tokens
```

### 12. Performance & Efficiency

- **Check**: Efficient API calls, proper pagination, lazy loading
- **Look for**: Batching operations, caching where appropriate, avoiding N+1 queries
- **Flag**: Loading all items in memory, multiple API calls in loops, no pagination

**Pagination Pattern:**
```python
def list(self, **kwargs: Any) -> Iterable[Job]:
    """List jobs with pagination.
    
    :return: An iterable of jobs.
    :rtype: ~azure.core.paging.ItemPaged[~azure.ai.ml.entities.Job]
    """
    return self._operation.list(...)  # Returns ItemPaged
```

## Analysis Instructions

1. **Get uncommitted changes**: Use git to identify modified files in `sdk/ml/azure-ai-ml/`
2. **Read changed sections**: Focus on modified lines and surrounding context
3. **Check each focus area**: Go through all 12 areas systematically
4. **Priority levels**: Critical (breaking/security) > High (bugs/types) > Medium (style/docs)
5. **Provide specific examples**: Show actual code with file paths and line numbers
6. **Cross-reference**: Check consistency across sync/async, operations/entities

## Output Format

Organize findings by priority and category:

### ✅ Positive Observations
Good patterns worth highlighting

### 🔴 Critical Issues
- Breaking changes without migration path
- Missing credential validation
- Type safety violations causing runtime errors
- Security vulnerabilities

### ⚠️ High Priority Issues
- Missing type annotations on public APIs
- Pylint/MyPy errors
- Missing tests for new functionality
- Improper async patterns

### 📋 Medium Priority Issues
- Missing or incomplete docstrings
- Code style inconsistencies
- Performance optimizations
- Better error messages

### 💡 Suggestions
- Refactoring opportunities
- Additional test coverage
- Documentation improvements

For each issue:
1. **Location**: File path and line numbers
2. **Current code**: Show the problematic code
3. **Issue**: Explain what's wrong and why
4. **Recommended fix**: Show corrected code
5. **References**: Link to relevant guidelines

### Summary

- Total files changed: X
- Critical issues: X
- High priority: X  
- Medium priority: X
- Overall assessment: Ready/Needs work/Blocked

Focus on issues that impact SDK quality, user experience, backwards compatibility, and Azure SDK guideline compliance.