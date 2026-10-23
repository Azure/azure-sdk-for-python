# Azure OpenAI Decisions evaluators

Use a GPT-6 Luna deployment with the `decision` capability in a supported Foundry region.
An ordinary chat configuration continues to use chat even when that deployment also supports Decisions.
The Evaluation SDK requires version 1.18.11 or a private build containing this adapter.

```python
from azure.identity import DefaultAzureCredential
from azure.ai.evaluation import CoherenceEvaluator

with DefaultAzureCredential() as credential:
    evaluator = CoherenceEvaluator(
        model_config={
            "type": "decision",
            "decision_protocol": "openai",
            "azure_endpoint": "https://YOUR-ACCOUNT.openai.azure.com",
            "azure_deployment": "YOUR-DECISIONS-DEPLOYMENT",
        },
        credential=credential,
    )
    result = evaluator(query="When does the museum open?", response="The museum opens at noon.")
```

For API-key authentication, provide `api_key` in the model configuration from your secret store.
The SDK retains the existing retry, timeout, cancellation, and credential ownership rules.
There is no dependency on `openai.decisions.create`; the shared asynchronous HTTP transport performs the request.

Existing rubrics become named predicate/score questions. Ordinal metrics still select the highest-probability
level, resolving ties to the lowest level. The returned OpenAI weighted mean is retained as `native_mean`,
and the original answer appears in `decision_model.native_answer`; it does not replace the public score.
Any refused question fails the evaluation with known usage rather than producing a fabricated grade.
Cache and reasoning details remain under `decision_model.usage_details` and are not additional token totals.

Omitting `decision_protocol` retains the Microsoft/PiLabs protocol. Hosted evaluations select a service-approved
deployment by name; the service owns protocol configuration and checks its live capability and model version.

References: [Azure Decisions](https://learn.microsoft.com/en-gb/azure/foundry/openai/how-to/decisions),
[OpenAI Decisions contract](https://developers.openai.com/api/reference/resources/decisions/methods/create).
