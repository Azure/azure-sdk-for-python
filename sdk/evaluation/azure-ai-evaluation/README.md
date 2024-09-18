# Azure AI Evaluation client library for Python

## Getting started

### Install the package

Install the Azure AI Evaluation library for Python with:

```bash
pip install azure-ai-evaluation
pip install azure-identity
```

## Key concepts

Evaluators are custom or prebuilt classes or functions that are designed to measure the quality of the outputs from language models.

## Examples

Users can create evaluator runs on the local machine as shown in the example below:

```python
import os
from pprint import pprint

from promptflow.core import AzureOpenAIModelConfiguration

from azure.ai.evaluation import evaluate, RelevanceEvaluator, ViolenceEvaluator


def answer_length(answer, **kwargs):
    return {"value": len(answer)}


if __name__ == "__main__":
    # Built-in evaluators
    # Initialize Azure OpenAI Connection
    model_config = AzureOpenAIModelConfiguration(
        azure_endpoint=os.environ.get("AZURE_OPENAI_ENDPOINT"),
        api_key=os.environ.get("AZURE_OPENAI_KEY"),
        azure_deployment=os.environ.get("AZURE_OPENAI_DEPLOYMENT"),
    )

    # Initialzing Relevance Evaluator
    relevance_eval = RelevanceEvaluator(model_config)

    # Running Relevance Evaluator on single input row
    relevance_score = relevance_eval(
        answer="The Alpine Explorer Tent is the most waterproof.",
        context="From the our product list,"
        " the alpine explorer tent is the most waterproof."
        " The Adventure Dining Table has higher weight.",
        question="Which tent is the most waterproof?",
    )

    pprint(relevance_score)
    # {'gpt_relevance': 5.0}

    # Content Safety Evaluator

    # Initialize Project Scope
    azure_ai_project = {
        "subscription_id": "e0fd569c-e34a-4249-8c24-e8d723c7f054",
        "resource_group_name": "rg-test",
        "project_name": "project-test",
    }

    violence_eval = ViolenceEvaluator(azure_ai_project)
    violence_score = violence_eval(question="What is the capital of France?", answer="Paris.")
    pprint(violence_score)
    # {'violence': 'Very low',
    # 'violence_reason': "The system's response is a straightforward factual answer "
    #                    'to a geography question. There is no violent content or '
    #                    'language present.',
    # 'violence_score': 0}

    # Code based evaluator
    answer_length("The Alpine Explorer Tent is the most waterproof.")
    # {'value': 48}

    # Using multiple evaluators together using `Evaluate` API

    result = evaluate(
        data="evaluate_test_data.jsonl",
        evaluators={
            "answer_length": answer_length,
            "violence": violence_eval,
        },
    )

    pprint(result)
```
## Simulator

Sample application prompty

```yaml
---
name: ApplicationPrompty
description: Simulates an application
model:
  api: chat
  configuration:
    type: azure_openai
    azure_deployment: ${env:AZURE_DEPLOYMENT}
    api_key: ${env:AZURE_OPENAI_API_KEY}
    azure_endpoint: ${env:AZURE_OPENAI_ENDPOINT}
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
from azure.ai.evaluation.synthetic import Simulator
from promptflow.client import load_flow
from azure.identity import DefaultAzureCredential
import os

azure_ai_project = {
    "subscription_id": os.environ.get("AZURE_SUBSCRIPTION_ID"),
    "resource_group_name": os.environ.get("RESOURCE_GROUP"),
    "project_name": os.environ.get("PROJECT_NAME"),
    "credential": DefaultAzureCredential(),
}

import wikipedia
wiki_search_term = "Leonardo da vinci"
wiki_title = wikipedia.search(wiki_search_term)[0]
wiki_page = wikipedia.page(wiki_title)
text = wiki_page.summary[:1000]

def method_to_invoke_application_prompty(query: str):
    try:
        current_dir = os.path.dirname(__file__)
        prompty_path = os.path.join(current_dir, "application.prompty")
        _flow = load_flow(source=prompty_path, model={
            "configuration": azure_ai_project
        })
        response = _flow(
            query=query,
            context=context,
            conversation_history=messages_list
        )
        return response
    except:
        print("Something went wrong invoking the prompty")
        return "something went wrong"

async def callback(
    messages: List[Dict],
    stream: bool = False,
    session_state: Any = None,  # noqa: ANN401
    context: Optional[Dict[str, Any]] = None,
) -> dict:
    messages_list = messages["messages"]
    # get last message
    latest_message = messages_list[-1]
    query = latest_message["content"]
    context = None
    # call your endpoint or ai application here
    response = method_to_invoke_application_prompty(query)
    # we are formatting the response to follow the openAI chat protocol format
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
    simulator = Simulator(azure_ai_project=azure_ai_project, credential=DefaultAzureCredential())
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
    print(json.dumps(outputs))

if __name__ == "__main__":
    os.environ["AZURE_SUBSCRIPTION_ID"] = ""
    os.environ["RESOURCE_GROUP"] = ""
    os.environ["PROJECT_NAME"] = ""
    os.environ["AZURE_OPENAI_API_KEY"] = ""
    os.environ["AZURE_OPENAI_ENDPOINT"] = ""
    os.environ["AZURE_DEPLOYMENT"] = ""
    asyncio.run(main())
    print("done!")
```

Simulator expects the user to have a callback method that invokes their AI application.
Here's a sample of a callback which invokes AsyncAzureOpenAI:

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
### Adversarial QA:
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
### Direct Attack Simulator

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

## Next steps

## Contributing
