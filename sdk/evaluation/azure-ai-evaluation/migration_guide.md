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

[performance_and_quality_evaluators]: https://learn.microsoft.com/azure/ai-studio/how-to/develop/evaluate-sdk#performance-and-quality-evaluators
[risk_and_safety_evaluators]: https://learn.microsoft.com/en-us/azure/ai-studio/how-to/develop/evaluate-sdk#risk-and-safety-evaluators-preview
[composite_evaluators]: https://learn.microsoft.com/azure/ai-studio/how-to/develop/evaluate-sdk#composite-evaluators