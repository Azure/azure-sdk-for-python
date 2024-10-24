## Welcome to the Evaluation in Cloud with schedules Bug Bash!

### Prerequisites
- Azure AI Project in `EastUS2` region

### Resources


### Clone the repository
```bash
git clone https://github.com/Azure/azure-sdk-for-python.git
# Navigate to cloned repo folder
git pull
git checkout users/singankit/remote_evaluation_bug_bash
```

### Installation Instructions:

1. Create a **virtual environment of you choice**. To create one using conda, run the following command:
    ```bash
    conda create -n remote-evaluation-bug-bash python=3.11
    conda activate remote-evaluation-bug-bash
    ```
2. Install the required packages by running the following command:
    ```bash
   # Clearing any old installation
    pip uninstall azure-ai-project azure-ai-ml

   pip install azure-identity azure-ai-ml
   # installing azure-ai-project
   pip install https://remoteevalbugbash.blob.core.windows.net/remoteevalbugbash/azure_ai_project-1.0.0b1-py3-none-any.whl
    ```

### How to Get `Connection String` for the Project ?
Connection string is needed to easily create `AIProjectClient` object. You can get the connection string from the project overview page. Here is the [link](https://int.ai.azure.com/build/overview?wsid=/subscriptions/72c03bf3-4e69-41af-9532-dfcdc3eefef4/resourceGroups/shared-online-evaluation-rg/providers/Microsoft.MachineLearningServices/workspaces/ignite-eval-schedule-bugbash&tid=72f988bf-86f1-41af-91ab-2d7cd011db47) to the project overview page.

### Instructions for pushing application insights data


### Instructions to view enriched data

### Samples
1. Online Evaluation - [Sample Link](./sample_evaluations_schedules.py). This sample demonstrates how to evaluate continuously by running evaluation on a schedule.