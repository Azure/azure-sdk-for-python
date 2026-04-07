## Welcome to Bug Bash for Azure AI Evaluation SDK

### Bug Bash: Custom & Friendly Evaluator Upload (`azure-ai-projects` SDK)

### Important Region Constraint
- This feature works for projects in the `TIP` environment hosted in the `West US 2` region.
- Project endpoint: `https://np-wus2-resource.services.ai.azure.com/api/projects/np-wus2`

### Feature Overview
This feature enables users to:

- Upload custom evaluators with user-defined evaluation logic.
- Upload friendly evaluators defined through evaluator metadata and prompt/scoring configuration.
- Run evaluations via SDK after uploading evaluators through the SDK.
- Upload evaluators through the SDK and then select and run them from Azure AI Studio UI.
- Create an evaluation definition through the Evaluations REST API and monitor the run through API and/or Azure AI Studio.
- Validate that evaluation outputs match the scoring logic, labels, thresholds, and other result fields defined by the evaluator.

### Supported Workflows
- `SDK -> SDK`: Upload evaluator using SDK and run evaluations using SDK.
- `SDK -> UI`: Upload evaluator using SDK, then select and run the evaluator from Azure AI Studio UI.
- `API -> API/UI`: Create an evaluation definition, including testing criteria, using the Evaluations REST API, then monitor results via API and/or Azure AI Studio.

### Primary Validation Goal
This bug bash is not limited to upload and registration. The main validation target is end-to-end correctness:

- the evaluator uploads successfully
- the evaluator can be selected and invoked successfully
- the evaluation run completes successfully
- the returned evaluation results match the evaluator definition
- labels, scores, thresholds, reasoning, and other evaluator-defined properties are preserved correctly in the final results

### Note
- Uploading evaluators via UI is not supported, evaluator upload must be done through the SDK.

### References
The bug bash scenarios are based on the following SDK samples:

- Simple custom evaluator upload sample:
  [sample_custom_eval_upload_simple.py](https://github.com/Azure/azure-sdk-for-python/blob/bug-bash/custom-evaluator/sdk/ai/azure-ai-projects/samples/evaluations/sample_custom_eval_upload_simple.py)
- Advanced custom evaluator upload sample:
  [sample_custom_eval_upload_advanced.py](https://github.com/Azure/azure-sdk-for-python/blob/bug-bash/custom-evaluator/sdk/ai/azure-ai-projects/samples/evaluations/sample_custom_eval_upload_advanced.py)
- Azure OpenAI custom evaluator upload sample (uses `AzureOpenAI` client with service-injected `model_config`):
  [sample_custom_eval_upload_more_friendly.py](https://github.com/Azure/azure-sdk-for-python/blob/bug-bash/custom-evaluator/sdk/ai/azure-ai-projects/samples/evaluations/sample_custom_eval_upload_more_friendly.py)

## Instructions

### 1. Setup Virtualenv

#### Recommended path
```bash
python -m venv .bugbashenv
```

#### Linux based
```bash
source .bugbashenv/bin/activate
```

#### Windows
```bash
.bugbashenv\Scripts\activate
```

### 2. Clone the Repository and Checkout the Bug Bash Branch
```bash
git clone https://github.com/Azure/azure-sdk-for-python.git
cd azure-sdk-for-python
git checkout bug-bash/custom-evaluator
```

### 3. Install Dependencies From the Branch

Authenticate with Azure:

```bash
az login
```

Install the `azure-ai-projects` SDK package directly from this branch (editable mode):

```bash
pip install -e sdk/ai/azure-ai-projects
```

Navigate to the samples:

```bash
cd sdk/ai/azure-ai-projects/samples/evaluations
```

### 4. Running the Tests

Run the unit tests for the `azure-ai-projects` package to verify everything works:

```bash
# From the repo root
cd sdk/ai/azure-ai-projects

# Install test dependencies
pip install -r dev_requirements.txt

# Run the tests
python -m pytest tests/ -v
```

### 5. Confirm Project Prerequisites
Make sure all of the following are true:

- You have an Azure subscription with access to Azure AI Projects.
- Your Azure AI Project is in the `TIP` environment hosted in the `West US 2` region.
- The project is visible in `https://ai.azure.com`.
- You are using Python 3.9 or later.
- Your authentication method is ready, such as Azure CLI login or service principal.

### 5.1 Shared Project Option
If you do not have your own Azure AI Project available for the bug bash, you can use the shared `np-wus2` project.

- ask the team for access to the `np-wus2` project if you do not already have it
- use `np-wus2` as your project for upload, evaluation runs, and result validation if you do not have your own project
- `np-wus2` is in the `TIP` environment hosted in `West US 2`
- project endpoint: `https://np-wus2-resource.services.ai.azure.com/api/projects/np-wus2`
- fetch the API key from the project before running the samples

### 6. Azure AI Project Configuration
Configure the sample with your project connection details before running it.

At minimum, verify:

- project endpoint or project connection settings
- API key fetched from the project URL
- model names are explicitly filled in by the user for the samples they run
- evaluator name
- evaluator version
- evaluator definition or evaluator logic
- test inputs with known expected outputs

If you are using the shared project, configure the samples against `np-wus2` after access has been granted, use `https://np-wus2-resource.services.ai.azure.com/api/projects/np-wus2` as the endpoint, and explicitly fill in the model variables required by the sample you are running.

### 6.1 Required Variables For The Provided Samples
For the provided samples, configure these values:

- `FOUNDRY_PROJECT_ENDPOINT=https://np-wus2-resource.services.ai.azure.com/api/projects/np-wus2`
- `FOUNDRY_MODEL_NAME=<fill this in>`
- `OPENAI_MODEL=<fill this in>`
- fetch the API key from the shared project URL and use it for the sample that requires `OPENAI_API_KEY`

Do not rely on defaults for model configuration. Fill in `FOUNDRY_MODEL_NAME` and `OPENAI_MODEL` explicitly before running the samples.

### 6.2 Using Your Own Custom Evaluator
Bug bash participants can use their own defined custom evaluators in addition to the provided samples.

Use the following naming format:

- evaluator class name: `CustomNameEvaluator`
- evaluator file name: `custom_name_evaluator.py`

Validate that:

- the class name follows the `CustomNameEvaluator` pattern
- the Python file follows the `custom_name_evaluator.py` pattern
- the evaluator definition is consistent with the expected output fields you want to validate during the run

### 7. Prepare Validation Inputs
Before running the bug bash, prepare a small set of prompts or dataset rows where the expected evaluator output is known ahead of time.

Examples:

- an input that should clearly pass
- an input that should clearly fail
- an input that should produce a specific label
- an input that should exercise threshold boundaries
- an input that should produce evaluator-specific metadata or properties

## Bug Bash Scenarios

### Scenario 1: Upload Custom Evaluator via SDK

#### Goal
Validate uploading a custom evaluator, ensuring it is registered successfully, and confirming that evaluation runs return the expected outputs defined by that evaluator.

This scenario applies both to the provided sample evaluator and to a user-defined custom evaluator that follows the required class and file naming format.

#### Steps
Open the sample:

```bash
python sample_custom_eval_upload_simple.py
```

Configure:

- project connection details
- evaluator name and version
- custom evaluator logic
- validation inputs with known expected results

#### Expected Results
- Evaluator upload completes without error.
- Evaluator appears in SDK list APIs.
- Evaluator appears in Azure AI Studio UI under Evaluators.
- Evaluation runs using the uploaded evaluator complete successfully.
- Output fields returned by the run match the evaluator definition.
- Any evaluator-defined score, label, threshold, reasoning, or custom properties are returned with the expected values.

#### What to Test
- invalid evaluator schema
- duplicate evaluator names
- versioning behavior
- deterministic inputs that should return known results
- mismatches between evaluator logic and actual returned outputs
- missing or incorrectly mapped result fields

### Scenario 2: Upload Advanced Custom Evaluator via SDK

#### Goal
Validate uploading a more advanced custom evaluator definition and confirming that evaluation runs using it return the expected outputs from the configured definition.

#### Steps
Open the sample:

```bash
python sample_custom_eval_upload_advanced.py
```

Configure:

- advanced evaluator metadata or configuration
- evaluator logic and output definition
- validation inputs with known expected results

#### Expected Results
- Advanced custom evaluator uploads successfully.
- Evaluator is selectable in Azure AI Studio UI.
- Evaluation runs complete successfully.
- Returned labels, scores, thresholds, and reasoning align with the evaluator configuration.
- Any additional evaluator-defined output fields are present and correct.

#### What to Test
- missing required fields
- invalid evaluator configuration
- evaluator discoverability in UI
- incorrect scoring or labeling behavior
- incorrect threshold application
- result payloads that do not match the evaluator definition

### Scenario 3: Upload Azure OpenAI Custom Evaluator via SDK (MoreFriendlyEvaluator)

#### Goal
Validate uploading a custom evaluator that uses `AzureOpenAI` (instead of the plain OpenAI client) with a service-injected `model_config`. The evaluator's `__init__` accepts `model_config: dict`, and the evaluation run only passes `deployment_name` — the service automatically resolves it into a full `model_config` dict containing `azure_endpoint`, `api_key`, `api_version`, and `azure_deployment`.

#### Steps
Open the sample:

```bash
python sample_custom_eval_upload_more_friendly.py
```

Configure:

- `FOUNDRY_PROJECT_ENDPOINT` — your project endpoint
- `FOUNDRY_MODEL_NAME` — the model deployment name in the project (e.g. `gpt-4o-mini`)

#### Expected Results
- Evaluator upload completes without error.
- The service resolves `deployment_name` into `model_config` and injects it into the evaluator.
- The `AzureOpenAI` client is constructed successfully from the injected config.
- Evaluation run completes with correct friendliness scores (1-5), labels (pass/fail at threshold=3), reasons, and properties (explanation, tone, confidence).
- Results are consistent with the FriendlyEvaluator (Scenario 2) for the same test inputs.

#### What to Test
- verify `model_config` injection works end to end
- test with different deployment names
- confirm scores, labels, and properties match expected values
- verify the evaluator appears in Azure AI Studio under Evaluators
- compare results against the FriendlyEvaluator to ensure parity

### Scenario 4: Run Evaluation via UI with SDK-Uploaded Evaluator

#### Goal
Ensure evaluators uploaded via SDK can be used in Azure AI Studio UI and that the final evaluation results are correct.

#### Steps
- Navigate to `https://ai.azure.com`.
- Open the project in the `TIP` environment hosted in `West US 2`.
- Go to Evaluations.
- Create a new evaluation run.
- Select the SDK-uploaded evaluator.
- Choose a dataset or inputs.
- Run the evaluation.
- Compare the resulting outputs against the expected values from the evaluator definition.

#### Expected Results
- Evaluation run starts successfully.
- Results are generated and visible in the UI.
- Metrics match expectations from evaluator logic.
- Result fields are not missing, renamed incorrectly, or assigned incorrect values.

### Scenario 5: Validate Result Correctness End to End

#### Goal
Confirm that evaluator execution returns the proper results defined in the evaluator definition, not just that the run succeeds.

#### Validation Checklist
- score values are correct for the given test inputs
- labels are correct for the given test inputs
- thresholds are applied correctly
- pass/fail outcomes are correct where applicable
- reasoning or explanation fields are returned when defined
- custom properties or evaluator-specific fields are returned when defined
- results are consistent between SDK and UI views of the same evaluation run

#### Failure Cases to Capture
- run succeeds but returned values are wrong
- expected fields are missing from results
- field names differ from the evaluator definition
- values are present but assigned to the wrong result fields
- UI and SDK show different outputs for the same run

## Known Limitations
- Evaluator upload is SDK-only.
- Feature is `TIP` region (`West US 2`) only.
- Uploading evaluators directly through the UI is not supported.

## Feedback to Capture
During bug bash, please report:

- SDK usability issues
- error message clarity
- UI discoverability of evaluators
- documentation gaps
- region-related confusion or failures
- support issues for user-defined evaluators authored and uploaded by customers
- result correctness issues where the evaluation completed but the outputs did not match the evaluator definition
- field mapping issues for labels, scores, thresholds, explanations, or custom properties

## Reporting Bugs
When filing bugs, include:

- project region
- evaluator used
- SDK version
- full error messages or stack traces
- repro steps
