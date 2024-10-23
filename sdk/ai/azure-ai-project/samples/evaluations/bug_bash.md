## Welcome to the Evaluation in Cloud Bug Bash!

### Prerequisites
- Azure AI Project in `EastUS2` region
- Azure Open AI Deployment with GPT model supporting `chat completion`. Example `gpt-4`

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
    pip uninstall azure-ai-project azure-ai-ml azure-ai-evaluation

   pip install azure-identity azure-ai-ml
   # installing azure-ai-evaluation
   pip install https://remoteevalbugbash.blob.core.windows.net/remoteevalbugbash/azure_ai_evaluation-1.0.0a20241022005-py3-none-any.whl
   # installing azure-ai-project
   pip install https://remoteevalbugbash.blob.core.windows.net/remoteevalbugbash/azure_ai_project-1.0.0b1-py3-none-any.whl
    ```

### Report Bugs

Please use the following template to report bugs : [**Bug Template**](https://msdata.visualstudio.com/Vienna/_workitems/create/Bug?templateId=5f8cafcf-2bbc-42df-a0ba-13c3ebcbeabe&ownerId=31cd3b44-f331-4377-95dd-2f8d6e169ee4)

### Sample Notebooks

1. Remote Evaluation - [Sample Link](./sample_evaluations.py). This sample demonstrates how to create a new evaluation in cloud.
2. Online Evaluation - [Sample Link](./sample_evaluations_schedules.py). This sample demonstrates how to evaluate continuously by running evaluation on a schedule.
