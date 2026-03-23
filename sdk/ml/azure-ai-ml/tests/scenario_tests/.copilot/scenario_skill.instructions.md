---
description: "Generate complex, production-grade customer scenario tests for azure-ai-ml SDK"
---

# Azure AI ML SDK – Scenario Test Generator

## Goal

Generate **complex, end-to-end customer scenario tests** that mirror real production
usage patterns from https://github.com/Azure/azureml-examples/tree/main/sdk/python.

These are NOT unit tests. Each scenario is a **multi-step workflow** that exercises
the SDK the same way a customer would in production: create resources → configure →
submit work → validate results → clean up.

---

## When to Use This Skill

Use this skill when someone asks you to:
- Create a new scenario test for the azure-ai-ml SDK
- Add a customer workflow test
- Validate that a customer pattern still works after SDK changes
- Write an end-to-end test for a specific feature area

---

## Architecture

### File location
All scenario tests live under:
```
sdk/ml/azure-ai-ml/tests/scenario_tests/
```

### Shared fixtures (conftest.py)
The conftest.py provides:
- `credential` – session-scoped, tries SP auth then CLI then DefaultAzureCredential
- `subscription_id`, `resource_group`, `workspace_name` – from env vars
- `ml_client` – session-scoped MLClient for the workspace
- `rand_name(prefix)` – generates collision-safe resource names
- `wait_for_job(ml_client, job, timeout)` – polls job to terminal state

### Environment variables required
```
ML_SUBSCRIPTION_ID, ML_RESOURCE_GROUP, ML_WORKSPACE_NAME
ML_TENANT_ID, ML_CLIENT_ID, ML_CLIENT_SECRET  (optional, for SP auth)
```

---

## Scenario Categories & Complexity Levels

### Level 1 – Resource Management (infrastructure setup)
Patterns from `azureml-examples/sdk/python/resources/`:
- Workspace with managed network (AIO → AOAO isolation, outbound rules, provisioning)
- Compute cluster lifecycle (create → scale → update → delete)
- Datastore CRUD with different credential types
- Workspace connections (Azure OpenAI, custom, etc.)

### Level 2 – Asset Lifecycle (model/data/env/component management)
Patterns from `azureml-examples/sdk/python/assets/`:
- Environment creation from conda YAML, Docker context, curated
- Model registration from local path, job output, MLflow
- Data asset creation (uri_file, uri_folder, mltable)
- Component creation from YAML, Python function decorators
- **Cross-workspace sharing via Registry** (create in registry → use in workspace)

### Level 3 – Job Workflows (training & pipelines)
Patterns from `azureml-examples/sdk/python/jobs/`:
- Command job: create env + submit training script + get metrics
- Pipeline job: load components → wire inputs/outputs → submit → stream
- Sweep job: hyperparameter tuning with search space
- AutoML job: classification/regression with data input
- Distributed training job: PyTorch/TF with multi-node

### Level 4 – Deployment & Inference (online/batch endpoints)
Patterns from `azureml-examples/sdk/python/endpoints/`:
- **Blue-green deployment**: create endpoint → deploy v1 → deploy v2 → shift traffic → delete old
- Batch endpoint: create → deploy → invoke with data asset → get results
- Model package deployment from registry
- MLflow no-code deployment

### Level 5 – Compound Workflows (multiple areas combined)
These are the most valuable scenarios:
- **Train → Register → Deploy**: pipeline job trains model → register in workspace → deploy to online endpoint → invoke → cleanup
- **Registry cross-workspace**: create env & component in registry → use component in workspace pipeline job → register model in registry → deploy from registry to workspace endpoint
- **Managed network workspace**: create workspace with managed VNet → add outbound rules (ServiceTag, FQDN, PE) → provision network → run job → cleanup
- **Data pipeline**: create datastore → upload data → create data asset → pipeline job references data → output to datastore

---

## Template for a Scenario Test

```python
# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Scenario: <TITLE – one line describing the end-to-end customer workflow>

Mirrors the customer pattern from:
  <LINK to azureml-examples notebook or doc>

Customer story:
  <2-3 sentences describing WHY a customer does this, what business problem it solves>

Steps:
  1. <step>
  2. <step>
  ...
  N. Clean up all created resources
"""

import pytest
import time

from azure.ai.ml import MLClient, Input, command, load_component
from azure.ai.ml.entities import (
    # Import only what this scenario needs
)
from azure.ai.ml.constants import AssetTypes


class TestScenario<Name>:
    """<One-line description matching the docstring title>"""

    def test_<workflow_name>(self, ml_client: MLClient, rand_name, <other fixtures>):
        """<Describe the end-to-end flow in one sentence>"""

        # ── Step 1: Setup / Create prerequisites ──────────────────
        # Create compute, environment, data assets, etc.

        # ── Step 2: Core workflow ─────────────────────────────────
        # Submit job, create endpoint, etc.

        # ── Step 3: Validate results ──────────────────────────────
        # Assert on status, properties, outputs

        # ── Step 4: Cleanup ───────────────────────────────────────
        # Delete all resources created in this test
        # Use try/finally to ensure cleanup happens even on failure
```

---

## Rules for Writing Scenarios

### DO:
1. **Use `try/finally`** for cleanup – every resource created MUST be deleted
2. **Use `rand_name("prefix")`** for all resource names to avoid collisions
3. **Assert on real properties** – not just "is not None", check actual values
   (name matches, status is correct, type is right)
4. **Chain multiple operations** – a single test should do 5-15 API calls minimum
5. **Use the SDK the way customers do** – follow the patterns from azureml-examples
6. **Include realistic entities** – real conda specs, real Docker images, real scripts
7. **Wait for async operations** – use `.result()` on LRO pollers, use `wait_for_job`
8. **Test round-trip fidelity** – create → get → verify properties match
9. **Reference azureml-examples link** in docstring

### DON'T:
1. **Don't write unit tests** – no mocking, no patching, no fake responses
2. **Don't test single API calls** – each scenario must be a multi-step workflow
3. **Don't skip cleanup** – leaked resources cost money and block future runs
4. **Don't hardcode resource names** – always use `rand_name()`
5. **Don't hardcode compute/env names** that may not exist – create what you need
6. **Don't assume specific workspace state** – scenario should be self-contained

### Inline training scripts:
For command jobs, embed small training scripts inline or create them in a
temp directory during the test:

```python
import tempfile, os

with tempfile.TemporaryDirectory() as code_dir:
    script = os.path.join(code_dir, "train.py")
    with open(script, "w") as f:
        f.write('''
import argparse
parser = argparse.ArgumentParser()
parser.add_argument("--learning-rate", type=float, default=0.01)
args = parser.parse_args()
print(f"Training with lr={args.learning_rate}")
# simulate training
import time; time.sleep(5)
print("Training complete")
''')
    job = command(
        code=code_dir,
        command="python train.py --learning-rate ${{inputs.lr}}",
        inputs={"lr": 0.01},
        environment="azureml:AzureML-sklearn-1.0-ubuntu20.04-py38-cpu@latest",
        compute="cpu-cluster",
    )
    submitted = ml_client.jobs.create_or_update(job)
```

### Endpoint testing:
For online endpoints, embed a minimal scoring script:

```python
score_script = '''
import json, os
def init():
    pass
def run(data):
    return json.dumps({"result": "ok"})
'''
```

---

## Naming Convention

| File | Pattern |
|------|---------|
| Simple workflow | `test_scenario_<area>.py` |
| Complex multi-area | `test_scenario_<primary>_to_<secondary>.py` |
| Network/security | `test_scenario_<feature>_network.py` |
| Registry | `test_scenario_registry_<workflow>.py` |

Examples:
- `test_scenario_train_to_deploy.py` – train model, register, deploy, invoke
- `test_scenario_registry_cross_workspace.py` – registry assets across workspaces
- `test_scenario_managed_network.py` – workspace with managed VNet
- `test_scenario_pipeline_with_components.py` – multi-step pipeline
- `test_scenario_blue_green_deployment.py` – safe rollout with traffic shifting
- `test_scenario_sweep_hyperparameter.py` – hyperparameter tuning

---

## How to Run

```bash
# Run a single scenario
pytest tests/scenario_tests/test_scenario_train_to_deploy.py -v -x

# Run all scenarios
pytest tests/scenario_tests/ -v

# Run with specific timeout (some scenarios are long)
pytest tests/scenario_tests/ -v --timeout=1200
```

---

## Checklist Before Submitting a Scenario

- [ ] Scenario mirrors a real azureml-examples pattern
- [ ] Docstring explains customer story and links to source example
- [ ] All resources created are cleaned up in `finally` block
- [ ] All names use `rand_name()` for uniqueness
- [ ] Assertions check real property values, not just existence
- [ ] Test exercises 5+ SDK API calls in a single test method
- [ ] No mocking – runs fully live
- [ ] Imports are minimal (only what the scenario uses)
