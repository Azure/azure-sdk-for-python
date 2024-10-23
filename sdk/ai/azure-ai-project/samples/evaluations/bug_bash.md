## Welcome to the Evaluation in Cloud Bug Bash!

### Prerequisites
- Azure AI Project in `EastUS2` region
- Azure Open AI Deployment with GPT model supporting `chat completion`. Example `gpt-4`

### Resources

If you do not have the required resources, please use the following resources:

| Resource Type     | Resource Name                                                                                                                                                                                                                                                                  |
|-------------------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Project           | [ignite-eval-project-eastus2](https://ai.azure.com/build/overview?wsid=/subscriptions/fac34303-435d-4486-8c3f-7094d82a0b60/resourceGroups/rg-cliu/providers/Microsoft.MachineLearningServices/workspaces/ignite-eval-project-eastus2&tid=72f988bf-86f1-41af-91ab-2d7cd011db47) |
| AOAI endpoint key | /subscriptions/fac34303-435d-4486-8c3f-7094d82a0b60/resourceGroups/rg-cliu/providers/Microsoft.MachineLearningServices/workspaces/ignite-eval-project-eastus2/connections/igniteevaluati8620559527_aoai/credentials/key                                                        |
| AOAI deployment   | [gpt-4-ignite-bugbash](https://ai.azure.com/build/deployments/aoai/connections/igniteevaluati8620559527_aoai/gpt-4-ignite-bugbash?wsid=/subscriptions/fac34303-435d-4486-8c3f-7094d82a0b60/resourceGroups/rg-cliu/providers/Microsoft.MachineLearningServices/workspaces/ignite-eval-project-eastus2&tid=72f988bf-86f1-41af-91ab-2d7cd011db47)|

### Datasets from Registry
| Dataset | Location                                                                                                                                                                                                                                            |
|---------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
|  To test any evaluators       | [azureml://registries/remote-eval-testing/data/remote-eval-bugbash-test-dataset-tiny/versions/2](https://ml.azure.com/registries/remote-eval-testing/data/remote-eval-bugbash-test-dataset-tiny/version/2?tid=72f988bf-86f1-41af-91ab-2d7cd011db47) |
| Jailbreak harm        | [azureml://registries/remote-eval-testing/data/indirect_jailbreak_attack_data_tiny/versions/1](https://ml.azure.com/registries/remote-eval-testing/data/indirect_jailbreak_attack_data_tiny/version/1?tid=72f988bf-86f1-41af-91ab-2d7cd011db47)     |
| Content harm        | [azureml://registries/remote-eval-testing/data/content_harm_data_tiny/versions/1](https://ml.azure.com/registries/remote-eval-testing/data/content_harm_data_tiny/version/1?tid=72f988bf-86f1-41af-91ab-2d7cd011db47)                               |
| Protected Materials (IP) harm  | [azureml://registries/remote-eval-testing/data/ip_harm_data_tiny/versions/1](https://ml.azure.com/registries/remote-eval-testing/data/ip_harm_data_tiny/version/1?tid=72f988bf-86f1-41af-91ab-2d7cd011db47)                                                                                                                                                                      |

### Datasets from Project
| Dataset | Location   |
|---------|------------|
|  To test any evaluators       | [/subscriptions/fac34303-435d-4486-8c3f-7094d82a0b60/resourceGroups/rg-cliu/providers/Microsoft.MachineLearningServices/workspaces/ignite-eval-project-eastus2/data/remote-eval-bugbash-dataset-tiny/versions/1](https://ai.azure.com/build/data/remote-eval-bugbash-dataset-tiny/1/details?wsid=/subscriptions/fac34303-435d-4486-8c3f-7094d82a0b60/resourcegroups/rg-cliu/providers/Microsoft.MachineLearningServices/workspaces/ignite-eval-project-eastus2&tid=72f988bf-86f1-41af-91ab-2d7cd011db477) |
| Jailbreak harm        | [/subscriptions/fac34303-435d-4486-8c3f-7094d82a0b60/resourceGroups/rg-cliu/providers/Microsoft.MachineLearningServices/workspaces/ignite-eval-project-eastus2/data/unfiltered_indirect_attack_sim_outputs/versions/1](https://ai.azure.com/build/data/unfiltered_indirect_attack_sim_outputs/1/details?wsid=/subscriptions/fac34303-435d-4486-8c3f-7094d82a0b60/resourcegroups/rg-cliu/providers/Microsoft.MachineLearningServices/workspaces/ignite-eval-project-eastus2&tid=72f988bf-86f1-41af-91ab-2d7cd011db47)     |
| Content harm tiny       | [/subscriptions/fac34303-435d-4486-8c3f-7094d82a0b60/resourceGroups/rg-cliu/providers/Microsoft.MachineLearningServices/workspaces/ignite-eval-project-eastus2/data/unfiltered_content_harm_sim_output/versions/1](https://ai.azure.com/build/data/unfiltered_content_harm_sim_output/1/details?wsid=/subscriptions/fac34303-435d-4486-8c3f-7094d82a0b60/resourcegroups/rg-cliu/providers/Microsoft.MachineLearningServices/workspaces/ignite-eval-project-eastus2&tid=72f988bf-86f1-41af-91ab-2d7cd011db47)                               |
| Protected Materials (IP) harm  | [/subscriptions/fac34303-435d-4486-8c3f-7094d82a0b60/resourceGroups/rg-cliu/providers/Microsoft.MachineLearningServices/workspaces/ignite-eval-project-eastus2/data/ip-harm-dataset-tiny/versions/1](https://ai.azure.com/build/data/ip-harm-dataset-tiny/1/details?wsid=/subscriptions/fac34303-435d-4486-8c3f-7094d82a0b60/resourcegroups/rg-cliu/providers/Microsoft.MachineLearningServices/workspaces/ignite-eval-project-eastus2&tid=72f988bf-86f1-41af-91ab-2d7cd011db47)  

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

### Evaluators to test

- [Built In Evaluators](https://ai.azure.com/build/evaluation/evaluator?wsid=/subscriptions/fac34303-435d-4486-8c3f-7094d82a0b60/resourceGroups/rg-cliu/providers/Microsoft.MachineLearningServices/workspaces/ignite-eval-project-eastus2&flight=ModelCatalogAMLTestRegistryName=azureml-staging&tid=72f988bf-86f1-41af-91ab-2d7cd011db47)
- Custom Prompt Based Evaluator
  - [FriendlinessMeasureEvaluator](https://ai.azure.com/build/evaluation/evaluators/FriendlinessMeasureEvaluator/1/ignite-eval-project-eastus2/details?wsid=/subscriptions/fac34303-435d-4486-8c3f-7094d82a0b60/resourceGroups/rg-cliu/providers/Microsoft.MachineLearningServices/workspaces/ignite-eval-project-eastus2&flight=ModelCatalogAMLTestRegistryName=azureml-staging&tid=72f988bf-86f1-41af-91ab-2d7cd011db47&resourceType=Workspace)

### How to Get `Connection String` for the Project ?
Connection string is needed to easily create `AIProjectClient` object. You can get the connection string from the project overview page. Here is the [link](https://int.ai.azure.com/build/overview?wsid=/subscriptions/fac34303-435d-4486-8c3f-7094d82a0b60/resourceGroups/rg-cliu/providers/Microsoft.MachineLearningServices/workspaces/ignite-eval-project-eastus2&tid=72f988bf-86f1-41af-91ab-2d7cd011db47) to the project overview page.

### Report Bugs

Please use the following template to report bugs : [**Bug Template**](https://msdata.visualstudio.com/Vienna/_workitems/create/Bug?templateId=5f8cafcf-2bbc-42df-a0ba-13c3ebcbeabe&ownerId=31cd3b44-f331-4377-95dd-2f8d6e169ee4)

### Samples

1. Remote Evaluation - [Sample Link](./sample_evaluations.py). This sample demonstrates how to create a new evaluation in cloud.
2. Online Evaluation - [Sample Link](./sample_evaluations_schedules.py). This sample demonstrates how to evaluate continuously by running evaluation on a schedule.
