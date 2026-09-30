# Azure AI Projects - Dataset Samples

## Prerequisites

Before running any sample:

```bash
pip install "azure-ai-projects>=2.8.0" azure-identity python-dotenv
```

To run asynchronous samples, also install `aiohttp`. Samples that produce or consume Azure OpenAI files, run evaluations, or seed agent conversations also use `openai`.

Set these environment variables:

| Variable | Required by | Value |
|---|---|---|
| `FOUNDRY_PROJECT_ENDPOINT` | All samples | Your Azure AI Project endpoint, e.g. `https://<your-account>.services.ai.azure.com/api/projects/<your-project>` |
| `FOUNDRY_MODEL_NAME` | All data generation samples | An Azure OpenAI model deployment in your project. For `simple_qna` and `simulation_seed` **evaluation** jobs use a [Responses API](https://learn.microsoft.com/azure/foundry/openai/how-to/responses?tabs=python-key#model-support) model; for `simple_qna` **fine-tuning** jobs use a chat-completions model (e.g. `gpt-4o`, `gpt-4.1`). The traces samples use it as the model of the agent they create and seed with conversations. |
| `DATASET_NAME` | Optional, most samples | Name of the output dataset (or output file prefix for fine-tuning jobs). Data generation samples append a unique run id; the resulting output name must fit within 50 characters. |
| `POLL_INTERVAL_SECONDS` | Optional, most data generation samples | Seconds to wait between job status polls. Defaults to `10`. |
| `TRACE_IDS` | Optional, `sample_dataset_generation_job_traces_for_evaluation_merge.py` | Comma-separated trace IDs to restrict the traces data generation jobs to. |

The traces samples create their own agent and seed it with conversations, so they don't need an existing agent. They require an Application Insights resource connected to the project, and the project's managed identity must have the `Reader` role on it. Other optional variables are documented in each sample's docstring.

Supervised fine-tuning data generation, `question_types`, and Azure OpenAI file outputs are preview features. The client automatically sends the required `Foundry-Features: DataGenerationJobs=V1Preview` opt-in header on all data generation job operations.

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
| [sample_dataset_generation_job_simulation_seed_for_evaluation.py](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/ai/azure-ai-projects/samples/datasets/sample_dataset_generation_job_simulation_seed_for_evaluation.py) | Prompt | Evaluation | Generate simulation seeds (multi-turn test cases) for agent evaluation from a description of the agent's purpose, and print the first rows |
| [sample_dataset_generation_job_traces_for_evaluation.py](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/ai/azure-ai-projects/samples/datasets/sample_dataset_generation_job_traces_for_evaluation.py) | Traces | Evaluation | Generate an evaluation dataset from an agent's recent conversation traces |
| [sample_dataset_generation_job_traces_for_evaluation_merge.py](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/ai/azure-ai-projects/samples/datasets/sample_dataset_generation_job_traces_for_evaluation_merge.py) | Traces | Evaluation | Grow an evaluation dataset from traces over time: create a dataset version with `write_mode=overwrite`, then merge newly generated, de-duplicated rows into the next version with `write_mode=merge` |
| [sample_dataset_generation_job_management.py](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/ai/azure-ai-projects/samples/datasets/sample_dataset_generation_job_management.py) | Prompt | Evaluation | Create a job without SDK polling, then list, get, cancel, and delete data generation jobs |
| [sample_dataset_generation_job_simpleqna_for_finetuning.py](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/ai/azure-ai-projects/samples/datasets/sample_dataset_generation_job_simpleqna_for_finetuning.py) | File (Azure OpenAI) | Supervised fine-tuning (preview) | Generate supervised fine-tuning JSONL files (training and validation partitions) from an uploaded Azure OpenAI File |
| [sample_dataset_generation_job_simpleqna_for_finetuning_async.py](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/ai/azure-ai-projects/samples/datasets/sample_dataset_generation_job_simpleqna_for_finetuning_async.py) | File (Azure OpenAI) | Supervised fine-tuning (preview) | Async version of the supervised fine-tuning sample above |
| [sample_dataset_generation_job_simpleqna_for_finetuning_with_app_polling.py](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/ai/azure-ai-projects/samples/datasets/sample_dataset_generation_job_simpleqna_for_finetuning_with_app_polling.py) | File (Azure OpenAI) | Supervised fine-tuning (preview) | Same as the supervised fine-tuning sample, but creates the job with `polling=False` and polls `get_generation_job` from application code |
| [sample_dataset_generation_job_simpleqna_for_finetuning_with_app_polling_async.py](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/ai/azure-ai-projects/samples/datasets/sample_dataset_generation_job_simpleqna_for_finetuning_with_app_polling_async.py) | File (Azure OpenAI) | Supervised fine-tuning (preview) | Async version of the application-polling sample above |
| [sample_dataset_generation_job_traces_for_finetuning.py](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/ai/azure-ai-projects/samples/datasets/sample_dataset_generation_job_traces_for_finetuning.py) | Traces | Supervised fine-tuning (preview) | Generate supervised fine-tuning JSONL files (training and validation partitions) from an agent's recent conversation traces |
