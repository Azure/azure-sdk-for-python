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
- `FOUNDRY_MODEL_NAME` - Required for `simple_qna` data generation samples (`sample_dataset_generation_job_simpleqna_with_prompt_source.py`, `sample_dataset_generation_job_simpleqna_with_file_source.py`, `sample_dataset_generation_job_simpleqna_with_agent_source.py`, `sample_dataset_generation_job_simpleqna_for_finetuning.py`). The name of an Azure OpenAI model **deployment** in your project (matches the `FOUNDRY_MODEL_NAME` convention used elsewhere in this samples folder). For **evaluation** jobs the deployment must support the [Responses API](https://learn.microsoft.com/azure/foundry/openai/how-to/responses?tabs=python-key#model-support); for **fine-tuning** jobs the deployment must support chat completions (e.g. `gpt-4o`, `gpt-4.1`).
- `FOUNDRY_AGENT_NAME` - Required for the two traces samples (`sample_dataset_generation_job_traces_for_evaluation.py`, `sample_dataset_generation_job_traces_for_finetuning.py`). The name of an agent that has recent traces in Application Insights. Traces sources support both Foundry Agents and third-party (OpenTelemetry instrumented) agents. The agent-source SimpleQnA sample (`sample_dataset_generation_job_simpleqna_with_agent_source.py`) does *not* read this variable — it creates its own short-lived prompt agent at runtime and cleans it up at the end.

Most samples accept additional optional environment variables (`DATASET_NAME`, `POLL_INTERVAL_SECONDS`, `FOUNDRY_TRACES_WINDOW_DAYS`, etc.) — see each sample's docstring for details.

## Running a Sample

```bash
# Set environment variables
export FOUNDRY_PROJECT_ENDPOINT="https://<your-account>.services.ai.azure.com/api/projects/<your-project>"
export FOUNDRY_MODEL_NAME="gpt-4o-mini" # Replace with your model deployment

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

Data generation jobs synthesize evaluation datasets or supervised fine-tuning files from different kinds of sources (an agent's traces, an agent's definition, an inline prompt, or an Azure OpenAI File). The job runs server-side; the samples below show how to submit a job, poll it to completion, and locate the generated artifacts.

To keep the project clean across repeated runs, each sample below also deletes every resource it creates (including the job record, any uploaded input files, any short-lived agent, and the generated dataset or fine-tuning files) before exiting.

| Sample | Source(s) | Scenario | Description |
|--------|-----------|----------|-------------|
| [sample_dataset_generation_job_simpleqna_with_prompt_source.py](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/ai/azure-ai-projects/samples/datasets/sample_dataset_generation_job_simpleqna_with_prompt_source.py) | Prompt | Evaluation | Generate a QnA dataset from an inline prompt and run an evaluation against it end-to-end |
| [sample_dataset_generation_job_traces_for_evaluation.py](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/ai/azure-ai-projects/samples/datasets/sample_dataset_generation_job_traces_for_evaluation.py) | Traces | Evaluation | Generate an evaluation dataset from an agent's recent conversation traces (traces recipe) |
| [sample_dataset_generation_job_traces_for_finetuning.py](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/ai/azure-ai-projects/samples/datasets/sample_dataset_generation_job_traces_for_finetuning.py) | Traces | Supervised fine-tuning | Generate ready-to-use training + validation JSONL files from an agent's recent traces |
| [sample_dataset_generation_job_simpleqna_with_agent_source.py](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/ai/azure-ai-projects/samples/datasets/sample_dataset_generation_job_simpleqna_with_agent_source.py) | Agent definition | Evaluation | Self-contained: creates a short-lived `PromptAgentDefinition`, then generates an evaluation dataset from the agent's instructions / prompt via the `simple_qna` recipe |
| [sample_dataset_generation_job_simpleqna_with_file_source.py](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/ai/azure-ai-projects/samples/datasets/sample_dataset_generation_job_simpleqna_with_file_source.py) | File (Azure OpenAI) + Prompt | Evaluation | Combine an uploaded reference document with an inline Prompt to steer multi-source SimpleQnA generation, and confirm output metadata propagation |
| [sample_dataset_generation_job_simpleqna_for_finetuning.py](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/ai/azure-ai-projects/samples/datasets/sample_dataset_generation_job_simpleqna_for_finetuning.py) | File (Azure OpenAI) | Supervised fine-tuning | Upload a reference document as an Azure OpenAI File and generate short- and long-answer fine-tuning files from it |
