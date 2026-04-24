# Concerns: `get_deployment_templates()` Convenience Method on AIProjectClient

## Proposed API

```python
templates = project_client.models.get_deployment_templates(model_name="my-gpt-oss-120B")
```

Internally: read custom model → parse `base_model` URI → call ML Registry → fetch each deployment template → return structured result.

---

## Concern 1: AIProjectClient lacks ARM coordinates to construct MLClient

`AIProjectClient` is a data-plane client initialized with just an endpoint + credential:

```python
AIProjectClient(endpoint="https://acct.services.ai.azure.com/api/projects/proj", credential=cred)
```

Constructing an `MLClient` for the registry requires `subscription_id`, `resource_group_name`, and `registry_name`. The `AIProjectClient` does not have these. Either the user passes them in (defeats the convenience purpose) or a discovery API is needed (adds latency + new dependency).

## Concern 2: N+1 network calls across two services

The method must:

1. `GET /models/{name}` — fetch custom model to read `base_model` (1 call, Foundry)
2. Parse base model URI → `ml_client.models.get()` — fetch base model to read `allowed_deployment_templates` (1 call, ML Registry)
3. `ml_client.deployment_templates.get()` **for each template** (N calls, ML Registry)

For a model with 3 allowed templates, that's **5 sequential network calls across 2 different services**. No way to batch the DT fetches. Latency compounds.

## Concern 3: Opaque error surface

Errors from the inner `MLClient` calls surface through an `AIProjectClient` method. The user sees:

```
HttpResponseError: (UserError) Model 'gpt-oss-120B' not found in registry 'azureml-openai-oss'
```

...from a call on `project_client.models`. Confusing — which service failed? The user didn't invoke any registry API directly. Wrapping these errors cleanly adds implementation complexity.

## Concern 4: azure-ai-ml becomes a dependency of azure-ai-projects

The convenience method imports `MLClient`, `DeploymentTemplate`, `AcceleratorMap`, etc. from `azure-ai-ml`. Three options:

| Option | Pros | Cons |
|---|---|---|
| **Hard dep** in `pyproject.toml` | Always works, no surprise errors | `azure-ai-ml` is ~50MB. Every `azure-ai-projects` user pays the install cost even if they never call this one method. Adds transitive deps (`msrest`, `azure-mgmt-core`, etc.) |
| **Optional/lazy import** at call time | No install bloat; users opt in with `pip install azure-ai-ml` | Runtime `ImportError` with no clear guidance unless we add a custom error message. Testing matrix grows (with/without installed) |
| **Extras group** `pip install azure-ai-projects[ml]` | Explicit opt-in, discoverable via docs | Packaging complexity; users must know to install the extra; `pip install azure-ai-projects` alone gives a confusing failure at runtime |

**Best option if we proceed:** Lazy import with a clear error message:

```python
def get_deployment_templates(self, model_name, **kwargs):
    try:
        from azure.ai.ml import MLClient
    except ImportError:
        raise ImportError(
            "azure-ai-ml is required for get_deployment_templates(). "
            "Install it with: pip install azure-ai-ml"
        )
    ...
```

Combined with an extras group so `pip install azure-ai-projects[ml]` pulls it automatically. This avoids bloating the base install while keeping the failure mode explicit.

## Concern 5: Breaking change coupling between packages

If `azure-ai-ml` changes entity shapes (e.g., PR #45895 renames `DefaultDeploymentTemplate` → `DeploymentTemplateReference`), the convenience method in `azure-ai-projects` breaks. The two packages release independently — this creates a fragile version-lock requirement.

---

## Recommendation

**Push resolution server-side.** Add a new data-plane API:

```http
GET /models/{modelName}/deploymentTemplates?api-version=2025-06-01-preview
```

The Foundry service resolves `base_model` → registry → allowed DTs → accelerator maps internally. Benefits:

- Single call, no URI parsing on the client
- No `MLClient` construction needed inside `AIProjectClient`
- Server can cache/optimize registry lookups
- Error messages come from one service with clear context
- No cross-package type coupling

Until the server-side API exists, document the manual bridge (user calls `MLClient` directly) as the supported path rather than hiding it behind a leaky convenience method.
