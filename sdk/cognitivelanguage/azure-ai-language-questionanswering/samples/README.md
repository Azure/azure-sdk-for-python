---
page_type: sample
languages:
  - python
products:
- azure
- azure-cognitive-services
- language-service
urlFragment: languagequestionanswering-samples
---

# Samples for Azure Language Question Answering (Inference)

These samples demonstrate how to use the runtime Question Answering features to query an existing knowledge base
or ad‑hoc text content. Authoring (project creation / deployment / source management) samples have been moved
to a separate location and are intentionally not referenced here.

## Samples Included

| File | Description |
|------|-------------|
| `sample_query_knowledgebase.py` / `async_samples/sample_query_knowledgebase_async.py` | Ask a question against a deployed knowledge base project (flattened parameters) |
| `sample_chat.py` / `async_samples/sample_chat_async.py` | Ask a follow‑up contextual question using `answer_context` |
| `sample_query_text.py` / `async_samples/sample_query_text_async.py` | Ask a question over ad‑hoc text documents (options object pattern) |

> Note: The deprecated wrapper methods `client.get_answers` and `client.get_answers_from_text`
> have been replaced in these samples by the recommended operations group access:
> `client.get_answers` and `client.get_answers_from_text`.

## Prerequisites

- Python 3.9+ (match the package's `python_requires`)
- An [Azure subscription][azure_subscription]
- A deployed Language Question Answering resource (project + deployment for knowledge base queries)

## Environment Variables

Set the following environment variables before running a sample:

Required (all runtime samples):
- `AZURE_QUESTIONANSWERING_ENDPOINT` – your resource endpoint
- `AZURE_QUESTIONANSWERING_KEY` – the API key

Additional for knowledge base & chat samples:
- `AZURE_QUESTIONANSWERING_PROJECT` – project (knowledge base) name
- `AZURE_QUESTIONANSWERING_DEPLOYMENT` – deployment name (if omitted, samples default to `production`)

## Install the Library

```bash
pip install azure-ai-language-questionanswering
```

## Run

```bash
python sample_query_knowledgebase.py
python sample_chat.py
python sample_query_text.py
# Async examples:
python async_samples/sample_query_knowledgebase_async.py
```

Ensure you are in this `samples` directory (or adjust paths accordingly).

## Authentication

These samples use `AzureKeyCredential`. For AAD / `DefaultAzureCredential` usage, see the main package documentation.

[azure_subscription]: https://azure.microsoft.com/free/
[language_service]: https://ms.portal.azure.com/#create/Microsoft.CognitiveServicesTextAnalytics
