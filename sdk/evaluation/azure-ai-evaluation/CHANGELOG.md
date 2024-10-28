# Release History

## 1.0.0b5 (2024-10-28)

### Features Added
- Added `GroundednessProEvaluator`, which is a service-based evaluator for determining response groundedness.
- Groundedness detection in Non Adversarial Simulator via query/context pairs
```python
import importlib.resources as pkg_resources
package = "azure.ai.evaluation.simulator._data_sources"
resource_name = "grounding.json"
custom_simulator = Simulator(model_config=model_config)
conversation_turns = []
with pkg_resources.path(package, resource_name) as grounding_file:
    with open(grounding_file, "r") as file:
        data = json.load(file)
for item in data:
    conversation_turns.append([item])
outputs = asyncio.run(custom_simulator(
    target=callback,
    conversation_turns=conversation_turns,
    max_conversation_turns=1,
))
```
- Adding evaluator for multimodal use cases

### Breaking Changes
- Renamed environment variable `PF_EVALS_BATCH_USE_ASYNC` to `AI_EVALS_BATCH_USE_ASYNC`.
- `RetrievalEvaluator` now requires a `context` input in addition to `query` in single-turn evaluation.
- `RelevanceEvaluator` no longer takes `context` as an input. It now only takes `query` and `response` in single-turn evaluation.
- `FluencyEvaluator` no longer takes `query` as an input. It now only takes `response` in single-turn evaluation.
- AdversarialScenario enum does not include `ADVERSARIAL_INDIRECT_JAILBREAK`, invoking IndirectJailbreak or XPIA should be done with `IndirectAttackSimulator`
- Outputs of `Simulator` and `AdversarialSimulator` previously had `to_eval_qa_json_lines` and now has `to_eval_qr_json_lines`. Where `to_eval_qa_json_lines` had:
```json
{"question": <user_message>, "answer": <assistant_message>}
```
`to_eval_qr_json_lines` now has:
```json
{"query": <user_message>, "response": assistant_message}
```

### Bugs Fixed
- Non adversarial simulator works with `gpt-4o` models using the `json_schema` response format
- Fixed an issue where the `evaluate` API would fail with "[WinError 32] The process cannot access the file because it is being used by another process" when venv folder and target function file are in the same directory.
- Fix evaluate API failure when `trace.destination` is set to `none`
- Non adversarial simulator now accepts context from the callback

### Other Changes
- Improved error messages for the `evaluate` API by enhancing the validation of input parameters. This update provides more detailed and actionable error descriptions.
- `GroundednessEvaluator` now supports `query` as an optional input in single-turn evaluation. If `query` is provided, a different prompt template will be used for the evaluation.
- To align with our support of a diverse set of models, the following evaluators will now have a new key in their result output without the `gpt_` prefix. To maintain backwards compatibility, the old key with the `gpt_` prefix will still be present in the output; however, it is recommended to use the new key moving forward as the old key will be deprecated in the future.
  - `CoherenceEvaluator`
  - `RelevanceEvaluator`
  - `FluencyEvaluator`
  - `GroundednessEvaluator`
  - `SimilarityEvaluator`
  - `RetrievalEvaluator`
- The following evaluators will now have a new key in their result output including LLM reasoning behind the score. The new key will follow the pattern "<metric_name>_reason". The reasoning is the result of a more detailed prompt template being used to generate the LLM response. Note that this requires the maximum number of tokens used to run these evaluators to be increased.
    
    | Evaluator | New Token Limit |
    | --- | --- |
    | `CoherenceEvaluator` | 800 |
    | `RelevanceEvaluator` | 800 |
    | `FluencyEvaluator` | 800 |
    | `GroundednessEvaluator` | 800 |
    | `RetrievalEvaluator` | 1600 |
- Improved the error message for storage access permission issues to provide clearer guidance for users.

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
