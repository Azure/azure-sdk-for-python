# Sample Red Team

This file demonstrates how to use the synchronous methods to create, get, list, and run Red Team scans using the Azure AI Project SDK.

## Prerequisites

Before running this sample, ensure you have the following:
- Python 3.8 or later.
- The Azure AI Project SDK installed. You can install it using:
  ```bash
  pip install azure-ai-projects azure-identity
  ```
- Set the following environment variables with your own values:
  - `PROJECT_ENDPOINT`: The Azure AI Project endpoint, as found in the overview page of your Azure AI Foundry project.
  - `AZURE_OPENAI_DEPLOYMENT`: Your Azure OpenAI deployment name.

---

```python
# Import required libraries
import os
from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import (
    RedTeam,
    AzureOpenAIModelConfiguration,
    AttackStrategy,
    RiskCategory,
)
```

---

## Set Environment Variables

Ensure the following environment variables are set before proceeding.

```python
endpoint = os.environ["PROJECT_ENDPOINT"]  # Example: https://<account_name>.services.ai.azure.com/api/projects/<project_name>
model_deployment_name = os.environ["AZURE_OPENAI_DEPLOYMENT"]
```

---

## Authenticate and Initialize the Client

```python
credential = DefaultAzureCredential(exclude_interactive_browser_credential=False)
project_client = AIProjectClient(endpoint=endpoint, credential=credential)
```

---

## Create and Run a Red Team Scan

This section demonstrates how to create a Red Team scan for direct model testing.

```python
# Create a Red Team scan
print("Creating a Red Team scan for direct model testing")

# Create target configuration for testing an Azure OpenAI model
target_config = AzureOpenAIModelConfiguration(model_deployment_name=model_deployment_name)

# OR create target configuration for inline callback
target_config = InLineCallbackConfiguration(callback={
     "type": "InLineCallback",
     "function": "print('Red Team inline scan')",
})

# OR create target configuration for callback file
callback = project_client.datasets.upload_file(
    name=callback_name,
    version="1",
    file="./samples_folder/callback.py",
)
target_config = CallbackConfiguration(callback_id=callback.id)

# Create the Red Team configuration
red_team = RedTeam(
    attack_strategies=[AttackStrategy.BASE64],
    risk_categories=[RiskCategory.VIOLENCE],
    display_name="redteamtest1",  # Use a simpler name
    target=target_config,
)

# Create and run the Red Team scan
red_team_response = project_client.red_teams.create(red_team=red_team)
print(f"Red Team scan created with scan name: {red_team_response.name}")
```

---

## Get Red Team Scan Details

Retrieve the details of the created Red Team scan.

```python
print("Getting Red Team scan details")
get_red_team_response = project_client.red_teams.get(name=red_team_response.name)
print(f"Red Team scan status: {get_red_team_response.status}")
```

---

## List All Red Team Scans

List all Red Team scans in the project.

```python
print("Listing all Red Team scans")
for scan in project_client.red_teams.list():
    print(f"Found scan: {scan.name}, Status: {scan.status}")
```