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

- Python 3.8 or later is required to use this package.
- [Optional] You must have [Azure AI Project][ai_project] or [Azure Open AI][azure_openai] to use AI-assisted evaluators

### Install the package

Install the Azure AI Evaluation SDK for Python with [pip][pip_link]:

```bash
pip install azure-ai-evaluation
```
If you want to track results in [AI Studio][ai_studio], install `remote` extra:
```python
pip install azure-ai-evaluation[remote]
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

# AI assisted safety evaluator
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
    # Optionally provide your AI Studio project information to track your evaluation results in your Azure AI Studio project
    azure_ai_project = azure_ai_project,
    # Optionally provide an output path to dump a json of metric summary, row level data and metric and studio URL
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


Simulators allow users to generate synthentic data using their application. Simulator expects the user to have a callback method that invokes
their AI application.

#### Simulating with a Prompty

```yaml
---
name: ApplicationPrompty
description: Simulates an application
model:
  api: chat
  parameters:
    temperature: 0.0
    top_p: 1.0
    presence_penalty: 0
    frequency_penalty: 0
    response_format:
      type: text

inputs:
  conversation_history:
    type: dict

---
system:
You are a helpful assistant and you're helping with the user's query. Keep the conversation engaging and interesting.

Output with a string that continues the conversation, responding to the latest message from the user, given the conversation history:
{{ conversation_history }}

```

Query Response generaing prompty for gpt-4o with `json_schema` support
Use this file as an override.
```yaml
---
name: TaskSimulatorQueryResponseGPT4o
description: Gets queries and responses from a blob of text
model:
  api: chat
  parameters:
    temperature: 0.0
    top_p: 1.0
    presence_penalty: 0
    frequency_penalty: 0
    response_format:
      type: json_schema
      json_schema:
        name: QRJsonSchema
        schema: 
          type: object
          properties:
            items:
              type: array
              items:
                type: object
                properties:
                  q:
                    type: string
                  r:
                    type: string
                required:
                  - q
                  - r

inputs:
  text:
    type: string
  num_queries:
    type: integer


---
system:
You're an AI that helps in preparing a Question/Answer quiz from Text for "Who wants to be a millionaire" tv show
Both Questions and Answers MUST BE extracted from given Text
Frame Question in a way so that Answer is RELEVANT SHORT BITE-SIZED info from Text
RELEVANT info could be: NUMBER, DATE, STATISTIC, MONEY, NAME
A sentence should contribute multiple QnAs if it has more info in it
Answer must not be more than 5 words
Answer must be picked from Text as is
Question should be as descriptive as possible and must include as much context as possible from Text
Output must always have the provided number of QnAs
Output must be in JSON format.
Output must have {{num_queries}} objects in the format specified below. Any other count is unacceptable.
Text:
<|text_start|>
On January 24, 1984, former Apple CEO Steve Jobs introduced the first Macintosh. In late 2003, Apple had 2.06 percent of the desktop share in the United States.
Some years later, research firms IDC and Gartner reported that Apple's market share in the U.S. had increased to about 6%.
<|text_end|>
Output with 5 QnAs:
{
    "qna": [{
        "q": "When did the former Apple CEO Steve Jobs introduced the first Macintosh?",
        "r": "January 24, 1984"
    },
    {
        "q": "Who was the former Apple CEO that introduced the first Macintosh on January 24, 1984?",
        "r": "Steve Jobs"
    },
    {
        "q": "What percent of the desktop share did Apple have in the United States in late 2003?",
        "r": "2.06 percent"
    },
    {
        "q": "What were the research firms that reported on Apple's market share in the U.S.?",
        "r": "IDC and Gartner"
    },
    {
        "q": "What was the percentage increase of Apple's market share in the U.S., as reported by research firms IDC and Gartner?",
        "r": "6%"
    }]
}
Text:
<|text_start|>
{{ text }}
<|text_end|>
Output with {{ num_queries }} QnAs:
```

Application code:

```python
import json
import asyncio
from typing import Any, Dict, List, Optional
from azure.ai.evaluation.simulator import Simulator
from promptflow.client import load_flow
import os
import wikipedia

# Set up the model configuration without api_key, using DefaultAzureCredential
model_config = {
    "azure_endpoint": os.environ.get("AZURE_OPENAI_ENDPOINT"),
    "azure_deployment": os.environ.get("AZURE_DEPLOYMENT"),
    # not providing key would make the SDK pick up `DefaultAzureCredential`
    # use "api_key": "<your API key>"
    "api_version": "2024-08-01-preview" # keep this for gpt-4o
}

# Use Wikipedia to get some text for the simulation
wiki_search_term = "Leonardo da Vinci"
wiki_title = wikipedia.search(wiki_search_term)[0]
wiki_page = wikipedia.page(wiki_title)
text = wiki_page.summary[:1000]

def method_to_invoke_application_prompty(query: str, messages_list: List[Dict], context: Optional[Dict]):
    try:
        current_dir = os.path.dirname(__file__)
        prompty_path = os.path.join(current_dir, "application.prompty")
        _flow = load_flow(
            source=prompty_path,
            model=model_config,
            credential=DefaultAzureCredential()
        )
        response = _flow(
            query=query,
            context=context,
            conversation_history=messages_list
        )
        return response
    except Exception as e:
        print(f"Something went wrong invoking the prompty: {e}")
        return "something went wrong"

async def callback(
    messages: Dict[str, List[Dict]],
    stream: bool = False,
    session_state: Any = None,  # noqa: ANN401
    context: Optional[Dict[str, Any]] = None,
) -> dict:
    messages_list = messages["messages"]
    # Get the last message from the user
    latest_message = messages_list[-1]
    query = latest_message["content"]
    # Call your endpoint or AI application here
    response = method_to_invoke_application_prompty(query, messages_list, context)
    # Format the response to follow the OpenAI chat protocol format
    formatted_response = {
        "content": response,
        "role": "assistant",
        "context": "",
    }
    messages["messages"].append(formatted_response)
    return {"messages": messages["messages"], "stream": stream, "session_state": session_state, "context": context}

async def main():
    simulator = Simulator(model_config=model_config)
    current_dir = os.path.dirname(__file__)
    query_response_override_for_latest_gpt_4o = os.path.join(current_dir, "TaskSimulatorQueryResponseGPT4o.prompty")
    outputs = await simulator(
        target=callback,
        text=text,
        query_response_generating_prompty=query_response_override_for_latest_gpt_4o, # use this only with latest gpt-4o
        num_queries=2,
        max_conversation_turns=1,
        user_persona=[
            f"I am a student and I want to learn more about {wiki_search_term}",
            f"I am a teacher and I want to teach my students about {wiki_search_term}"
        ],
    )
    print(json.dumps(outputs, indent=2))

if __name__ == "__main__":
    # Ensure that the following environment variables are set in your environment:
    # AZURE_OPENAI_ENDPOINT and AZURE_DEPLOYMENT
    # Example:
    # os.environ["AZURE_OPENAI_ENDPOINT"] = "https://your-endpoint.openai.azure.com/"
    # os.environ["AZURE_DEPLOYMENT"] = "your-deployment-name"
    asyncio.run(main())
    print("done!")

```

#### Adversarial Simulator

```python
from azure.ai.evaluation.simulator import AdversarialSimulator, AdversarialScenario
from azure.identity import DefaultAzureCredential
from typing import Any, Dict, List, Optional
import asyncio


azure_ai_project = {
    "subscription_id": <subscription_id>,
    "resource_group_name": <resource_group_name>,
    "project_name": <project_name>
}

async def callback(
    messages: List[Dict],
    stream: bool = False,
    session_state: Any = None,
    context: Dict[str, Any] = None
) -> dict:
    messages_list = messages["messages"]
    # get last message
    latest_message = messages_list[-1]
    query = latest_message["content"]
    context = None
    if 'file_content' in messages["template_parameters"]:
        query += messages["template_parameters"]['file_content']
    # the next few lines explains how to use the AsyncAzureOpenAI's chat.completions
    # to respond to the simulator. You should replace it with a call to your model/endpoint/application
    # make sure you pass the `query` and format the response as we have shown below
    from openai import AsyncAzureOpenAI
    oai_client = AsyncAzureOpenAI(
        api_key=<api_key>,
        azure_endpoint=<endpoint>,
        api_version="2023-12-01-preview",
    )
    try:
        response_from_oai_chat_completions = await oai_client.chat.completions.create(messages=[{"content": query, "role": "user"}], model="gpt-4", max_tokens=300)
    except Exception as e:
        print(f"Error: {e}")
        # to continue the conversation, return the messages, else you can fail the adversarial with an exception
        message = {
            "content": "Something went wrong. Check the exception e for more details.",
            "role": "assistant",
            "context": None,
        }
        messages["messages"].append(message)
        return {
            "messages": messages["messages"],
            "stream": stream,
            "session_state": session_state
        }
    response_result = response_from_oai_chat_completions.choices[0].message.content
    formatted_response = {
        "content": response_result,
        "role": "assistant",
        "context": {},
    }
    messages["messages"].append(formatted_response)
    return {
        "messages": messages["messages"],
        "stream": stream,
        "session_state": session_state,
        "context": context
    }

```

#### Adversarial QA

```python
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
#### Direct Attack Simulator

```python
scenario = AdversarialScenario.ADVERSARIAL_QA
simulator = DirectAttackSimulator(azure_ai_project=azure_ai_project, credential=DefaultAzureCredential())

outputs = asyncio.run(
    simulator(
        scenario=scenario,
        max_conversation_turns=1,
        max_simulation_results=2,
        target=callback
    )
)

print(outputs)
```

## Examples

In following section you will find examples of:
- [Evaluate an application][evaluate_app]
- [Evaluate different models][evaluate_models]
- [Custom Evaluators][custom_evaluators]

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
[evaluate_app]: https://github.com/Azure-Samples/azureai-samples/tree/main/scenarios/evaluate/evaluate_app
[evaluation_tsg]: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/evaluation/azure-ai-evaluation/TROUBLESHOOTING.md
[ai_studio]: https://learn.microsoft.com/azure/ai-studio/what-is-ai-studio
[ai_project]: https://learn.microsoft.com/azure/ai-studio/how-to/create-projects?tabs=ai-studio
[azure_openai]: https://learn.microsoft.com/azure/ai-services/openai/
[evaluate_models]: https://github.com/Azure-Samples/azureai-samples/tree/main/scenarios/evaluate/evaluate_endpoints
[custom_evaluators]: https://github.com/Azure-Samples/azureai-samples/tree/main/scenarios/evaluate/evaluate_custom
[evaluate_samples]: https://github.com/Azure-Samples/azureai-samples/tree/main/scenarios/evaluate
[evaluation_metrics]: https://learn.microsoft.com/azure/ai-studio/concepts/evaluation-metrics-built-in
[performance_and_quality_evaluators]: https://learn.microsoft.com/azure/ai-studio/how-to/develop/evaluate-sdk#performance-and-quality-evaluators
[risk_and_safety_evaluators]: https://learn.microsoft.com/azure/ai-studio/how-to/develop/evaluate-sdk#risk-and-safety-evaluators
[composite_evaluators]: https://learn.microsoft.com/azure/ai-studio/how-to/develop/evaluate-sdk#composite-evaluators