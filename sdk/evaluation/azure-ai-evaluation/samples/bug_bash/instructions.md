# Agent Evaluators Bug Bash Instructions

## Welcome to Agent Evaluators Bug Bash!

### Prerequisites
- Azure Open AI Endpoint
- Open AI Model Deployment that supports `chat completion`
- Azure AI Project
  - For local to remote tracking

### Clone the repo
```bash
git clone -b prp/agent_evaluators https://github.com/Azure/azure-sdk-for-python

# Navigate to bug bash folder in repo with instructions and samples
cd azure-sdk-for-python\sdk\evaluation\azure-ai-evaluation\samples\bug_bash
```

### Installation Instructions:

1. Create a **virtual environment of you choice**. To create one using conda, run the following command:
    ```bash
    conda create -n agent-evals-bug-bash python=3.11
    conda activate agent-evals-bug-bash
    ```
2. Install the required packages by running the following command:
    ```bash
   pip install -r requirements.txt
    ```
3. To run the examples from the notebook, please install the kernel in your environment:
   ```bash
   python -m ipykernel install --user --name agent-evals-bug-bash --display-name "agent-evals-bug-bash"
   ```
4. Select the newly installed kernel in the Jupyter notebook.

### Report Bugs

Please use the following template to report bugs : [**Bug Template**](https://msdata.visualstudio.com/3adb301f-9ede-41f2-933b-fcd1a486ff7f/_workitems/create/Bug?templateId=9079923c-1e6d-4341-be65-a0665e17f0d7&ownerId=8d25f9a6-0175-4ac6-8d4e-c1e2702a635c)

### Sample Notebooks

- [**Run Agent and Evaluate using Evaluation SDK**](./agent_evaluation.ipynb)
