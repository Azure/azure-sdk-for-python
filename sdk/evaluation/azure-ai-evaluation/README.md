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
    project_scope = {
        "subscription_id": "e0fd569c-e34a-4249-8c24-e8d723c7f054",
        "resource_group_name": "rg-test",
        "project_name": "project-test",
    }

    violence_eval = ViolenceEvaluator(project_scope)
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

## Troubleshooting

## Next steps

## Contributing
