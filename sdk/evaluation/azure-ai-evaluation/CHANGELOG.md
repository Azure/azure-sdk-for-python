# Release History

## 1.0.0b4 (Unreleased)

### Features Added

### Breaking Changes

- Removed `numpy` dependency. All NaN values returned by the SDK have been changed to from `numpy.nan` to `math.nan`.

### Bugs Fixed

### Other Changes

## 1.0.0b3 (2024-10-01)

### Features Added

- Added `type` field to `AzureOpenAIModelConfiguration` and `OpenAIModelConfiguration`
- The following evaluators now support `conversation` as an alternative input to their usual single-turn inputs:
  - `ViolenceEvaluator`
  - `SexualEvaluator`
  - `SelfHarmEvaluator`
  - `HateUnfairnessEvaluator`
  - `ProtectedMaterialEvaluator`
  - `IndirectAttackEvaluator`
  - `CoherenceEvaluator`
  - `RelevanceEvaluator`
  - `FluencyEvaluator`
  - `GroundednessEvaluator`
- Surfaced `RetrievalScoreEvaluator`, formally an internal part of `ChatEvaluator` as a standalone conversation-only evaluator.

### Breaking Changes

- Removed `ContentSafetyChatEvaluator` and `ChatEvaluator`
- The `evaluator_config` parameter of `evaluate` now maps in evaluator name to a dictionary `EvaluatorConfig`, which is a `TypedDict`. The
`column_mapping` between `data` or `target` and evaluator field names should now be specified inside this new dictionary:

Before:
```python
evaluate(
    ...,
    evaluator_config={
        "hate_unfairness": {
            "query": "${data.question}",
            "response": "${data.answer}",
        }
    },
    ...
)
```

After
```python
evaluate(
    ...,
    evaluator_config={
        "hate_unfairness": {
            "column_mapping": {
                "query": "${data.question}",
                "response": "${data.answer}",
             }
        }
    },
    ...
)
```

- Simulator now requires configuration to call the prompty within the `azure_ai_project`. This enables the usage of simulator with Entra ID based auth.
Before:
```python
azure_ai_project = {
    "subscription_id": os.environ.get("AZURE_SUBSCRIPTION_ID"),
    "resource_group_name": os.environ.get("RESOURCE_GROUP"),
    "project_name": os.environ.get("PROJECT_NAME"),
}
sim = Simulator(azure_ai_project=azure_ai_project, credentails=DefaultAzureCredentials())
```
After:
```python
model_config = {
    "azure_endpoint": os.environ.get("AZURE_OPENAI_ENDPOINT"),
    "azure_deployment": os.environ.get("AZURE_DEPLOYMENT"),
}
sim = Simulator(model_config=model_config)
```
If `api_key` is not included in the `model_config`, the prompty runtime in `promtpflow-core` will pick up `DefaultAzureCredential`.

### Bugs Fixed

- Fixed issue where Entra ID authentication was not working with `AzureOpenAIModelConfiguration` 

## 1.0.0b2 (2024-09-24)

### Breaking Changes

- `data` and `evaluators` are now required keywords in `evaluate`.

## 1.0.0b1 (2024-09-20)

### Breaking Changes

- The `synthetic` namespace has been renamed to `simulator`, and sub-namespaces under this module have been removed
- The `evaluate` and `evaluators` namespaces have been removed, and everything previously exposed in those modules has been added to the root namespace `azure.ai.evaluation`  
- The parameter name `project_scope` in content safety evaluators have been renamed to `azure_ai_project` for consistency with evaluate API and simulators.
- Model configurations classes are now of type `TypedDict` and are exposed in the `azure.ai.evaluation` module instead of coming from `promptflow.core`.  
- Updated the parameter names for `question` and `answer` in built-in evaluators to more generic terms: `query` and `response`.

### Features Added

- First preview
- This package is port of `promptflow-evals`. New features will be added only to this package moving forward.
- Added a `TypedDict` for `AzureAIProject` that allows for better intellisense and type checking when passing in project information
