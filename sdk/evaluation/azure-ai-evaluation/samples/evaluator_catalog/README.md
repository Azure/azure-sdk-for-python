
# How to publish new evaluator in Evaluator Catalog.

This guide helps our partners to bring their evaluators into Microsoft provided Evaluator Catalog in Next Gen UI. 

## Context

We are building an Evaluator Catalog, that will allow us to store Microsoft provided built-in evaluators, as well as Customer's provided custom evaluators. It will allow versioning support so that customer can maintain different version of custom evaluators.

Using this catalog, customer can publish their custom evaluators under the project. Post Ignite, we'll allow them to prompt evaluators from projects to registries so that can share evaluators among different projects.

This evaluator catalog is backed by Generic Asset Service (that provides scalable and multi-region support to store all your assets in CosmosDB).

Types of Built_in Evaluators
There are 3 types of evaluators we support as Built-In Evaluators.

1. Code Based - It contains Python file
2. Code + Prompt Based - It contains Python file & Prompty file
3. Prompt Based - It contains only Prompty file.
4. Service Based - It references the evaluator from Evaluation SDK or RAI Service.

## Step 1: Run Evaluator with SDK.

Create builtin evaluator and use azure-ai-evaluation SDK to run locally. 
List of evaluators can be found at [here](https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/evaluation/azure-ai-evaluation/azure/ai/evaluation/_evaluators)

## Step 2: Create a PR 
Add a new folder with name as the Evaluator name. 

Please include following files. 

* asset.yaml
* spec.yaml
* 'evaluator' folder. Please include python files and prompty files in this folder.

Please look at existing built-in evaluators for reference. 
Location : [/assets/evaluators/builtin](https://msdata.visualstudio.com/Vienna/_git/azureml-asset?path=/assets/evaluators/builtin)

Sample PR: [pullrequest/1816050](https://msdata.visualstudio.com/Vienna/_git/azureml-asset/pullrequest/1816050?_a=files\)

Please follow directions given below. 

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
| initParameterSchema |  |  |  The JSON schema (Draft 2020-12) for the evaluator's input parameters. This includes parameters like type, properties, required. | 
| dataMappingSchema |  |  | The JSON schema (Draft 2020-12) for the evaluator's input data. This includes parameters like type, properties, required.  | 
| outputSchema |  |  | List of output metrics produced by this evaluator | 
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

## Step 3: Publish
When PR is merged. Evaluation Team will be able to kick off the CI Pipeline to publish evaluator in the Evaluator Catalog. 
This is done is 2 steps. 

In Step 1, new evaluator is published in azureml-dev registry so that it can be tested in INT environment. Once all looks good, Step 2 is performed.
In Step 2, new evaluator is published in azure-ml registry (for Production).


## Step 4: Verify Evaluator
Now, use Evaluators CRUD APIs to view evaluator in GET /evaluator list. 

Use following links

INT: 
PROD: 