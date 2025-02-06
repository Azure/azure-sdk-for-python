# End-to-End Safety Evaluation for Deployment Safety Board (DSB) Reviews

1P teams need to run Safety Evaluations for DSB review readiness. Currently, onboarding to Azure Safety Evaluations has proven difficult for customers due to the process's complexities. Currently, users need to:

- Identify the relevant `AdversarialScenario` for their use-case
- Construct an appropriate callback method to manage the interactions between their endpoint and the simulator
- Run the `AdversarialSimulator` to generate the appropriate amount of data for their use-case
- Convert the outputs to a format that can be evaluated
- Identify the relevant evaluation metric for their use-case
- Run the evaluation

To simplify this process, we will support a new interface, `DSBEvaluation`, which will reduce the user requirements to:

- Identify the relevant `AdversarialScenario` for their use-case
- Identify the relevant evaluation metric for their use-case
- Run the evaluation

The following is an example of usage and output:

```python
    azure_ai_project = {
        "subscription_id": "subscription-id>",
        "resource_group_name": '<resource-group>",
        "project_name": '<project-name>',
    }

    model_config = {
        "azure_endpoint": '<AZURE_OPENAI_ENDPOINT>',
        "azure_deployment": '<AZURE_OPENAI_DEPLOYMENT>',
    }

    credential = DefaultAzureCredential()

    
    dsb_evaluation = DSBEvaluation(model_config=model_config, azure_ai_project=azure_ai_project, credential=credential)

    dsb_evaluation_outputs = dsb_evaluation(
        adversarial_scenario=AdversarialScenario.ADVERSARIAL_CONVERSATION,
        evaluators=[DSBEvaluator.CONTENT_SAFETY, DSBEvaluator.GROUNDEDNESS, DSBEvaluator.PROTECTED_MATERIAL],
        target=call_to_your_endpoint_here,
        source_text=source_text,
        max_conversation_turns=1,
        max_simulation_results=3,
        output_path="evaluation_outputs.jsonl",
    )
```

## Evaluators

Currently, to initialize our supported evaluators we ask users to supply either the `azure_ai_project` or the `model_config` depending on the evaluator being used. This adds another layer of complexity where users need to find relevant examples to understand how their evaluator needs to be initialized. Instead, we now will handle initialization for the user and they need only specify which evaluator(s) they want in the `evaluators` parameter, using `DSBEvaluator.<evaluator-name>`. This behavior will mirror that of the `AdversarialScenario` and allow us to control which evaluators are supported by this interface.

Currently, initialization of evaluators is as follows:

```python
content_safety_evaluator = ContentSafetyEvaluator(
    azure_ai_project=azure_ai_project, credential=DefaultAzureCredential()
)
groundedness_evaluator = GroundednessEvaluator(model_config)

result = evaluate(
    ...,
    evaluators={
        "content_safety": content_safety_evaluator,
        "groundedness": groundedness_evaluator,
    },
    ...
)
```

Instead, we will have:

```python
dsb_evaluation(
    ...,
    evaluators=[DSBEvaluator.CONTENT_SAFETY, DSBEvaluator.GROUNDEDNESS]
)
```
