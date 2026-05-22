# Azure AI Projects - Dataset Samples

This folder contains samples demonstrating how to work with versioned Datasets and data generation jobs in Azure AI Foundry using the `azure-ai-projects` SDK.

## Prerequisites

Before running any sample:

```bash
pip install "azure-ai-projects>=2.0.0" azure-identity python-dotenv
```

To run asynchronous samples, you will also need to install `aiohttp`. The data generation samples that interact with Azure OpenAI files (any sample that emits or consumes Azure OpenAI File outputs/inputs) also require `openai`.

Set these environment variables:
- `FOUNDRY_PROJECT_ENDPOINT` - Required for all samples. Your Azure AI Project endpoint (e.g., `https://<account>.services.ai.azure.com/api/projects/<project>`).
- `FOUNDRY_MODEL_NAME` - Required for `simple_qna` data generation samples (`sample_dataset_generation_job_with_evaluation.py`, `sample_dataset_generation_job_simpleqna_with_dataset_source.py`, `sample_dataset_generation_job_simpleqna_for_finetuning.py`). The model deployment name (e.g., `gpt-4o-mini`).
- `FOUNDRY_AGENT_NAME` - Required for traces-based data generation samples (`sample_dataset_generation_job_traces_for_evaluation.py`, `sample_dataset_generation_job_traces_for_finetuning.py`). The name of a Foundry agent with recent traces in Application Insights.

Most samples accept additional optional environment variables (`DATASET_NAME`, `POLL_INTERVAL_SECONDS`, `FOUNDRY_TRACES_WINDOW_DAYS`, etc.) — see each sample's docstring for details.

## Running a Sample

```bash
# Set environment variables
export FOUNDRY_PROJECT_ENDPOINT="https://<your-account>.services.ai.azure.com/api/projects/<your-project>"
export FOUNDRY_MODEL_NAME="gpt-4o-mini" # Replace with your model

# Run a sample. For example:
python sample_datasets.py
```

## Sample Index

### Dataset Basics

| Sample | Description |
|--------|-------------|
| [sample_datasets.py](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/ai/azure-ai-projects/samples/datasets/sample_datasets.py) | Upload files, create, list, and delete versioned Datasets |
| [sample_datasets_async.py](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/ai/azure-ai-projects/samples/datasets/sample_datasets_async.py) | Async version of the dataset CRUD sample |
| [sample_datasets_download.py](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/ai/azure-ai-projects/samples/datasets/sample_datasets_download.py) | Upload a folder as a Dataset and download its files via an Azure storage ContainerClient |

### Data Generation Jobs

Data generation jobs synthesize evaluation datasets or supervised fine-tuning files from different kinds of sources (a Foundry agent's traces, an inline prompt, an existing Dataset, or an Azure OpenAI File). The job runs server-side; the samples below show how to submit a job, poll it to completion, and locate the generated artifacts.

| Sample | Source(s) | Scenario | Description |
|--------|-----------|----------|-------------|
| [sample_dataset_generation_job_with_evaluation.py](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/ai/azure-ai-projects/samples/datasets/sample_dataset_generation_job_with_evaluation.py) | Prompt | Evaluation | Generate a QnA dataset from an inline prompt and run an evaluation against it end-to-end |
| [sample_dataset_generation_job_traces_for_evaluation.py](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/ai/azure-ai-projects/samples/datasets/sample_dataset_generation_job_traces_for_evaluation.py) | Traces | Evaluation | Generate an evaluation dataset from a Foundry agent's recent conversation traces |
| [sample_dataset_generation_job_traces_for_finetuning.py](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/ai/azure-ai-projects/samples/datasets/sample_dataset_generation_job_traces_for_finetuning.py) | Traces | Supervised fine-tuning | Generate ready-to-use training + validation JSONL files from a Foundry agent's recent traces |
| [sample_dataset_generation_job_simpleqna_with_dataset_source.py](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/ai/azure-ai-projects/samples/datasets/sample_dataset_generation_job_simpleqna_with_dataset_source.py) | Dataset + Prompt | Evaluation | Combine a seed Dataset with an inline Prompt to steer multi-source SimpleQnA generation, and confirm output metadata propagation |
| [sample_dataset_generation_job_simpleqna_for_finetuning.py](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/ai/azure-ai-projects/samples/datasets/sample_dataset_generation_job_simpleqna_for_finetuning.py) | File (Azure OpenAI) | Supervised fine-tuning | Upload a reference document as an Azure OpenAI File and generate short- and long-answer fine-tuning files from it |
