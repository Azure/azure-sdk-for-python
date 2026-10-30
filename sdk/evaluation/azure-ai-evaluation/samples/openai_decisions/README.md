# Azure OpenAI Decisions evaluators

Use a GPT-6 Luna deployment with the `decision` capability in a region where Azure OpenAI Decisions is available
(East US 2 is excluded). Use the account's OpenAI endpoint, such as `https://YOUR-ACCOUNT.openai.azure.com`.
An ordinary chat configuration continues to use chat even when that deployment also supports Decisions.
The Evaluation SDK requires version 1.18.11 or a private build containing this adapter.
Run this example from the companion `azureml-assets` checkout with the existing PiLabs/Microsoft Decision-capable
evaluator versions. Their code and rubrics are shared across protocols; an OpenAI-specific asset release is not required.
The SDK supplies the shared runner; its top-level `azure.ai.evaluation.CoherenceEvaluator` remains a chat evaluator.

```python
from azure.identity import DefaultAzureCredential
from assets.evaluators.builtin.coherence.evaluator._coherence import CoherenceEvaluator

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
There is no dependency on `openai.decisions.create`, which needs a newer major version of the `openai` package;
the shared asynchronous HTTP transport sends the same request to `/openai/v1/decisions`.

The SDK's protocol adapter turns each Boolean question into a predicate whose instructions state its true and false
criteria, and each ordinal question into levels labeled `Level 1` to `Level n` from the lowest, the ordinal names that
rubric text such as "imply level 2" uses. Answers are bound back by question name, so
the evaluator scores them exactly as it scores Microsoft Decision answers: ordinal metrics select the
highest-probability level, resolving ties to the lowest level, and the provider's weighted mean is kept only as
`native_mean`. `decision_model.native_answer` holds the answer in this shared shape, and `decision_model.protocol`
is `openai`. Cache and reasoning counters stay under `decision_model.usage_details` and are not added to token totals.

A refused question fails the evaluation only when the evaluation reads that answer. For example, when the
applicability question says the metric does not apply, the evaluation is skipped even if its grade was refused.
A refusal that is read raises an `EvaluationException` with known usage and `decision_model.error_kind` set to
`model_refusal`; it never becomes a fabricated score or skip.

Omitting `decision_protocol` retains the Microsoft Decision protocol. Hosted evaluations select a service-approved
deployment by name; the service owns protocol configuration and checks its live capability and model version.

References: [Azure Decisions](https://learn.microsoft.com/en-gb/azure/foundry/openai/how-to/decisions),
[OpenAI Decisions contract](https://developers.openai.com/api/reference/resources/decisions/methods/create).
