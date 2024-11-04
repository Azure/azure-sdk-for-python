## Welcome to the Quality Evaluation Bug Bash!


For this bug bash, we'll be testing all of the quality evaluators that will be release in the GA version of the Azure AI Evaluation SDK. Quality evaluators include:

 - `SimilarityEvaluator`
 - `CoherenceEvaluator`
 - `RelevanceEvaluator`
 - `RetrievalEvaluator`
 - `FluencyEvaluator`
 - `GroundednessEvaluator`
 - `F1ScoreEvaluator`
 - `QAEvaluator` (composite evaluator with Similarity, Coherence, Relevance, F1Score, Groundedness, and Fluency)

We want to test the individual evaluators (in single-turn and conversation scenarios) and test them as inputs to the `evaluate()` method. For `evaluate()` testing, ensure that if you are using a dataset with input column names, that the required inputs of the evaluator(s) you're using are present.

The following changes have been made for Ignite:

- Add optional `query` parameter to `GroundednessEvaluator` + update prompts
- Add `query` and `context` parameters to `RetrievalEvaluator` + update prompt
- Remove `context` parameter to `RelevanceEvaluator` + update prompt
- Remove `query` parameter from `FluencyEvaluator` + update prompt
- Update prompt for `CoherenceEvaluator`
- Add `_reason` output to all evaluators except `SimilarityEvaluator` and `F1ScoreEvaluator`
- Validation is added for conversation vs. single-turn inputs on each evaluator
- Optional inputs are allowed when using `evaluate()` method (e.g. `GroundednessEvaluator` can be used with a dataset that doesn't include a `query` column)
- New duplicate keys are added to evaluator outputs with the `gpt_` prefix removed. For now, both keys should be present in all outputs. The `gpt_` keys will be removed in a future release.



### Prerequisites
- Azure AI Project in `EastUS2` region
- Azure Open AI Deployment with GPT model supporting `chat completion`. Example `gpt-4`
- Azure SDK for Python repository cloned and checked out to the `release/azure-ai-evaluation/1.0.0` branch

### Resources

If you do not have an Azure AI Project with a deployed model, please use the following resources:

| Resource Type     | Resource Name                                                                                                                                                                                                                                                                  |
|-------------------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Project           | [ignite-eval-project-eastus2](https://ai.azure.com/build/overview?wsid=/subscriptions/fac34303-435d-4486-8c3f-7094d82a0b60/resourceGroups/rg-cliu/providers/Microsoft.MachineLearningServices/workspaces/ignite-eval-project-eastus2&tid=72f988bf-86f1-41af-91ab-2d7cd011db47) |
| AOAI endpoint key | /subscriptions/fac34303-435d-4486-8c3f-7094d82a0b60/resourceGroups/rg-cliu/providers/Microsoft.MachineLearningServices/workspaces/ignite-eval-project-eastus2/connections/igniteevaluati8620559527_aoai/credentials/key                                                        |
| AOAI deployment   | [gpt-4-ignite-bugbash](https://ai.azure.com/build/deployments/aoai/connections/igniteevaluati8620559527_aoai/gpt-4-ignite-bugbash?wsid=/subscriptions/fac34303-435d-4486-8c3f-7094d82a0b60/resourceGroups/rg-cliu/providers/Microsoft.MachineLearningServices/workspaces/ignite-eval-project-eastus2&tid=72f988bf-86f1-41af-91ab-2d7cd011db47)|



### Clone the repository
```bash
git clone https://github.com/Azure/azure-sdk-for-python.git
# Navigate to cloned repo folder
git pull
git checkout release/azure-ai-evaluation/1.0.0
```

### Installation Instructions:

1. Create a **virtual environment of you choice**. To create one using conda, run the following command:
    ```bash
    >> conda create -n quality-evaluation-bug-bash python=3.11
    >> conda activate quality-evaluation-bug-bash
    ```
2. Install the required packages by running the following command:
    ```bash
   >> cd sdk/evaluation/azure-ai-evaluation
   >> pip install -r dev_requirements.txt
   >> pip install "tox<5"
   >> pip install -e .
    ```

### Data
You can use the datasets in the `data` directory. Some datasets have column mappings, some are conversations, some omit certain columns, etc. You can use these datasets to test the evaluators.

### Report Bugs

Please use the following template to report bugs : [**Bug Template**](https://msdata.visualstudio.com/Vienna/_workitems/edit/3600109)

### Samples

1. [Using `evaluate()`](https://github.com/Azure-Samples/azureai-samples/blob/main/scenarios/evaluate/evaluate_qualitative_metrics/evaluate_qualitative_metrics.ipynb) (note that some input params have changed)
2. [Individual evaluator](https://github.com/Azure-Samples/azureai-samples/blob/47c934561c24533644af58ed377e2b7382d61621/scenarios/evaluate/evaluate_app/evaluate_app.ipynb#L182)
3. There are also sample usages of each evaluator in their docstrings