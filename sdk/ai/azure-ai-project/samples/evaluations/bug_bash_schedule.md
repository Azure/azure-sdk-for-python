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
    pip uninstall azure-ai-project azure-ai-ml azure-ai-evaluation

   pip install azure-identity azure-ai-ml
   # installing azure-ai-evaluation
   pip install https://remoteevalbugbash.blob.core.windows.net/remoteevalbugbash/azure_ai_evaluation-1.0.0a20241022005-py3-none-any.whl
   # installing azure-ai-project
   pip install https://remoteevalbugbash.blob.core.windows.net/remoteevalbugbash/azure_ai_project-1.0.0b1-py3-none-any.whl
    ```

### How to Get `Connection String` for the Project ?
Connection string is needed to easily create `AIProjectClient` object. You can get the connection string from the project overview page. Here is the [link]() to the project overview page.

### Samples
1. Online Evaluation - [Sample Link](./sample_evaluations_schedules.py). This sample demonstrates how to evaluate continuously by running evaluation on a schedule.