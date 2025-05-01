## Welcome to Bug Bash for Azure AI Evaluation SDK 

### Prerequisites
- Azure AI Project in `eastus2euap` or `centalus2euap` region. It is used to get token/credential to call Evaluation service. 

### Resources

If you do not have the required resources, please use the following resources:


| Resource Type     | Resource Name                                                                                                                                                                                                                                                                  |
|-------------------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Project           | [anksingtest1rpproject](https://ai.azure.com/foundryProject/overview?wsid=/subscriptions/b17253fa-f327-42d6-9686-f3e553e24763/resourceGroups/anksing-vanilla-eval/providers/Microsoft.CognitiveServices/accounts/anksingtest1rp/projects/anksingtest1rpproject&tid=72f988bf-86f1-41af-91ab-2d7cd011db47) |


## Instructions:

### 1. Setup Virtualenv 

##### Recommended path: 
`python3 -m venv .bugbashenv`

##### Linux based:
`source .bugbashenv/bin/activate`
##### Windows:
`.bugbashenv\Scripts\activate`

### 2. To checkout Bug Bash branch.
```bash
To pull latest code from the Bug bash branch.

git clone https://github.com/Azure/azure-sdk-for-python.git
cd azure-sdk-for-python
git pull
git remote add w-javed https://github.com/w-javed/azure-sdk-for-python.git
git remote -v
git fetch w-javed
git checkout -b Bug-Bash-SDK-Evaluations-1DP-Project w-javed/Bug-Bash-SDK-Evaluations-1DP-Project
cd sdk/evaluation/azure-ai-evaluation/samples/onedp/bugbash
```

### 3. Install Azure AI Evaluation
```bash
pip install --upgrade git+https://github.com/Azure/azure-sdk-for-python.git@main#subdirectory=sdk/evaluation/azure-ai-evaluation
```


### 4. Running Content Safety Evaluator with 1DP Project
```bash
python content_safety_evaluator.py  
```

### 5. Running Evaluate API
```bash
python content_safety_using_evaluate_api.py
```

### 6. Simulations
```bash
python simulation_and_eval.py
```


### Azure AI project

Please select or create a new 1DP/RP project in `eastus2euap` region, and set the following values in env variable. 

```bash
os.environ["1DP_PROJECT_URL"] = "https://anksingtest1rp.cognitiveservices.azure.com/api/projects/anksingtest1rpproject"
```

Please create a bug/task for any issue you encounter during bug bash using following link. Thanks!


Bug Template [here](https://msdata.visualstudio.com/Vienna/_workitems/edit/4157449)

