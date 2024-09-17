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

from azure.ai.evaluation.evaluate import evaluate
from azure.ai.evaluation.evaluators import RelevanceEvaluator
from azure.ai.evaluation.evaluators.content_safety import ViolenceEvaluator


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

Simulator expects the user to have a callback method that invokes their AI application.
Here's a sample of a callback which invokes AsyncAzureOpenAI:

```python
from from azure.ai.evaluation.synthetic import AdversarialSimulator, AdversarialScenario
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
