# Azure AI Projects - Dataset Samples

## Prerequisites

Before running any sample:

```bash
pip install "azure-ai-projects>=2.2.0" azure-identity python-dotenv
```

To run asynchronous samples, also install `aiohttp`. Samples that produce or consume Azure OpenAI files also require `openai`.

Set these environment variables:

| Variable | Required by | Value |
|---|---|---|
| `FOUNDRY_PROJECT_ENDPOINT` | All samples | Your Azure AI Project endpoint, e.g. `https://<your-account>.services.ai.azure.com/api/projects/<your-project>` |
| `FOUNDRY_MODEL_NAME` | `simple_qna` data-generation samples | An Azure OpenAI model deployment in your project. For **evaluation** jobs use a [Responses API](https://learn.microsoft.com/azure/foundry/openai/how-to/responses?tabs=python-key#model-support) model; for **fine-tuning** jobs use a chat-completions model (e.g. `gpt-4o`, `gpt-4.1`). |
| `FOUNDRY_AGENT_NAME` | Traces data-generation samples | An agent with recent traces in Application Insights. Foundry Agents and OpenTelemetry-instrumented third-party agents are both supported. |

Optional per-sample variables (`DATASET_NAME`, `POLL_INTERVAL_SECONDS`, `FOUNDRY_TRACES_WINDOW_DAYS`, etc.) are documented in each sample's docstring.

## Sample Index

### Dataset Basics

| Sample | Description |
|--------|-------------|
| [sample_datasets.py](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/ai/azure-ai-projects/samples/datasets/sample_datasets.py) | Upload files, create, list, and delete versioned Datasets |
| [sample_datasets_async.py](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/ai/azure-ai-projects/samples/datasets/sample_datasets_async.py) | Async version of the dataset CRUD sample |
| [sample_datasets_download.py](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/ai/azure-ai-projects/samples/datasets/sample_datasets_download.py) | Upload a folder as a Dataset and download its files via an Azure storage ContainerClient |

### Data Generation Jobs

| Sample | Source(s) | Scenario | Description |
|--------|-----------|----------|-------------|
| [sample_dataset_generation_job_simpleqna_with_prompt_source.py](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/ai/azure-ai-projects/samples/datasets/sample_dataset_generation_job_simpleqna_with_prompt_source.py) | Prompt | Evaluation | Generate a QnA dataset from an inline prompt and run an evaluation against it end-to-end |
| [sample_dataset_generation_job_simpleqna_with_file_source.py](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/ai/azure-ai-projects/samples/datasets/sample_dataset_generation_job_simpleqna_with_file_source.py) | File (Azure OpenAI) + Prompt | Evaluation | Generate a QnA dataset from an Azure OpenAI File combined with an inline Prompt |
| [sample_dataset_generation_job_simpleqna_with_agent_source.py](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/ai/azure-ai-projects/samples/datasets/sample_dataset_generation_job_simpleqna_with_agent_source.py) | Agent definition | Evaluation | Generate a QnA dataset by creating a prompt agent and sourcing the job from the agent's instructions |
| [sample_dataset_generation_job_traces_for_evaluation.py](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/ai/azure-ai-projects/samples/datasets/sample_dataset_generation_job_traces_for_evaluation.py) | Traces | Evaluation | Generate a QnA dataset from an agent's recent conversation traces |
| [sample_dataset_generation_job_simpleqna_for_finetuning.py](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/ai/azure-ai-projects/samples/datasets/sample_dataset_generation_job_simpleqna_for_finetuning.py) | File (Azure OpenAI) | Supervised fine-tuning | Generate supervised fine-tuning JSONL files (training and validation partitions) from an uploaded Azure OpenAI File |
| [sample_dataset_generation_job_traces_for_finetuning.py](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/ai/azure-ai-projects/samples/datasets/sample_dataset_generation_job_traces_for_finetuning.py) | Traces | Supervised fine-tuning | Generate supervised fine-tuning JSONL files (training and validation partitions) from an agent's recent conversation traces |
