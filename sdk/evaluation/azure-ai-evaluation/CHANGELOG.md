# Release History


## 1.0.0b5 (Unreleased)

### Features Added

### Breaking Changes
- Renamed environment variable `PF_EVALS_BATCH_USE_ASYNC` to `AI_EVALS_BATCH_USE_ASYNC`.

### Bugs Fixed
- Non adversarial simulator works with `gpt-4o` models using the `json_schema` response format

### Other Changes
- Improved error messages for the `evaluate` API by enhancing the validation of input parameters. This update provides more detailed and actionable error descriptions.

## 1.0.0b4 (2024-10-16)

### Breaking Changes

- Removed `numpy` dependency. All NaN values returned by the SDK have been changed to from `numpy.nan` to `math.nan`.
- `credential` is now required to be passed in for all content safety evaluators and `ProtectedMaterialsEvaluator`. `DefaultAzureCredential` will no longer be chosen if a credential is not passed.
- Changed package extra name from "pf-azure" to "remote".

### Bugs Fixed
- Adversarial Conversation simulations would fail with `Forbidden`. Added logic to re-fetch token in the exponential retry logic to retrive RAI Service response.
- Fixed an issue where the Evaluate API did not fail due to missing inputs when the target did not return columns required by the evaluators.

### Other Changes
- Enhance the error message to provide clearer instruction when required packages for the remote tracking feature are missing.
- Print the per-evaluator run summary at the end of the Evaluate API call to make troubleshooting row-level failures easier.

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

- Simulator now requires a model configuration to call the prompty instead of an Azure AI project scope. This enables the usage of simulator with Entra ID based auth.
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
If `api_key` is not included in the `model_config`, the prompty runtime in `promptflow-core` will pick up `DefaultAzureCredential`.

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
