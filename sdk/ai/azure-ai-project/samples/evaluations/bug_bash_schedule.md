## Welcome to the Bug Bash for Evaluation in Cloud with Schedules!

### How To Get Started
#### Permissions needed - Please request for below access in channel
1. Project user access to do bug bush
2. Log Analytics Contributor role for query and view the evaluation results by the schedule.

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
2. We have created AI project with relevant permissions to test for bug bash, please refer `Setup: Sample SDK API Testing Parameters` section in [Online Evaluation Bug Bash Document](https://microsoftapc-my.sharepoint.com/:w:/g/personal/saikothinti_microsoft_com/Eab1g-gIhqJCkf7fsBHjjxEBxm6fIwTbbMgIu0HeAreEvQ?e=1cTIyz) for values to override in [sample_evaluation_schedules.py](./sample_evaluations_schedules.py).
3. Please raise request in channel to get yourself added into AI project for bug bash.

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


#### Instructions to view enriched data
- You would need LogAnlaytics Contributor role for the AppInsights instance attached to the project
- Please raise request in the channel to get yourself added
- Go to Logs dashboard and run query
    - traces | where customDimensions["event.name"] == "gen_ai.evaluation.< evaluator-name >"
    - Eg: traces | where customDimensions["event.name"] == "gen_ai.evaluation.f1_score_saik1034"