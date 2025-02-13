# Migration Guide - From Promptflow Eval SDK To Azure AI Evaluation SDK



Github: [link](https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/evaluation/azure-ai-evaluation)
Pypi: [link](https://pypi.org/project/azure-ai-evaluation/)
Documentation: [link](https://learn.microsoft.com/en-us/azure/ai-studio/how-to/develop/evaluate-sdk)

Following Built-in evaluators are provided in new Azure AI Evaluation SDK ([azure-ai-evaluation](https://pypi.org/project/azure-ai-evaluation/)).

#### Built-in evaluators

| Category  | Evaluator class|
|-----------------------------|------------------------------------------|
| [Performance and quality][performance_and_quality_evaluators] (AI-assisted)  | `GroundednessEvaluator`, `RelevanceEvaluator`, `CoherenceEvaluator`, `FluencyEvaluator`, `SimilarityEvaluator`, `RetrievalEvaluator` |
| [Performance and quality][performance_and_quality_evaluators] (NLP)  | `F1ScoreEvaluator`, `RougeScoreEvaluator`, `GleuScoreEvaluator`, `BleuScoreEvaluator`, `MeteorScoreEvaluator`|
| [Risk and safety][risk_and_safety_evaluators] (AI-assisted)    | `ViolenceEvaluator`, `SexualEvaluator`, `SelfHarmEvaluator`, `HateUnfairnessEvaluator`, `IndirectAttackEvaluator`, `ProtectedMaterialEvaluator`                                             |
| [Composite][composite_evaluators] | `QAEvaluator`, `ContentSafetyEvaluator`



### Difference b/w promptflow-eval package and azure-ai-evaluation package. 

| SDK  |Import statements                                                                                                              |
|-----------|------------------------------------------------------------------------------------------------------------------------------------|
| promptflow-eval | `from promptflow.evals.evaluators import ContentSafetyEvaluator` |
| azure-ai-evaluation   | `from azure.ai.evaluation import ContentSafetyEvaluator` |

**Note**: `ViolenceEvaluator, SexualEvaluator, SelfHarmEvaluator, HateUnfairnessEvaluator, IndirectAttackEvaluator, ProtectedMaterialEvaluator` follows the same pattern.

`ChatEvaluator` and `ContentSafetyChatEvaluator` has been removed. 
However, multi-turn chat capabilities is added in ContentSafetyEvaluator. Please take a look at below sample code. 




##### Promptflow Evals SDK

```python
from promptflow.evals.evaluators.content_safety import ContentSafetyEvaluator, ContentSafetyChatEvaluator
from pprint import pprint

project_scope = {
    "subscription_id": "",
    "resource_group_name": "",
    "project_name": "",
}

content_safety_eval = ContentSafetyEvaluator(project_scope)
content_safety_score = content_safety_eval(
    question="What is the capital of France?", 
    answer="Paris."
)
pprint(content_safety_score)

content_safety_chat_eval = ContentSafetyChatEvaluator(project_scope)
conversation = [
        {
            "role": "user", 
            "content": "What is the capital of France?"
        },
        {
            "role": "assistant",
            "content": "The capital of France is Paris.",
        },
    ]
content_safety_chat_score = content_safety_chat_eval(conversation=conversation)
pprint(content_safety_chat_score)
```

##### Azure AI Evaluation SDK
```python
from azure.identity import DefaultAzureCredential
from azure.ai.evaluation import ContentSafetyEvaluator
from pprint import pprint

azure_cred = DefaultAzureCredential()
project_scope = {
    "subscription_id": "<your-subscription-id>",
    "resource_group_name": "<your-resource-group>",
    "project_name": "<your-project-name>",
}
content_safety_eval = ContentSafetyEvaluator(azure_cred, project_scope)
content_safety_score = content_safety_eval(
    query="What is the capital of Japan?",
    response="The capital of Japan is Tokyo."
pprint(content_safety_score)

# Using Chat conversation
conversation = {
    "messages": [
        {
            "content": "What is the capital of France?",
            "role": "user",
        },
        {
            "content": "Paris", 
            "role": "assistant", 
        }
    ],
}
content_safety_score = content_safety_eval(conversation=conversation)
pprint(content_safety_score)

```
### Using Evaluate API

| SDK  |Statements                                                                                                              |
|-----------|------------------------------------------------------------------------------------------------------------------------------------|
| promptflow-eval | ``from promptflow.evals.evaluate import evaluate`` |
| azure-ai-evaluation   | ``from azure.ai.evaluation import evaluate`` |


##### Promptflow Evals SDK

```python
from promptflow.evals.evaluators.content_safety import ContentSafetyEvaluator, ContentSafetyChatEvaluator
from pprint import pprint
import pathlib

project_scope = {
    "subscription_id": "",
    "resource_group_name": "",
    "project_name": "",
}

content_safety_eval = ContentSafetyEvaluator(project_scope)

# Using Evaluate API

file_path = pathlib.Path("data.jsonl")
result = evaluate(
    data=file_path,
    azure_ai_project=project_scope,
    evaluators={"content_safety": content_safety_eval},
)
pprint(result)
```

##### Azure AI Evaluation SDK
```python
from azure.identity import DefaultAzureCredential
from azure.ai.evaluation import ContentSafetyEvaluator
import pathlib
from pprint import pprint


azure_cred = DefaultAzureCredential()
project_scope = {
    "subscription_id": "<your-subscription-id>",
    "resource_group_name": "<your-resource-group>",
    "project_name": "<your-project-name>",
}
content_safety_eval = ContentSafetyEvaluator(azure_cred, project_scope)

# Using Evaluate API

file_path = pathlib.Path("data.jsonl")
result = evaluate(
    data=file_path,
    azure_ai_project=project_scope,
    evaluators={"content_safety": content_safety_eval},
)
pprint(result)
```





<!-- LINKS -->

[source_code]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/evaluation/azure-ai-evaluation
[evaluation_pypi]: https://pypi.org/project/azure-ai-evaluation/
[evaluation_ref_docs]: https://learn.microsoft.com/python/api/azure-ai-evaluation/azure.ai.evaluation?view=azure-python-preview
[evaluation_samples]: https://github.com/Azure-Samples/azureai-samples/tree/main/scenarios
[product_documentation]: https://learn.microsoft.com/azure/ai-studio/how-to/develop/evaluate-sdk
[python_logging]: https://docs.python.org/3/library/logging.html
[sdk_logging_docs]: https://docs.microsoft.com/azure/developer/python/azure-sdk-logging
[azure_core_readme]: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/core/azure-core/README.md
[pip_link]: https://pypi.org/project/pip/
[azure_core_ref_docs]: https://aka.ms/azsdk-python-core-policies
[azure_core]: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/core/azure-core/README.md
[azure_identity]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/identity/azure-identity
[cla]: https://cla.microsoft.com
[code_of_conduct]: https://opensource.microsoft.com/codeofconduct/
[coc_faq]: https://opensource.microsoft.com/codeofconduct/faq/
[coc_contact]: mailto:opencode@microsoft.com
[evaluate_target]: https://learn.microsoft.com/azure/ai-studio/how-to/develop/evaluate-sdk#evaluate-on-a-target
[evaluate_dataset]: https://learn.microsoft.com/azure/ai-studio/how-to/develop/evaluate-sdk#evaluate-on-test-dataset-using-evaluate
[evaluators]: https://learn.microsoft.com/python/api/azure-ai-evaluation/azure.ai.evaluation?view=azure-python-preview
[evaluate_api]: https://learn.microsoft.com/python/api/azure-ai-evaluation/azure.ai.evaluation?view=azure-python-preview#azure-ai-evaluation-evaluate
[evaluate_app]: https://github.com/Azure-Samples/azureai-samples/tree/main/scenarios/evaluate/Supported_Evaluation_Targets/Evaluate_App_Endpoint
[evaluation_tsg]: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/evaluation/azure-ai-evaluation/TROUBLESHOOTING.md
[ai_studio]: https://learn.microsoft.com/azure/ai-studio/what-is-ai-studio
[ai_project]: https://learn.microsoft.com/azure/ai-studio/how-to/create-projects?tabs=ai-studio
[azure_openai]: https://learn.microsoft.com/azure/ai-services/openai/
[evaluate_models]: https://github.com/Azure-Samples/azureai-samples/tree/main/scenarios/evaluate/Supported_Evaluation_Targets/Evaluate_Base_Model_Endpoint
[custom_evaluators]: https://github.com/Azure-Samples/azureai-samples/tree/main/scenarios/evaluate/Supported_Evaluation_Metrics/Custom_Evaluators
[evaluate_samples]: https://github.com/Azure-Samples/azureai-samples/tree/main/scenarios/evaluate
[evaluation_metrics]: https://learn.microsoft.com/azure/ai-studio/concepts/evaluation-metrics-built-in
[performance_and_quality_evaluators]: https://learn.microsoft.com/azure/ai-studio/how-to/develop/evaluate-sdk#performance-and-quality-evaluators
[risk_and_safety_evaluators]: https://learn.microsoft.com/azure/ai-studio/how-to/develop/evaluate-sdk#risk-and-safety-evaluators
[composite_evaluators]: https://learn.microsoft.com/azure/ai-studio/how-to/develop/evaluate-sdk#composite-evaluators
[adversarial_simulation_docs]: https://learn.microsoft.com/azure/ai-studio/how-to/develop/simulator-interaction-data#generate-adversarial-simulations-for-safety-evaluation
[adversarial_simulation_scenarios]: https://learn.microsoft.com/azure/ai-studio/how-to/develop/simulator-interaction-data#supported-adversarial-simulation-scenarios
[adversarial_simulation]: https://github.com/Azure-Samples/azureai-samples/tree/main/scenarios/evaluate/Simulators/Simulate_Adversarial_Data
[simulate_with_conversation_starter]: https://github.com/Azure-Samples/azureai-samples/tree/main/scenarios/evaluate/Simulators/Simulate_Context-Relevant_Data/Simulate_From_Conversation_Starter
[adversarial_jailbreak]: https://learn.microsoft.com/azure/ai-studio/how-to/develop/simulator-interaction-data#simulating-jailbreak-attacks