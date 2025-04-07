# Agent Evaluators Instructions

A general agent workflow typically contains a linear workflow of intent resolution, tool calling, and final response, at a minimum. We abstracted these evaluation aspects to enable observability user for users into an agent system. We provide native integration with Azure AI agents so that Azure users can seamlessly evaluate their agents. Other users can still follow our input schema to use our evaluator. We enable evaluation support for agent system on these aspects:
- Intent resolution measures the extent of which an agent identifies the correct intent from a user query. 
- Task adherence measures the extent of which an agent’s final response adheres to the task based on its system message and a user query.
- Response completeness measures the extent of which an agent or RAG response is complete (does not miss critical information) compared to the ground truth.

## Getting started

### Prerequisites
- Python 3.9 or later is required to use this package.
- Azure Open AI Model Deployment that supports `chat completion`  to use AI-assisted evaluators
- (Optional) Azure AI Project
  - If you want to log results to the Foundry Evaluation UI


### Clone the repo
```bash
git clone https://github.com/Azure/azure-sdk-for-python

# Navigate to the repo folder with samples
cd azure-sdk-for-python/sdk/evaluation/azure-ai-evaluation/samples/agent_evaluators/
```

### Installation Instructions:

1. Create a **virtual environment of you choice**. To create one using conda, run the following command:
    ```bash
    conda create -n agent-evals python=3.11
    conda activate agent-evals
    ```
2. Install the required packages by running the following command:
    ```bash
   pip install "git+https://github.com/Azure/azure-sdk-for-python.git@main#egg=azure-ai-evaluation&subdirectory=sdk/evaluation/azure-ai-evaluation" azure-ai-projects ipykernel azure-identity
    ```
3. To run the examples from the notebook, please install the kernel in your environment:
   ```bash
   python -m ipykernel install --user --name agent-evals --display-name "agent-evals"
   ```
4. Select the newly installed kernel in the sample Jupyter notebook.
