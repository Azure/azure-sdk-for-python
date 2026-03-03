# Azure AI Projects - Evaluation Samples

This folder contains samples demonstrating how to use Azure AI Foundry's evaluation capabilities with the `azure-ai-projects` SDK.

## Prerequisites

Before running any sample:

```bash
pip install "azure-ai-projects>=2.0.0b4" python-dotenv
```

Set these environment variables:
- `AZURE_AI_PROJECT_ENDPOINT` - Your Azure AI Project endpoint (e.g., `https://<account>.services.ai.azure.com/api/projects/<project>`)
- `AZURE_AI_MODEL_DEPLOYMENT_NAME` - The model deployment name (e.g., `gpt-4o-mini`)

## Sample Index

### Getting Started

| Sample | Description |
|--------|-------------|
| [sample_evaluations_builtin_with_inline_data.py](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/ai/azure-ai-projects/samples/evaluations/sample_evaluations_builtin_with_inline_data.py) | Basic evaluation with built-in evaluators using inline data |
| [sample_evaluations_builtin_with_dataset_id.py](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/ai/azure-ai-projects/samples/evaluations/sample_evaluations_builtin_with_dataset_id.py) | Evaluate using an uploaded dataset |
| [sample_eval_catalog.py](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/ai/azure-ai-projects/samples/evaluations/sample_eval_catalog.py) | Browse and use evaluators from the evaluation catalog |

### Agent / Model Evaluation

| Sample | Description |
|--------|-------------|
| [sample_agent_evaluation.py](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/ai/azure-ai-projects/samples/evaluations/sample_agent_evaluation.py) | Create a response from an agent and evaluate |
| [sample_agent_response_evaluation.py](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/ai/azure-ai-projects/samples/evaluations/sample_agent_response_evaluation.py) | Evaluate given agent responses |
| [sample_agent_response_evaluation_with_function_tool.py](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/ai/azure-ai-projects/samples/evaluations/sample_agent_response_evaluation_with_function_tool.py) | Evaluate agent responses with function tools |
| [sample_model_evaluation.py](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/ai/azure-ai-projects/samples/evaluations/sample_model_evaluation.py) | Create response from model and evaluate |

### Red Team Evaluations

| Sample | Description |
|--------|-------------|
| [sample_redteam_evaluations.py](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/ai/azure-ai-projects/samples/evaluations/sample_redteam_evaluations.py) | Security and safety evaluations using red team techniques |

### Additional Scenarios

These samples require additional setup or Azure services:

| Sample | Description | Requirements |
|--------|-------------|--------------|
| [sample_evaluations_builtin_with_traces.py](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/ai/azure-ai-projects/samples/evaluations/sample_evaluations_builtin_with_traces.py) | Evaluate against Application Insights traces | Connected Application Insights on Foundry Project |
| [sample_scheduled_evaluations.py](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/ai/azure-ai-projects/samples/evaluations/sample_scheduled_evaluations.py) | Schedule recurring evaluations | RBAC setup |
| [sample_continuous_evaluation_rule.py](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/ai/azure-ai-projects/samples/evaluations/sample_continuous_evaluation_rule.py) | Set up continuous evaluation rules | RBAC Setup |
| [sample_evaluations_score_model_grader_with_image.py](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/ai/azure-ai-projects/samples/evaluations/sample_evaluations_score_model_grader_with_image.py) | Evaluate with image data | Image file |
| [sample_evaluations_builtin_with_inline_data_oai.py](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/ai/azure-ai-projects/samples/evaluations/sample_evaluations_builtin_with_inline_data_oai.py) | Use OpenAI client directly | OpenAI SDK |

### Evaluator Types

| Sample | Description |
|--------|-------------|
| [sample_evaluations_graders.py](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/ai/azure-ai-projects/samples/evaluations/sample_evaluations_graders.py) | OpenAI graders: label_model, text_similarity, string_check, score_model |
| [sample_evaluations_ai_assisted.py](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/ai/azure-ai-projects/samples/evaluations/sample_evaluations_ai_assisted.py) | AI-assisted and NLP-based evaluators: Similarity, ROUGE, METEOR, GLEU, F1, BLEU |
| [sample_eval_catalog_code_based_evaluators.py](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/ai/azure-ai-projects/samples/evaluations/sample_eval_catalog_code_based_evaluators.py) | Custom code-based (python) evaluators |
| [sample_eval_catalog_prompt_based_evaluators.py](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/ai/azure-ai-projects/samples/evaluations/sample_eval_catalog_prompt_based_evaluators.py) | Custom prompt-based evaluators |

### Agentic Evaluators

Located in the [agentic_evaluators](https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/ai/azure-ai-projects/samples/evaluations/agentic_evaluators) subfolder:

| Sample | Description |
|--------|-------------|
| [sample_coherence.py](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/ai/azure-ai-projects/samples/evaluations/agentic_evaluators/sample_coherence.py) | Evaluate response coherence |
| [sample_fluency.py](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/ai/azure-ai-projects/samples/evaluations/agentic_evaluators/sample_fluency.py) | Evaluate response fluency |
| [sample_groundedness.py](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/ai/azure-ai-projects/samples/evaluations/agentic_evaluators/sample_groundedness.py) | Evaluate response groundedness |
| [sample_relevance.py](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/ai/azure-ai-projects/samples/evaluations/agentic_evaluators/sample_relevance.py) | Evaluate response relevance |
| [sample_intent_resolution.py](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/ai/azure-ai-projects/samples/evaluations/agentic_evaluators/sample_intent_resolution.py) | Evaluate intent resolution |
| [sample_response_completeness.py](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/ai/azure-ai-projects/samples/evaluations/agentic_evaluators/sample_response_completeness.py) | Evaluate response completeness |
| [sample_task_adherence.py](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/ai/azure-ai-projects/samples/evaluations/agentic_evaluators/sample_task_adherence.py) | Evaluate task adherence |
| [sample_task_completion.py](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/ai/azure-ai-projects/samples/evaluations/agentic_evaluators/sample_task_completion.py) | Evaluate task completion |
| [sample_task_navigation_efficiency.py](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/ai/azure-ai-projects/samples/evaluations/agentic_evaluators/sample_task_navigation_efficiency.py) | Evaluate navigation efficiency |
| [sample_tool_call_accuracy.py](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/ai/azure-ai-projects/samples/evaluations/agentic_evaluators/sample_tool_call_accuracy.py) | Evaluate tool call accuracy |
| [sample_tool_call_success.py](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/ai/azure-ai-projects/samples/evaluations/agentic_evaluators/sample_tool_call_success.py) | Evaluate tool call success |
| [sample_tool_input_accuracy.py](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/ai/azure-ai-projects/samples/evaluations/agentic_evaluators/sample_tool_input_accuracy.py) | Evaluate tool input accuracy |
| [sample_tool_output_utilization.py](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/ai/azure-ai-projects/samples/evaluations/agentic_evaluators/sample_tool_output_utilization.py) | Evaluate tool output utilization |
| [sample_tool_selection.py](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/ai/azure-ai-projects/samples/evaluations/agentic_evaluators/sample_tool_selection.py) | Evaluate tool selection |
| [sample_generic_agentic_evaluator](https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/ai/azure-ai-projects/samples/evaluations/agentic_evaluators/sample_generic_agentic_evaluator) | Generic agentic evaluator example |


### Evaluation Result Insights & Analysis

| Sample | Description |
|--------|-------------|
| [sample_evaluation_compare_insight.py](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/ai/azure-ai-projects/samples/evaluations/sample_evaluation_compare_insight.py) | Compare evaluation runs and generate statistics |
| [sample_evaluation_cluster_insight.py](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/ai/azure-ai-projects/samples/evaluations/sample_evaluation_cluster_insight.py) | Analyze evaluation runs with cluster insights |

## Running a Sample

```bash
# Set environment variables
export AZURE_AI_PROJECT_ENDPOINT="https://<your-account>.services.ai.azure.com/api/projects/<your-project>"
export AZURE_AI_MODEL_DEPLOYMENT_NAME="gpt-4o-mini" # Replace with your model

# Run a sample
python sample_evaluations_builtin_with_inline_data.py
```
