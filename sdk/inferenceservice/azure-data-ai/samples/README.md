# Azure Data AI samples

These samples use dictionary requests and responses with Azure Inference Service.
They do not require any model classes or a Cosmos DB account.

The SDK takes its endpoint and credential directly from the application. Environment
variables are optional configuration conventions, not SDK requirements.

The synchronous `semantic_reranking.py` sample uses the endpoint, key, and request configured
in `get_sample_inputs()`. The throttling benchmark reuses that function, so configuration
changes apply to both samples. Preserve local configuration privately; do not commit real credentials.
The asynchronous and Entra samples read these environment variables:

| Variable | Value |
| --- | --- |
| `AZURE_DATA_AI_ENDPOINT` | Azure Inference Service endpoint. |
| `AZURE_DATA_AI_KEY` | API subscription key, required for the key-auth samples. |

Never put real credentials in source code intended to be shared.

- `python samples/semantic_reranking.py`: synchronous raw-string API-key example with sentence scores.
- `python samples/semantic_reranking_async.py`: asynchronous `AzureKeyCredential` example.
- `python samples/semantic_reranking_entra.py`: synchronous Microsoft Entra example.
  Install `azure-identity` and configure a supported credential with permission
  to invoke the service endpoint.
- `python samples/semantic_reranking_throttling.py`: bounded asynchronous throttling benchmark
  using the original synchronous sample's current endpoint, key, query, documents, and options.

For the async sample, install `aiohttp`. The Entra sample only needs
`AZURE_DATA_AI_ENDPOINT`, not `AZURE_DATA_AI_KEY`.
The synchronous sample also retains local `AzureCliCredential` configuration, which
requires `azure-identity`; its current client call uses the key instead.

Both clients accept a key string, `AzureKeyCredential`, or the appropriate sync/async
token credential. Key authentication uses `Ocp-Apim-Subscription-Key` and requires a
key issued for an endpoint with key-based authentication enabled.

## Model selection and request options

The asynchronous and Entra examples accept `--model`. Omitting it leaves model selection to the service.
The original synchronous example uses the model configured in `get_sample_inputs()`.
The TypeSpec example uses `semantic-reranker-v1`; choose a model supported by your
endpoint rather than assuming that every endpoint exposes that model.

```bash
python samples/semantic_reranking_async.py --model semantic-reranker-v1
python samples/semantic_reranking_entra.py --model semantic-reranker-v1
```

The request dictionaries demonstrate `topK`, `batchSize`, `sort`, `returnDocuments`,
`returnSentenceScore`, and `documentType`. When supplied, the model argument becomes
the request's `model` field. These are service request-body fields, not method keyword
arguments.

For JSON documents, JSON-encode each document string and use `documentType: "json"`
with a `targetPaths` string. See the [JSON document and model-selection example](../README.md#model-selection-and-json-documents).

Python method names use snake_case, but dictionary keys keep the service's JSON
names: `topK`, `returnDocuments`, `returnSentenceScore`, and `sentenceScores`.
Read response entries from `scores`, not the legacy `Scores` spelling.

## Throttling benchmark

Use only an endpoint/account where you are authorized to generate test traffic.
The benchmark needs `aiohttp` and uses your original sample's local configuration;
it neither copies the key into another file nor prints credentials or document contents.
No wheel rebuild is needed for these sample-only changes.

From this package directory, run a burst with retries disabled so 429 responses
remain visible:

```bash
python samples/semantic_reranking_throttling.py --requests 60 --concurrency 25
```

The defaults are 60 logical calls, at most 25 concurrent calls, and a 60-second
deadline per call. These settings provide a burst above the reported 20-request
threshold, but **20 requests is not assumed to mean 20 requests per second**.
The limiter's time window, scope, and traffic from other callers affect the results.
No warm-up traffic is sent.

To exercise Azure Core's built-in retries and `Retry-After` handling:

```bash
python samples/semantic_reranking_throttling.py --requests 60 --concurrency 25 --retry-total 3
```

`--retry-total` changes the total retry budget; Azure Core's other retry rules and
per-error limits still apply. Retries increase HTTP traffic beyond the logical
call count. `--timeout` includes retry waits, so increase it when testing long
`Retry-After` delays. `--model` optionally overrides the original sample's model
for this run without changing that sample.

The JSON report distinguishes final logical-call outcomes from all HTTP responses.
`throttled_calls` counts calls that end in 429; `http_status_counts["429"]` also
includes throttles recovered by retries. `additional_http_attempts` counts attempts
beyond the first attempt per completed call, including retries or redirects.
The report includes throughput, overall and successful-call p50/p95/p99 latency,
`Retry-After` values, and up to ten error-response correlation IDs. Logical latency
includes retry/backoff time; fast rejected calls are excluded from success latency.

HTTP 429 is an expected benchmark outcome. Other HTTP errors, transport failures,
or timeouts produce a nonzero exit code. HTTP 401/403 stops scheduling new calls;
already-running calls are allowed to finish. If no 429 is observed, the report
says so rather than claiming that the limiter is absent or inferring its window.
