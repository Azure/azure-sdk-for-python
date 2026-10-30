# Azure OpenAI Decisions evaluators

Use a GPT-6 Luna deployment with the `decision` capability in a region where Azure OpenAI Decisions is available
(East US 2 is excluded). Use the account's OpenAI endpoint, such as `https://YOUR-ACCOUNT.openai.azure.com`.
This requires `azure-ai-evaluation` 1.18.11 or later, where the built-in evaluators accept a Decision model
configuration.

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

The other built-in evaluators that support Decision models, and the Decision-capable evaluators in the Microsoft
Foundry catalog, accept the same configuration; their rubrics are shared across protocols.
For API-key authentication, provide `api_key` in the model configuration from your secret store.
The SDK retains the existing retry, timeout, cancellation, and credential ownership rules, and reuses a credential's
token across requests until shortly before it expires.
There is no dependency on `openai.decisions.create`, which needs a newer major version of the `openai` package;
the shared asynchronous HTTP transport sends the same request to `/openai/v1/decisions`.

Omitting `decision_protocol` selects the Microsoft Decision protocol. A deployment that serves the other protocol
fails with an error that names the setting to change. An ordinary chat configuration continues to use chat even when
that deployment also supports Decisions; GPT-6 Luna is a reasoning model, so pass `is_reasoning_model=True` to an
evaluator that uses it as a chat judge.

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

Hosted evaluations select a service-approved deployment by name; the service owns protocol configuration and checks
its live capability and model version.

References: [Azure Decisions](https://learn.microsoft.com/en-gb/azure/foundry/openai/how-to/decisions),
[OpenAI Decisions contract](https://developers.openai.com/api/reference/resources/decisions/methods/create).
