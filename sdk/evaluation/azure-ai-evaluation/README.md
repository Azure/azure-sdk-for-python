# Azure AI Evaluation client library for Python

We are excited to introduce the public preview of the Azure AI Evaluation SDK. 

[Source code][source_code]
| [Package (PyPI)][evaluation_pypi]
| [API reference documentation][evaluation_ref_docs]
| [Product documentation][product_documentation]
| [Samples][evaluation_samples]

This package has been tested with Python 3.8, 3.9, 3.10, 3.11, and 3.12.

For a more complete set of Azure libraries, see https://aka.ms/azsdk/python/all

## Getting started

### Prerequisites

- Python 3.8 or later is required to use this package.

### Install the package

Install the Azure AI Evaluation library for Python with [pip][pip_link]::

```bash
pip install azure-ai-evaluation
```

## Key concepts

Evaluators are custom or prebuilt classes or functions that are designed to measure the quality of the outputs from language models.

## Examples

### Evaluators

Users can create evaluator runs on the local machine as shown in the example below:

```python
import os
from pprint import pprint

from azure.ai.evaluation import evaluate, RelevanceEvaluator, ViolenceEvaluator


def response_length(response, **kwargs):
    return {"value": len(response)}


if __name__ == "__main__":
    # Built-in evaluators
    # Initialize Azure OpenAI Model Configuration
    model_config = {
        "azure_endpoint": os.environ.get("AZURE_OPENAI_ENDPOINT"),
        "api_key": os.environ.get("AZURE_OPENAI_KEY"),
        "azure_deployment": os.environ.get("AZURE_OPENAI_DEPLOYMENT"),
    }

    # Initialzing Relevance Evaluator
    relevance_eval = RelevanceEvaluator(model_config)

    # Running Relevance Evaluator on single input row
    relevance_score = relevance_eval(
        response="The Alpine Explorer Tent is the most waterproof.",
        context="From the our product list,"
        " the alpine explorer tent is the most waterproof."
        " The Adventure Dining Table has higher weight.",
        query="Which tent is the most waterproof?",
    )

    pprint(relevance_score)
    # {'gpt_relevance': 5.0}

    # Content Safety Evaluator

    # Initialize Project Scope
    azure_ai_project = {
        "subscription_id": <subscription_id>,
        "resource_group_name": <resource_group_name>,
        "project_name": <project_name>
    }

    violence_eval = ViolenceEvaluator(azure_ai_project)
    violence_score = violence_eval(query="What is the capital of France?", response="Paris.")
    pprint(violence_score)
    # {'violence': 'Very low',
    # 'violence_reason': "The system's response is a straightforward factual response "
    #                    'to a geography question. There is no violent content or '
    #                    'language present.',
    # 'violence_score': 0}

    # Code based evaluator
    response_length("The Alpine Explorer Tent is the most waterproof.")
    # {'value': 48}

    # Using multiple evaluators together using `Evaluate` API

    result = evaluate(
        data="evaluate_test_data.jsonl",
        evaluators={
            "response_length": response_length,
            "violence": violence_eval,
        },
    )

    pprint(result)
```
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
Application code:

```python
import json
import asyncio
from typing import Any, Dict, List, Optional
from azure.ai.evaluation.simulator import Simulator
from promptflow.client import load_flow
from azure.identity import DefaultAzureCredential
import os
import wikipedia

# Set up the model configuration without api_key, using DefaultAzureCredential
model_config = {
    "azure_endpoint": os.environ.get("AZURE_OPENAI_ENDPOINT"),
    "azure_deployment": os.environ.get("AZURE_DEPLOYMENT"),
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
        "context": {
            "citations": None,
        },
    }
    messages["messages"].append(formatted_response)
    return {"messages": messages["messages"], "stream": stream, "session_state": session_state, "context": context}

async def main():
    simulator = Simulator(model_config=model_config, credential=DefaultAzureCredential())
    outputs = await simulator(
        target=callback,
        text=text,
        num_queries=2,
        max_conversation_turns=4,
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
from from azure.ai.evaluation.simulator import AdversarialSimulator, AdversarialScenario
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

print(outputs.to_eval_qa_json_lines())
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
## Troubleshooting

### General

Azure ML clients raise exceptions defined in [Azure Core][azure_core_readme].

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
