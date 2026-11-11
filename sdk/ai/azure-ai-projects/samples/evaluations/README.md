# Azure AI Projects - Evaluation Samples

This folder contains samples demonstrating how to use Azure AI Foundry's evaluation capabilities with the `azure-ai-projects` SDK.

## Prerequisites

Before running any sample:

```bash
pip install "azure-ai-projects>=2.8.0" python-dotenv
```

To run asynchronous samples, you will also need to install `aiohttp`.

Set these environment variables:
- `FOUNDRY_PROJECT_ENDPOINT` - Your Azure AI Project endpoint (e.g., `https://<account>.services.ai.azure.com/api/projects/<project>`)
- `FOUNDRY_MODEL_NAME` - The model deployment name (e.g., `gpt-4o-mini`)

## Running a Sample

```bash
# Set environment variables
export FOUNDRY_PROJECT_ENDPOINT="https://<your-account>.services.ai.azure.com/api/projects/<your-project>"
export FOUNDRY_MODEL_NAME="gpt-4o-mini" # Replace with your model

# Run a sample. For example:
python sample_evaluations_builtin_with_inline_data.py
```

## Sample Index

### Getting Started

| Sample | Description |
|--------|-------------|
| [sample_evaluations_builtin_with_inline_data.py](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/ai/azure-ai-projects/samples/evaluations/sample_evaluations_builtin_with_inline_data.py) | Basic evaluation with built-in evaluators using inline data |
| [sample_evaluations_builtin_with_dataset_id.py](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/ai/azure-ai-projects/samples/evaluations/sample_evaluations_builtin_with_dataset_id.py) | Evaluate using an uploaded JSONL dataset |
| [sample_evaluations_builtin_with_csv.py](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/ai/azure-ai-projects/samples/evaluations/sample_evaluations_builtin_with_csv.py) | Evaluate using an uploaded CSV dataset |
| [sample_eval_catalog.py](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/ai/azure-ai-projects/samples/evaluations/sample_eval_catalog.py) | Browse and use evaluators from the evaluation catalog |

### Agent / Model Evaluation

| Sample | Description |
|--------|-------------|
| [sample_agent_evaluation.py](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/ai/azure-ai-projects/samples/evaluations/sample_agent_evaluation.py) | Create a response from an agent and evaluate |
| [sample_agent_response_evaluation.py](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/ai/azure-ai-projects/samples/evaluations/sample_agent_response_evaluation.py) | Evaluate given agent responses |
| [sample_agent_response_evaluation_with_function_tool.py](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/ai/azure-ai-projects/samples/evaluations/sample_agent_response_evaluation_with_function_tool.py) | Evaluate agent responses with function tools |
| [sample_model_evaluation.py](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/ai/azure-ai-projects/samples/evaluations/sample_model_evaluation.py) | Create response from model and evaluate |
| [sample_synthetic_data_agent_evaluation.py](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/ai/azure-ai-projects/samples/evaluations/sample_synthetic_data_agent_evaluation.py) | Generate synthetic test data, evaluate a Foundry agent |
| [sample_synthetic_multiturn_evaluation.py](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/ai/azure-ai-projects/samples/evaluations/sample_synthetic_multiturn_evaluation.py) | Generate synthetic scenarios from an agent and simulate multi-turn conversations for them in a single eval run, then evaluate |
| [sample_synthetic_data_model_evaluation.py](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/ai/azure-ai-projects/samples/evaluations/sample_synthetic_data_model_evaluation.py) | Generate synthetic test data, evaluate a model |

### Red Team Evaluations

| Sample | Description |
|--------|-------------|
| [sample_redteam_evaluations.py](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/ai/azure-ai-projects/samples/evaluations/sample_redteam_evaluations.py) | Security and safety evaluations using red team techniques |

### Voice Evaluation

[sample_audio_conversation_evaluation.py](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/ai/azure-ai-projects/samples/evaluations/sample_audio_conversation_evaluation.py) and its
[async version](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/ai/azure-ai-projects/samples/evaluations/sample_audio_conversation_evaluation_async.py) evaluate a
recorded-conversation dataset without calling a target agent. They use
`builtin.task_completion_audio`, `builtin.groundedness_audio`,
`builtin.customer_satisfaction_audio`, and `builtin.coherence_audio`.
These evaluators and an eligible audio-input judge deployment must be available in the
project; installing the SDK alone does not enable audio scoring.

Only `FOUNDRY_PROJECT_ENDPOINT` and `FOUNDRY_MODEL_NAME` (the audio judge) are required.
When `FOUNDRY_DATASET_ID` is omitted, the samples upload the bundled short WAV to a
recording-folder dataset, build and upload one JSONL row referencing it, then delete
both created dataset versions after evaluation, including on failure. This path uses
the project's default Azure Storage connection and requires dataset upload permissions.

Optionally set `FOUNDRY_DATASET_ID` to your registered JSONL dataset ID to bypass uploads.
Existing datasets and recordings are never changed or deleted. To prepare your own inputs, adapt the existing
[dataset workflow](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/ai/azure-ai-projects/samples/datasets/sample_datasets.py): upload the recording folder
with a `file_pattern` that includes `.wav` (or omit the filter for a folder containing
only recordings), and set `data_file` to your JSONL file instead of the sample's
`.txt` file. Use separate dataset names for the recording folder and JSONL file.
Omit the sample's final dataset deletion calls until evaluation and any dataset
reuse are complete; both registered versions must remain available.
Each JSONL row contains a
reference to a recording in a versioned dataset asset; the transcript is optional:

```json
{
  "messages": [
    {"role": "user", "content": "When does the Springfield store close?"},
    {"role": "assistant", "content": "Which Springfield location do you mean?"}
  ],
  "conversation_artifacts": {
    "audio": {
      "asset_id": "azureai://accounts/<account>/projects/<project>/datasets/<dataset>/versions/1",
      "asset_file_path": "recordings/conversation.wav"
    }
  }
}
```

Use one compact object per line in the actual JSONL file. The reference must identify
the same account/project, use `/datasets/` in `asset_id`, and give the WAV member's relative
path. It is not a local path, SAS URL, or evaluator-local `audio_path`. The JSONL dataset ID
supplied to the run is separate from the recording reference inside each row.

Audio routing is selected by the evaluator's `builtin.*_audio` identity, not a run-level
modality flag. Do not supply grader `data_mapping` or `audio_path`. Conversation scope uses
the existing OpenAI client extension:

```python
extra_body={"evaluation_level": "conversation"}
```

[sample_voice_agent_simulation_evaluation.py](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/ai/azure-ai-projects/samples/evaluations/sample_voice_agent_simulation_evaluation.py)
and its [async version](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/ai/azure-ai-projects/samples/evaluations/sample_voice_agent_simulation_evaluation_async.py) instead generate
a short call against a voice agent, then grade its recording with
`builtin.task_completion_audio`. These simulation samples require `azure-ai-projects>=2.11.0`
for the voice-agent configuration models. Only the endpoint and audio-judge variables above are
required. By default, the sample creates a uniquely named, managed `gpt-realtime` voice
agent that knows the Springfield store's closing time, and deletes that version afterward,
including on failure. Set `FOUNDRY_VOICE_AGENT_MODEL` to override the managed voice model.
The simulator defaults to the `gpt-4.1` chat deployment and `en-US-AvaNeural` speech voice;
the project must have that chat deployment, or set `FOUNDRY_SIMULATOR_MODEL_NAME` to
another deployed chat model. Set `FOUNDRY_SIMULATOR_VOICE` to override the speech voice.
The audio judge is separate from the simulator; an audio-capable judge is not necessarily
a chat-compatible simulator model.

Optionally set `FOUNDRY_AGENT_NAME` to an **existing voice agent** to bypass creation.
`FOUNDRY_AGENT_VERSION` is optional and defaults to that agent's latest version; providing
a version requires an agent name. Existing agents are never changed or deleted.
The inline seed describes store-hours assistance: use an agent configured for that task,
or replace the seed with a task your agent supports.
The [voice-agent samples](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/ai/azure-ai-projects/samples/agents/voice/sample_voice_agent_basic.py) show the agent
configuration; keep the chosen agent/version available when running evaluation.
Set `FOUNDRY_AGENT_NAME` to that voice agent's name (`FOUNDRY_VOICE_AGENT_NAME` in
the voice-agent samples).
The simulator model generates user turns, the voice
renders simulated-user speech, and the audio judge grades the result; none is a substitute
for selecting the target agent. No dataset upload is needed for this single inline seed.

Both workflows poll for at most 10 minutes, print output items (scores, reasons, pass/fail)
and result counts, and clean up their evaluation/run resources even after errors.
A low score or failed grading threshold is not an execution error. The simulation also
generates billable calls and conversation dataset artifacts; those generated datasets
are not removed by evaluation cleanup. Audio grading is conversation-level;
turn-level audio grading and multi-tenant VNet execution are unsupported.

### Additional Scenarios

These samples require additional setup or Azure services:

| Sample | Description | Requirements |
|--------|-------------|--------------|
| [sample_evaluations_builtin_with_traces.py](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/ai/azure-ai-projects/samples/evaluations/sample_evaluations_builtin_with_traces.py) | Evaluate against Application Insights traces | Connected Application Insights on Foundry Project |
| [sample_scheduled_evaluations.py](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/ai/azure-ai-projects/samples/evaluations/sample_scheduled_evaluations.py) | Schedule recurring evaluations | RBAC setup |
| [sample_continuous_evaluation_rule.py](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/ai/azure-ai-projects/samples/evaluations/sample_continuous_evaluation_rule.py) | Set up continuous evaluation rules | RBAC Setup |
| [sample_trace_evaluation_rule.py](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/ai/azure-ai-projects/samples/evaluations/sample_trace_evaluation_rule.py) | Evaluate an agent's traces on a recurring schedule with an evaluation rule | RBAC setup, connected Application Insights, existing agent |
| [sample_dataset_evaluation_rule.py](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/ai/azure-ai-projects/samples/evaluations/sample_dataset_evaluation_rule.py) | Evaluate an agent on a fixed set of queries on a recurring schedule with an evaluation rule | RBAC setup |
| [sample_evaluations_score_model_grader_with_image.py](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/ai/azure-ai-projects/samples/evaluations/sample_evaluations_score_model_grader_with_image.py) | Evaluate with image data | Image file |
| [sample_evaluations_score_model_grader_with_image_model_target.py](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/ai/azure-ai-projects/samples/evaluations/sample_evaluations_score_model_grader_with_image_model_target.py) | Evaluate image data using a model as the target | Image file, vision-capable model deployment |
| [sample_evaluations_score_model_grader_with_audio.py](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/ai/azure-ai-projects/samples/evaluations/sample_evaluations_score_model_grader_with_audio.py) | Evaluate with audio data | Audio file, audio-capable model deployment |
| [sample_evaluations_score_model_grader_with_audio_model_target.py](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/ai/azure-ai-projects/samples/evaluations/sample_evaluations_score_model_grader_with_audio_model_target.py) | Evaluate audio data using a model as the target | Audio file, audio-capable model deployment |
| [sample_evaluations_builtin_with_inline_data_oai.py](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/ai/azure-ai-projects/samples/evaluations/sample_evaluations_builtin_with_inline_data_oai.py) | Use OpenAI client directly | OpenAI SDK |
| [sample_human_evaluations.py](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/ai/azure-ai-projects/samples/evaluations/sample_human_evaluations.py) | Emit human evaluation events (binary / Likert-5) as OpenTelemetry custom events to Application Insights | Connected Application Insights on Foundry Project, `azure-monitor-opentelemetry` |

### Evaluator Types

| Sample | Description |
|--------|-------------|
| [sample_evaluations_graders.py](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/ai/azure-ai-projects/samples/evaluations/sample_evaluations_graders.py) | OpenAI graders: label_model, text_similarity, string_check, score_model |
| [sample_evaluations_graders_async.py](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/ai/azure-ai-projects/samples/evaluations/sample_evaluations_graders_async.py) | Async version of OpenAI graders: label_model, text_similarity, string_check, score_model |
| [sample_evaluations_ai_assisted.py](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/ai/azure-ai-projects/samples/evaluations/sample_evaluations_ai_assisted.py) | AI-assisted and NLP-based evaluators: Similarity, ROUGE, METEOR, GLEU, F1, BLEU |
| [sample_eval_catalog_code_based_evaluators.py](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/ai/azure-ai-projects/samples/evaluations/sample_eval_catalog_code_based_evaluators.py) | Custom code-based (inline) evaluators |
| [sample_eval_catalog_prompt_based_evaluators.py](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/ai/azure-ai-projects/samples/evaluations/sample_eval_catalog_prompt_based_evaluators.py) | Custom prompt-based evaluators |

### Rubric Evaluators

| Sample | Description |
|--------|-------------|
| [sample_rubric_evaluator_manual.py](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/ai/azure-ai-projects/samples/evaluations/sample_rubric_evaluator_manual.py) | Hand-author a rubric evaluator (dimensions, weights, pass threshold) with `create_version`, then use it in an OpenAI eval run |
| [sample_rubric_evaluator_generation_basic.py](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/ai/azure-ai-projects/samples/evaluations/sample_rubric_evaluator_generation_basic.py) | Generate an evaluator from a single prompt source, inspect the produced dimensions, and use the auto-saved evaluator in an eval run |
| [sample_rubric_evaluator_generation_all_sources.py](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/ai/azure-ai-projects/samples/evaluations/sample_rubric_evaluator_generation_all_sources.py) | Exercise every source type — prompt + agent + dataset in a combined job, plus a separate traces + agent-companion job |
| [sample_rubric_evaluator_generation_iterate.py](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/ai/azure-ai-projects/samples/evaluations/sample_rubric_evaluator_generation_iterate.py) | Human-in-the-loop iteration: generate v1, edit dimensions locally, save as v2 with `create_version` |
| [sample_rubric_evaluator_generation_lifecycle.py](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/ai/azure-ai-projects/samples/evaluations/sample_rubric_evaluator_generation_lifecycle.py) | Full generation-job lifecycle: idempotent `create_generation_job`, polling, list, and delete |

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


### Endpoint-Based (Custom) Evaluators

| Sample | Description | Requirements |
|--------|-------------|--------------|
| [sample_endpoint_evaluator.py](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/ai/azure-ai-projects/samples/evaluations/sample_endpoint_evaluator.py) | Bring your own HTTP endpoint as an evaluator, authenticated with an API key or Entra ID | Scoring endpoint, project connection |
| [sample_endpoint_evaluator_schema_0_0_1.py](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/ai/azure-ai-projects/samples/evaluations/sample_endpoint_evaluator_schema_0_0_1.py) | Register an endpoint evaluator for an existing endpoint that uses the older 0.0.1 contract. Use 0.0.2 for new evaluators | Scoring endpoint, project connection |

### Evaluation Result Insights & Analysis

| Sample | Description |
|--------|-------------|
| [sample_evaluation_compare_insight.py](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/ai/azure-ai-projects/samples/evaluations/sample_evaluation_compare_insight.py) | Compare evaluation runs and generate statistics |
| [sample_evaluation_cluster_insight.py](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/ai/azure-ai-projects/samples/evaluations/sample_evaluation_cluster_insight.py) | Analyze evaluation runs with cluster insights |
