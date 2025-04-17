# Release History

## 1.6.0 (Unreleased)

### Features Added
- New `<evaluator>.binary_aggregate` field added to evaluation result metrics. This field contains the aggregated binary evaluation results for each evaluator, providing a summary of the evaluation outcomes.

### Breaking Changes

### Bugs Fixed

### Other Changes

## 1.5.0 (2025-04-04)

### Features Added

- New `RedTeam` agent functionality to assess the safety and resilience of AI systems against adversarial prompt attacks

## 1.4.0 (2025-03-27)

### Features Added
- Enhanced binary evaluation results with customizable thresholds
  - Added threshold support for QA and ContentSafety evaluators
  - Evaluation results now include both the score and threshold values
  - Configurable threshold parameter allows custom binary classification boundaries
  - Default thresholds provided for backward compatibility
  - Quality evaluators use "higher is better" scoring (score ≥ threshold is positive)
  - Content safety evaluators use "lower is better" scoring (score ≤ threshold is positive)
- New Built-in evaluator called CodeVulnerabilityEvaluator is added. 
  - It provides capabilities to identify the following code vulnerabilities.
    - path-injection
    - sql-injection
    - code-injection
    - stack-trace-exposure
    - incomplete-url-substring-sanitization
    - flask-debug
    - clear-text-logging-sensitive-data
    - incomplete-hostname-regexp
    - server-side-unvalidated-url-redirection
    - weak-cryptographic-algorithm
    - full-ssrf
    - bind-socket-all-network-interfaces
    - client-side-unvalidated-url-redirection
    - likely-bugs
    - reflected-xss
    - clear-text-storage-sensitive-data
    - tarslip
    - hardcoded-credentials
    - insecure-randomness
  - It also supports multiple coding languages such as (Python, Java, C++, C#, Go, Javascript, SQL)
  
- New Built-in evaluator called UngroundedAttributesEvaluator is added.
  - It evaluates ungrounded inference of human attributes for a given query, response, and context for a single-turn evaluation only, 
  - where query represents the user query and response represents the AI system response given the provided context. 
 
  - Ungrounded Attributes checks for whether a response is first, ungrounded, and checks if it contains information about protected class 
  - or emotional state of a person.
  
  - It identifies the following attributes:
    
    - emotional_state
    - protected_class
    - groundedness
- New Built-in evaluators for Agent Evaluation (Preview)
  - IntentResolutionEvaluator - Evaluates the intent resolution of an agent's response to a user query.
  - ResponseCompletenessEvaluator - Evaluates the response completeness of an agent's response to a user query.
  - TaskAdherenceEvaluator - Evaluates the task adherence of an agent's response to a user query.
  - ToolCallAccuracyEvaluator - Evaluates the accuracy of tool calls made by an agent in response to a user query.

### Bugs Fixed
- Fixed error in `GroundednessProEvaluator` when handling non-numeric values like "n/a" returned from the service.
- Uploading local evaluation results from `evaluate` with the same run name will no longer result in each online run sharing (and bashing) result files.

## 1.3.0 (2025-02-28)

### Breaking Changes
- Multimodal specific evaluators `ContentSafetyMultimodalEvaluator`, `ViolenceMultimodalEvaluator`, `SexualMultimodalEvaluator`, `SelfHarmMultimodalEvaluator`, `HateUnfairnessMultimodalEvaluator` and `ProtectedMaterialMultimodalEvaluator` has been removed. Please use `ContentSafetyEvaluator`, `ViolenceEvaluator`, `SexualEvaluator`, `SelfHarmEvaluator`, `HateUnfairnessEvaluator` and `ProtectedMaterialEvaluator` instead.
- Metric name in ProtectedMaterialEvaluator's output is changed from `protected_material.fictional_characters_label` to `protected_material.fictional_characters_defect_rate`. It's now consistent with other evaluator's metric names (ending with `_defect_rate`).

## 1.2.0 (2025-01-27)

### Features Added
- CSV files are now supported as data file inputs with `evaluate()` API. The CSV file should have a header row with column names that match the `data` and `target` fields in the `evaluate()` method and the filename should be passed as the `data` parameter. Column name 'Conversation' in CSV file is not fully supported yet.  

### Breaking Changes
- `ViolenceMultimodalEvaluator`, `SexualMultimodalEvaluator`, `SelfHarmMultimodalEvaluator`, `HateUnfairnessMultimodalEvaluator` and `ProtectedMaterialMultimodalEvaluator` will be removed in next release. 

### Bugs Fixed
- Removed `[remote]` extra. This is no longer needed when tracking results in Azure AI Studio.
- Fixed `AttributeError: 'NoneType' object has no attribute 'get'` while running simulator with 1000+ results
- Fixed the non adversarial simulator to run in task-free mode
- Content safety evaluators (violence, self harm, sexual, hate/unfairness) return the maximum result as the
  main score when aggregating per-turn evaluations from a conversation into an overall
  evaluation score. Other conversation-capable evaluators still default to a mean for aggregation.
- Fixed bug in non adversarial simulator sample where `tasks` undefined

### Other Changes
- Changed minimum required python version to use this package from 3.8 to 3.9
- Stop dependency on the local promptflow service. No promptflow service will automatically start when running evaluation.
- Evaluators internally allow for custom aggregation. However, this causes serialization failures if evaluated while the
  environment variable `AI_EVALS_BATCH_USE_ASYNC` is set to false.

## 1.1.0 (2024-12-12)

### Features Added
- Added image support in `ContentSafetyEvaluator`, `ViolenceEvaluator`, `SexualEvaluator`, `SelfHarmEvaluator`, `HateUnfairnessEvaluator` and `ProtectedMaterialEvaluator`. Provide image URLs or base64 encoded images in `conversation` input for image evaluation. See below for an example:

```python
evaluator = ContentSafetyEvaluator(credential=azure_cred, azure_ai_project=project_scope)
conversation = {
    "messages": [
        {
            "role": "system",
            "content": [
                {"type": "text", "text": "You are an AI assistant that understands images."}
            ],
        },
        {
            "role": "user",
            "content": [
                {"type": "text", "text": "Can you describe this image?"},
                {
                    "type": "image_url",
                    "image_url": {
                        "url": "https://cdn.britannica.com/68/178268-050-5B4E7FB6/Tom-Cruise-2013.jpg"
                    },
                },
            ],
        },
        {
            "role": "assistant",
            "content": [
                {
                    "type": "text",
                    "text": "The image shows a man with short brown hair smiling, wearing a dark-colored shirt.",
                }
            ],
        },
    ]
}
print("Calling Content Safety Evaluator for multi-modal")
score = evaluator(conversation=conversation)
```

- Please switch to generic evaluators for image evaluations as mentioned above. `ContentSafetyMultimodalEvaluator`, `ContentSafetyMultimodalEvaluatorBase`, `ViolenceMultimodalEvaluator`, `SexualMultimodalEvaluator`, `SelfHarmMultimodalEvaluator`, `HateUnfairnessMultimodalEvaluator` and `ProtectedMaterialMultimodalEvaluator` will be deprecated in the next release.

### Bugs Fixed
- Removed `[remote]` extra. This is no longer needed when tracking results in Azure AI Foundry portal.
- Fixed `AttributeError: 'NoneType' object has no attribute 'get'` while running simulator with 1000+ results

## 1.0.1 (2024-11-15)

### Bugs Fixed
- Removing `azure-ai-inference` as dependency.
- Fixed `AttributeError: 'NoneType' object has no attribute 'get'` while running simulator with 1000+ results

## 1.0.0 (2024-11-13)

### Breaking Changes
- The `parallel` parameter has been removed from composite evaluators: `QAEvaluator`, `ContentSafetyChatEvaluator`, and `ContentSafetyMultimodalEvaluator`. To control evaluator parallelism, you can now use the `_parallel` keyword argument, though please note that this private parameter may change in the future.
- Parameters `query_response_generating_prompty_kwargs` and `user_simulator_prompty_kwargs` have been renamed to `query_response_generating_prompty_options` and `user_simulator_prompty_options` in the Simulator's __call__ method.

### Bugs Fixed
- Fixed an issue where the `output_path` parameter in the `evaluate` API did not support relative path.
- Output of adversarial simulators are of type `JsonLineList` and the helper function `to_eval_qr_json_lines` now outputs context from both user and assistant turns along with `category` if it exists in the conversation
- Fixed an issue where during long-running simulations, API token expires causing "Forbidden" error. Instead, users can now set an environment variable `AZURE_TOKEN_REFRESH_INTERVAL` to refresh the token more frequently to prevent expiration and ensure continuous operation of the simulation.
- Fixed an issue with the `ContentSafetyEvaluator` that caused parallel execution of sub-evaluators to fail. Parallel execution is now enabled by default again, but can still be disabled via the '_parallel' boolean keyword argument during class initialization.
- Fix `evaluate` function not producing aggregated metrics if ANY values to be aggregated were None, NaN, or
otherwise difficult to process. Such values are ignored fully, so the aggregated metric of `[1, 2, 3, NaN]`
would be 2, not 1.5.

### Other Changes
- Refined error messages for serviced-based evaluators and simulators.
- Tracing has been disabled due to Cosmos DB initialization issue.
- Introduced environment variable `AI_EVALS_DISABLE_EXPERIMENTAL_WARNING` to disable the warning message for experimental features.
- Changed the randomization pattern for `AdversarialSimulator` such that there is an almost equal number of Adversarial harm categories (e.g. Hate + Unfairness, Self-Harm, Violence, Sex) represented in the  `AdversarialSimulator` outputs. Previously, for 200 `max_simulation_results` a user might see 140 results belonging to the 'Hate + Unfairness' category and 40 results belonging to the 'Self-Harm' category. Now, user will see 50 results for each of Hate + Unfairness, Self-Harm, Violence, and Sex.
- For the `DirectAttackSimulator`, the prompt templates used to generate simulated outputs for each Adversarial harm category will no longer be in a randomized order by default. To override this behavior, pass `randomize_order=True` when you call the `DirectAttackSimulator`, for example:
```python
adversarial_simulator = DirectAttackSimulator(azure_ai_project=azure_ai_project, credential=DefaultAzureCredential())
outputs = asyncio.run(
    adversarial_simulator(
        scenario=scenario,
        target=callback,
        randomize_order=True
    )
)
```

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

    | Evaluator | New `max_token` for Generation |
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
