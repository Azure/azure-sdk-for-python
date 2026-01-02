
# How to publish new built-in evaluator in Evaluator Catalog.

This guide helps our partners to bring their evaluators into Microsoft provided Evaluator Catalog in Next Gen UI. 

## Context

We are building an Evaluator Catalog, that will allow us to store built-in evaluators (provided by Microsoft), as well as 1P/3P customer's provided evaluators. 

We are also building Evaluators CRUD API and SDK experience which can be used by our external customer to create custom evaluators. NextGen UI will leverage these new APIs to list evaluators in Evaluation Section. 

These custom evaluators are also stored in the Evaluator Catalog, but the scope these evaluator will be at project level at Ignite. Post Ignite, we'll allow customers to share their evaluators among different projects.

This evaluator catalog is backed by Generic Asset Service (that provides versioning support as well as scalable and multi-region support to store all your assets in CosmosDB).

Types of Built_in Evaluators
There are 3 types of evaluators we support as Built-In Evaluators.

1. Code Based - It contains Python file
2. Code + Prompt Based - It contains Python file & Prompty file
3. Prompt Based - It contains only Prompty file.
4. Service Based - It references the evaluator in RAI Service that calls fine tuned models provided by Data Science Team. 

## Step 1: Run Your evaluators with Evaluation SDK.

Create builtin evaluator and use azure-ai-evaluation SDK to run locally. 
List of evaluators can be found at [here](https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/evaluation/azure-ai-evaluation/azure/ai/evaluation/_evaluators)

## Step 2: Provide your evaluator

We are storing all the builtin evaluators in Azureml-asset Repo. Please provide your evaluators files by creating a PR in this repo. Please follow the steps.

1. Add a new folder with name as the Evaluator name. 

2. Please include following files.

* asset.yaml
* spec.yaml
* 'evaluator' folder. 

This 'evaluator' folder contains two files.
1. Python file name should be same as evaluator name with '_' prefix.
2. Prompty file name should be same as evaluator name with .prompty extension.  

Example: Coherence evaluator contains 2 files. 
_coherence.py
coherence.prompty

Please look at existing built-in evaluators for reference. 
* Evaluator Catalog Repo : [/assets/evaluators/builtin](https://github.com/Azure/azureml-assets/tree/main/assets/evaluators/builtin)
* Sample PR: [PR 1816050](https://msdata.visualstudio.com/Vienna/_git/azureml-asset/pullrequest/1816050)

3. Please copy asset.yaml from sample. No change is required. 
   
4. Please follow steps given below to create spec.yaml. 

## Asset Content - spec.yaml

| Asset Property | API Property  | Example | Description |
| - | - | - | - |
| type | type | evaluator | It is always 'evaluator'. It identifies type of the asset.  |
| name | name | test.f1_score| Name of the evaluator, alway in URL | 
| version | version | 1 | It is auto incremented version number, starts with 1 | 
| displayName: | display name | F1 Score | It is the name of the evaluator shown in UI | 
| description: | description | | This is description of the evaluator. | 
| evaluatorType: | evaluator_type | "builtin"| For Built-in evaluators, value is "builtin". For custom evaluators, value is "custom". API only supports 'custom'| 
| evaluatorSubType | definition.type | "code" | It represents what type of evaluator It is. For #1 & #2 type evaluators, please add "code". For #3 type evaluator, please provide "prompt". For #4 type evaluator, please provide "service" | 
| categories | categories | ["Quality"] | The categories of the evaluator. It's an array. Allowed values are Quality, Safety, Agents. Multiple values are allowed | 
| initParameterSchema | init_parameters |  |  The JSON schema (Draft 2020-12) for the evaluator's input parameters. This includes parameters like type, properties, required. | 
| dataMappingSchema | data_schema |  | The JSON schema (Draft 2020-12) for the evaluator's input data. This includes parameters like type, properties, required.  | 
| outputSchema | metrics |  | List of output metrics produced by this evaluator | 
| path |  Not expose in API |  ./evaluator |  Fixed. | 

Example:

```yml

type: "evaluator"
name: "test.bleu_score"
version: 1
displayName: "Bleu-Score-Evaluator"
description: "| | |\n| -- | -- |\n| Score range | Float [0-1]: higher means better quality. |\n| What is this metric? | BLEU (Bilingual Evaluation Understudy) score is commonly used in natural language processing (NLP) and machine translation. It measures how closely the generated text matches the reference text. |\n| How does it work? | The BLEU score calculates the geometric mean of the precision of n-grams between the model-generated text and the reference text, with an added brevity penalty for shorter generated text. The precision is computed for unigrams, bigrams, trigrams, etc., depending on the desired BLEU score level. The more n-grams that are shared between the generated and reference texts, the higher the BLEU score. |\n| When to use it? | The recommended scenario is Natural Language Processing (NLP) tasks. It's widely used in text summarization and text generation use cases. |\n| What does it need as input? | Response, Ground Truth |\n"
evaluatorType: "builtin"
evaluatorSubType: "code"
categories: ["quality"]
initParameterSchema:
  type: "object"
  properties:
    threshold:
      type: "number"
      minimum: 0
      maximum: 1
      multipleOf: 0.1
  required: ["threshold"]
dataMappingSchema:
  type: "object"
  properties:
    ground_truth:
      type: "string"
    response:
      type: "string"
  required: ["ground_truth", "response"]
outputSchema:
  bleu:
    type: "continuous"
    desirable_direction: "increase"
    min_value: 0
    max_value: 1
path: ./evaluator
```

## Step 3: Test in RAI Service ACA Code.

Once PR is ready to be reviewed. Before merging, please verify your code in ACA. 
Please follow instructions given on this PR
[https://dev.azure.com/msdata/Vienna/_git/vienna/pullrequest/1837536?_a=files&path=/src/azureml-api/src/RAISvc/aca/README.md](https://dev.azure.com/msdata/Vienna/_git/vienna/pullrequest/1837536?_a=files&path=/src/azureml-api/src/RAISvc/aca/README.md)

## Step 4: Create a PR to add assets
Please create a PR to add an evaluator asset in Built-In registries.
This is a Step 1 in [Build & Release Process](https://eng.ms/docs/cloud-ai-platform/ai-platform/ai-platform-ml-platform/project-vienna-services/azure-machine-learning-runbook/operational/assets/registry/azureml/sop/adding-assets-to-builtin-registry/build-and-release-process) provided by asset team. 

## Step 5: Update Deployment Config
Please update the deployment config file for following registries.

Please find evaluator: section.

[azureml-dev](https://msdata.visualstudio.com/Vienna/_git/azureml-asset?path=/registry/deploy_configs/azureml-dev.yml)
[azureml-staging](https://msdata.visualstudio.com/Vienna/_git/azureml-asset?path=/registry/deploy_configs/azureml-staging.yml)
[azureml](https://msdata.visualstudio.com/Vienna/_git/azureml-asset?path=/registry/deploy_configs/azureml.yml)

This is a Step 2 in [Build & Release Process](https://eng.ms/docs/cloud-ai-platform/ai-platform/ai-platform-ml-platform/project-vienna-services/azure-machine-learning-runbook/operational/assets/registry/azureml/sop/adding-assets-to-builtin-registry/build-and-release-process).

## Step 6: Post your PR(s) in the [System Registry Content](https://teams.microsoft.com/l/channel/19%3Abe5ce76d1cba4418a81829e32ee7cf2b%40thread.skype/System%20Registry%20Content?groupId=88aa174e-6310-4634-bfcb-5761e1a1190a&tenantId=72f988bf-86f1-41af-91ab-2d7cd011db47) channel

Please get the approval from Asset Team and merge the PR. This is Step 3 in [Build & Release Process](https://eng.ms/docs/cloud-ai-platform/ai-platform/ai-platform-ml-platform/project-vienna-services/azure-machine-learning-runbook/operational/assets/registry/azureml/sop/adding-assets-to-builtin-registry/build-and-release-process)

## Step 7: Build & Release the pipeline
Please follow steps 4 & 5 in [Build & Release Process](https://eng.ms/docs/cloud-ai-platform/ai-platform/ai-platform-ml-platform/project-vienna-services/azure-machine-learning-runbook/operational/assets/registry/azureml/sop/adding-assets-to-builtin-registry/build-and-release-process).

This will deploy evaluator assets in azureml-dev, azureml-staging and azureml (prod) registries. 
You can choose to first deploy in dev and test it INT region and proceed with other registries. 

## Step 8a: Test is INT Environment
Please verify following:

1. Verify if new evaluator is available in Evaluator REST APIs (https://int.api.azureml-test.ms)
2. Verify if there are rendered correctly in NextGen UI. 
3. Verify if Evaluation API (Eval Run and Open AI Eval) both are able to reference these evaluators from Evaluator Catalog and run in ACA. 

## Step 8b: Test is Canary Environment
Please verify following:

1. Verify if new evaluator is available in Evaluator REST APIs (https://eastus2euap.api.azureml.ms)
2. Verify if there are rendered correctly in NextGen UI. 
3. Verify if Evaluation API (Eval Run and Open AI Eval) both are able to reference these evaluators from Evaluator Catalog and run in ACA. 

## Step 8c: Test is Prod Environment
Please verify following:

1. Verify if new evaluator is available in Evaluator REST APIs (https://eastus2.api.azureml.ms)
2. Verify if there are rendered correctly in NextGen UI. 
3. Verify if Evaluation API (Eval Run and Open AI Eval) both are able to reference these evaluators from Evaluator Catalog and run in ACA.
