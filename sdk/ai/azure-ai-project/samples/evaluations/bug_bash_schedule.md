## Welcome to the Bug Bash for Evaluation in Cloud with Schedules!

### Environment
- Online Evaluation Service & Azure AI Project deployed in `EastUS2` region

### How To Get Started

#### Azure SDK Setup
```bash
git clone https://github.com/Azure/azure-sdk-for-python.git
# Navigate to cloned repo folder
git pull
git checkout users/singankit/remote_evaluation_bug_bash
```

#### Python Environment Creation Instructions:

1. Create a **virtual environment of you choice**. To create one using conda, run the following command:

    ```bash
    conda create -n online-evaluation-bug-bash python=3.11
    conda activate online-evaluation-bug-bash
    ```
2. Install the required packages by running the following command:

    ```bash
   # Clearing any old installation
    pip uninstall azure-ai-project azure-ai-ml

   pip install azure-identity azure-ai-ml
   # Optional: Upgrade pip if any issues occur in above two steps (pip install --upgrade pip)
   # installing azure-ai-project, SDK is same for remote, if already installed please ignore.
   pip install https://onlineevalbugbash.blob.core.windows.net/onlineevalbugbash/azure_ai_projects-1.0.0b3-py3-none-any.whl
    ```
### How To Run Python Samples From SDK

1. This Online Evaluation [sample_evaluation_schedules.py](./sample_evaluations_schedules.py) file demonstrates how to run CRUD operations on how to evaluate continuously by running evaluation on a given schedule.
2. We have created AI project with relevant permissions to test for bug bash, please refer `Setup: Sample SDK API Testing Parameters` section in [Online Evaluation Bug Bash Document](https://microsoftapc-my.sharepoint.com/:w:/g/personal/shiprajain_microsoft_com/EQwumulCeG9JoQbgHw0ts-EB1-Yj9Vw8HeXKwgXQl_hv9w?e=kbBnKY) for values to override in [sample_evaluation_schedules.py](./sample_evaluations_schedules.py).

### Log A Bug Under [Bug Bash Query Board](https://dev.azure.com/msdata/Vienna/_workitems/edit/3572161)

#### Template  

- Title: [Brief description of the bug]  
- Steps to Reproduce:  
- Expected Result: [What you expected to happen]  

- Actual Result: [What actually happened]  

- Screenshots/Logs: [Attach any relevant files]  

- Priority: [Low/Medium/High]  

- Tag: ignite, OnlineEvaluation  

### Appendix
The following sections are optional for the bug bash and will be enhanced afterward.
#### How to Get `Project Connection String`?
- Connection string is needed to easily create `AIProjectClient` object. You can get the connection string from the project overview page > Quick reference section. Here is the [link](https://int.ai.azure.com/build/overview?wsid=/subscriptions/72c03bf3-4e69-41af-9532-dfcdc3eefef4/resourceGroups/shared-online-evaluation-rg/providers/Microsoft.MachineLearningServices/workspaces/ignite-eval-schedule-bugbash&tid=72f988bf-86f1-41af-91ab-2d7cd011db47) to the project overview page.

#### Instructions for pushing application insights data
- TBD


#### Instructions to view enriched data
- TBD

