# Azure AI Evaluation client library for Python

Use Azure AI Evaluation SDK to assess the performance of your generative AI applications. Generative AI application generations are quantitatively measured with mathematical based metrics, AI-assisted quality and safety metrics. Metrics are defined as `evaluators`. Built-in or custom evaluators can provide comprehensive insights into the application's capabilities and limitations.

Use Azure AI Evaluation SDK to:
- Evaluate existing data from generative AI applications
- Evaluate generative AI applications
- Evaluate by generating mathematical, AI-assisted quality and safety metrics

Azure AI SDK provides following to evaluate Generative AI Applications:
- [Evaluators][evaluators] - Generate scores individually or when used together with `evaluate` API.
- [Evaluate API][evaluate_api] - Python API to evaluate dataset or application using built-in or custom evaluators.

[Source code][source_code]
| [Package (PyPI)][evaluation_pypi]
| [API reference documentation][evaluation_ref_docs]
| [Product documentation][product_documentation]
| [Samples][evaluation_samples]


## Getting started

### Prerequisites

- Python 3.9 or later is required to use this package.
- [Optional] You must have [Azure AI Foundry Project][ai_project] or [Azure Open AI][azure_openai] to use AI-assisted evaluators

### Install the package

Install the Azure AI Evaluation SDK for Python with [pip][pip_link]:

```bash
pip install azure-ai-evaluation
```

## Key concepts

### Evaluators

Evaluators are custom or prebuilt classes or functions that are designed to measure the quality of the outputs from language models or generative AI applications.

#### Built-in evaluators

Built-in evaluators are out of box evaluators provided by Microsoft:
| Category  | Evaluator class                                                                                                                    |
|-----------|------------------------------------------------------------------------------------------------------------------------------------|
| [Performance and quality][performance_and_quality_evaluators] (AI-assisted)  | `GroundednessEvaluator`, `RelevanceEvaluator`, `CoherenceEvaluator`, `FluencyEvaluator`, `SimilarityEvaluator`, `RetrievalEvaluator` |
| [Performance and quality][performance_and_quality_evaluators] (NLP)  | `F1ScoreEvaluator`, `RougeScoreEvaluator`, `GleuScoreEvaluator`, `BleuScoreEvaluator`, `MeteorScoreEvaluator`|
| [Risk and safety][risk_and_safety_evaluators] (AI-assisted)    | `ViolenceEvaluator`, `SexualEvaluator`, `SelfHarmEvaluator`, `HateUnfairnessEvaluator`, `IndirectAttackEvaluator`, `ProtectedMaterialEvaluator`                                             |
| [Composite][composite_evaluators] | `QAEvaluator`, `ContentSafetyEvaluator`                                             |

For more in-depth information on each evaluator definition and how it's calculated, see [Evaluation and monitoring metrics for generative AI][evaluation_metrics].

```python
import os

from azure.ai.evaluation import evaluate, RelevanceEvaluator, ViolenceEvaluator, BleuScoreEvaluator

# NLP bleu score evaluator
bleu_score_evaluator = BleuScoreEvaluator()
result = bleu_score(
    response="Tokyo is the capital of Japan.",
    ground_truth="The capital of Japan is Tokyo."
)

# AI assisted quality evaluator
model_config = {
    "azure_endpoint": os.environ.get("AZURE_OPENAI_ENDPOINT"),
    "api_key": os.environ.get("AZURE_OPENAI_API_KEY"),
    "azure_deployment": os.environ.get("AZURE_OPENAI_DEPLOYMENT"),
}

relevance_evaluator = RelevanceEvaluator(model_config)
result = relevance_evaluator(
    query="What is the capital of Japan?",
    response="The capital of Japan is Tokyo."
)

# There are two ways to provide Azure AI Project.
# Option #1 : Using Azure AI Project Details 
azure_ai_project = {
    "subscription_id": "<subscription_id>",
    "resource_group_name": "<resource_group_name>",
    "project_name": "<project_name>",
}

violence_evaluator = ViolenceEvaluator(azure_ai_project)
result = violence_evaluator(
    query="What is the capital of France?",
    response="Paris."
)

# Option # 2 : Using Azure AI Project Url 
azure_ai_project = "https://{resource_name}.services.ai.azure.com/api/projects/{project_name}"

violence_evaluator = ViolenceEvaluator(azure_ai_project)
result = violence_evaluator(
    query="What is the capital of France?",
    response="Paris."
)
```

#### Custom evaluators

Built-in evaluators are great out of the box to start evaluating your application's generations. However you can build your own code-based or prompt-based evaluator to cater to your specific evaluation needs.

```python

# Custom evaluator as a function to calculate response length
def response_length(response, **kwargs):
    return len(response)

# Custom class based evaluator to check for blocked words
class BlocklistEvaluator:
    def __init__(self, blocklist):
        self._blocklist = blocklist

    def __call__(self, *, response: str, **kwargs):
        score = any([word in answer for word in self._blocklist])
        return {"score": score}

blocklist_evaluator = BlocklistEvaluator(blocklist=["bad, worst, terrible"])

result = response_length("The capital of Japan is Tokyo.")
result = blocklist_evaluator(answer="The capital of Japan is Tokyo.")

```

### Evaluate API
The package provides an `evaluate` API which can be used to run multiple evaluators together to evaluate generative AI application response.

#### Evaluate existing dataset

```python
from azure.ai.evaluation import evaluate

result = evaluate(
    data="data.jsonl", # provide your data here
    evaluators={
        "blocklist": blocklist_evaluator,
        "relevance": relevance_evaluator
    },
    # column mapping
    evaluator_config={
        "relevance": {
            "column_mapping": {
                "query": "${data.queries}"
                "ground_truth": "${data.ground_truth}"
                "response": "${outputs.response}"
            } 
        }
    }
    # Optionally provide your AI Foundry project information to track your evaluation results in your Azure AI Foundry project
    azure_ai_project = azure_ai_project,
    # Optionally provide an output path to dump a json of metric summary, row level data and metric and AI Foundry URL
    output_path="./evaluation_results.json"
)
```
For more details refer to [Evaluate on test dataset using evaluate()][evaluate_dataset]

#### Evaluate generative AI application
```python
from askwiki import askwiki

result = evaluate(
    data="data.jsonl",
    target=askwiki,
    evaluators={
        "relevance": relevance_eval
    },
    evaluator_config={
        "default": {
            "column_mapping": {
                "query": "${data.queries}"
                "context": "${outputs.context}"
                "response": "${outputs.response}"
            } 
        }
    }
)
```
Above code snippet refers to askwiki application in this [sample][evaluate_app].

For more details refer to [Evaluate on a target][evaluate_target]

### Simulator


Simulators allow users to generate synthentic data using their application. Simulator expects the user to have a callback method that invokes their AI application. The intergration between your AI application and the simulator happens at the callback method. Here's how a sample callback would look like:


```python
async def callback(
    messages: Dict[str, List[Dict]],
    stream: bool = False,
    session_state: Any = None,
    context: Optional[Dict[str, Any]] = None,
) -> dict:
    messages_list = messages["messages"]
    # Get the last message from the user
    latest_message = messages_list[-1]
    query = latest_message["content"]
    # Call your endpoint or AI application here
    # response should be a string
    response = call_to_your_application(query, messages_list, context)
    formatted_response = {
        "content": response,
        "role": "assistant",
        "context": "",
    }
    messages["messages"].append(formatted_response)
    return {"messages": messages["messages"], "stream": stream, "session_state": session_state, "context": context}
```

The simulator initialization and invocation looks like this:
```python
from azure.ai.evaluation.simulator import Simulator
model_config = {
    "azure_endpoint": os.environ.get("AZURE_ENDPOINT"),
    "azure_deployment": os.environ.get("AZURE_DEPLOYMENT_NAME"),
    "api_version": os.environ.get("AZURE_API_VERSION"),
}
custom_simulator = Simulator(model_config=model_config)
outputs = asyncio.run(custom_simulator(
    target=callback,
    conversation_turns=[
        [
            "What should I know about the public gardens in the US?",
        ],
        [
            "How do I simulate data against LLMs",
        ],
    ],
    max_conversation_turns=2,
))
with open("simulator_output.jsonl", "w") as f:
    for output in outputs:
        f.write(output.to_eval_qr_json_lines())
```

#### Adversarial Simulator

```python
from azure.ai.evaluation.simulator import AdversarialSimulator, AdversarialScenario
from azure.identity import DefaultAzureCredential

# There are two ways to provide Azure AI Project.
# Option #1 : Using Azure AI Project 
azure_ai_project = {
    "subscription_id": <subscription_id>,
    "resource_group_name": <resource_group_name>,
    "project_name": <project_name>
}

# Option #2 : Using Azure AI Project Url 
azure_ai_project = "https://{resource_name}.services.ai.azure.com/api/projects/{project_name}"

scenario = AdversarialScenario.ADVERSARIAL_QA
simulator = AdversarialSimulator(azure_ai_project=azure_ai_project, credential=DefaultAzureCredential())

outputs = asyncio.run(
    simulator(
        scenario=scenario,
        max_conversation_turns=1,
        max_simulation_results=3,
        target=callback
    )
)

print(outputs.to_eval_qr_json_lines())
```

For more details about the simulator, visit the following links:
- [Adversarial Simulation docs][adversarial_simulation_docs]
- [Adversarial scenarios][adversarial_simulation_scenarios]
- [Simulating jailbreak attacks][adversarial_jailbreak]

## Examples

In following section you will find examples of:
- [Evaluate an application][evaluate_app]
- [Evaluate different models][evaluate_models]
- [Custom Evaluators][custom_evaluators]
- [Adversarial Simulation][adversarial_simulation]
- [Simulate with conversation starter][simulate_with_conversation_starter]

More examples can be found [here][evaluate_samples].

## Troubleshooting

### General

Please refer to [troubleshooting][evaluation_tsg] for common issues.

### Logging

This library uses the standard
[logging][python_logging] library for logging.
Basic information about HTTP sessions (URLs, headers, etc.) is logged at INFO
level.

Detailed DEBUG level logging, including request/response bodies and unredacted
headers, can be enabled on a client with the `logging_enable` argument.

See full SDK logging documentation with examples [here][sdk_logging_docs].

## Next steps

- View our [samples][evaluation_samples].
- View our [documentation][product_documentation]

## Contributing

This project welcomes contributions and suggestions. Most contributions require you to agree to a Contributor License Agreement (CLA) declaring that you have the right to, and actually do, grant us the rights to use your contribution. For details, visit [cla.microsoft.com][cla].

When you submit a pull request, a CLA-bot will automatically determine whether you need to provide a CLA and decorate the PR appropriately (e.g., label, comment). Simply follow the instructions provided by the bot. You will only need to do this once across all repos using our CLA.

This project has adopted the [Microsoft Open Source Code of Conduct][code_of_conduct]. For more information see the [Code of Conduct FAQ][coc_faq] or contact [opencode@microsoft.com][coc_contact] with any additional questions or comments.

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
