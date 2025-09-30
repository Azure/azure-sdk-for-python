
# How to publish new evaluator in Evaluator Catalog.

This guide helps our partners to bring their evaluators into Microsoft provided Evaluator Catalog in Next Gen UI. 

## Context

We are building an Evaluator Catalog, that will allow us to store Microsoft provided built-in evaluators, as well as Customer's provided custom evaluators. It will allow versioning support so that customer can maintain different version of custom evaluators.

Using this catalog, customer can publish their custom evaluators under the project. Post Ignite, we'll allow them to prompt evaluators from projects to registries so that can share evaluators amount different projects.

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

## spec.yaml content

```yml

type: "evaluator"
name: "test.{name}"
version: 1
displayName: "{display name}"
description: "{description}"
evaluatorType: "builtin"
evaluatorSubType: "code"
It represents what type of evaluator It is. 
For #1 & #2 type evaluators, please add "code"
For #3 type evaluator, please provide "prompt"
For #4 type evaluator, please provide "service"

**categories: **
It represents an array of categories (Quality, Safety, Agents)
Example- ["Quality", "Safety"]

**initParameterSchema:**
The JSON schema (Draft 2020-12) for the evaluator's input parameters. This includes parameters like type, properties, required.
Example-
          type: "object"
          properties:
            threshold:
              type: "number"
              minimumValue: 0
              maximumValue: 1
              step: 0.1
          required: ["threshold"]


**dataMappingSchema:**
The JSON schema (Draft 2020-12) for the evaluator's input data. This includes parameters like type, properties, required.
Example-
          type: "object"
          properties:
            ground_truth:
              type: "string"
            response:
              type: "string"
          required: ["ground_truth", "response"]

**outputSchema:**
List of output metrics produced by this evaluator
Example-
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

In Step 1, new evaluator is published in azureml-dev registry so that I can be tested in INT environment. Once all looks good, Step 2 is performed.
In Step 2, new evaluator is published in azure-ml registry (for Production).


## Step 4: Verify Evaluator
Now, use Evaluators CRUD APIs to view evaluator in GET /evaluator list. 

Use following links

INT: 
PROD: 