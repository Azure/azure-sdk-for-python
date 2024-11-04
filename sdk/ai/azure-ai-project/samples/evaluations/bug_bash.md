## Welcome to the Quality Evaluation Bug Bash!


For this bug bash, we'll be testing all of the quality evaluators that will be released in the GA version of the Azure AI Evaluation SDK. Quality evaluators include:


#### Data Requirements for Quality Evaluators

| Evaluator         | `query`      | `response`      | `context`       | `ground_truth`  | `conversation` |
|----------------|---------------|---------------|---------------|---------------|-----------|
| `GroundednessEvaluator`   | Optional: String | Required: String | Required: String | N/A  | Supported |
| `GroundednessProEvaluator`   | Required: String | Required: String | Required: String | N/A  | Supported |
| `RetrievalEvaluator`        | Required: String | N/A | Required: String         | N/A           | Supported |
| `RelevanceEvaluator`      | Required: String | Required: String | N/A | N/A           | Supported |
| `CoherenceEvaluator`      | Required: String | Required: String | N/A           | N/A           |Supported |
| `FluencyEvaluator`        | N/A  | Required: String | N/A          | N/A           |Supported |
| `SimilarityEvaluator` | Required: String | Required: String | N/A           | Required: String |Not supported |
| `F1ScoreEvaluator` | N/A  | Required: String | N/A           | Required: String |Not supported |
| `RougeScoreEvaluator` | N/A | Required: String | N/A           | Required: String           | Not supported |
| `GleuScoreEvaluator` | N/A | Required: String | N/A           | Required: String           |Not supported |
| `BleuScoreEvaluator` | N/A | Required: String | N/A           | Required: String           |Not supported |
| `MeteorScoreEvaluator` | N/A | Required: String | N/A           | Required: String           |Not supported |
| `QAEvaluator`      | Required: String | Required: String | Required: String | N/A           | Not supported |

> [!NOTE]
>`QAEvaluator` is a composite evaluator with Similarity, Coherence, Relevance, F1Score, Groundedness, and Fluency.

We want to test the individual evaluators (in single-turn and conversation scenarios) and test them as inputs to the `evaluate()` method. For `evaluate()` testing, ensure that if you are using a dataset with input column names, that the required inputs of the evaluator(s) you're using are present.

```python
from azure.ai.evaluation import evaluate, GroundednessEvaluator
groundedness_eval = GroundednessEvaluator(model_config)

result = evaluate(
    data="./data/groundedness_200.jsonl", # provide your data here
    evaluation_name="groundedness_pro_test",
    evaluators={
        "groundedness": groundedness_pro_eval
    },
    # column mapping
    evaluator_config={
        "groundedness": {
            "column_mapping": {
                "query": "${data.query}",
                "context": "${data.context}",
                "response": "${data.response}"
            } 
        }
    },
    # Optionally provide your AI Studio project information to track your evaluation results in your Azure AI Studio project
    azure_ai_project = azure_ai_project
)
```

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



#### Evaluating multi-turn conversations

For evaluators that support conversations as input, you can just pass in the conversation directly into the evaluator:

```python
groundedness_score = groundedness_eval(conversation=conversation)
```

A conversation is a Python dictionary of a list of messages (which include content, role, and optionally context). The following is an example of a two-turn conversation.

```json
{"conversation":
    {"messages": [
        {
            "content": "Which tent is the most waterproof?", 
            "role": "user"
        },
        {
            "content": "The Alpine Explorer Tent is the most waterproof",
            "role": "assistant", 
            "context": "From the our product list the alpine explorer tent is the most waterproof. The Adventure Dining Table has higher weight."
        },
        {
            "content": "How much does it cost?",
            "role": "user"
        },
        {
            "content": "The Alpine Explorer Tent is $120.",
            "role": "assistant",
            "context": null
        }
        ]
    }
}
```

### Prerequisites
- Azure AI Project in `EastUS2` region
- Azure Open AI Deployment with GPT model supporting `chat completion`. Example `gpt-4`
- Azure SDK for Python repository cloned and checked out to the `release/azure-ai-evaluation/1.0.0` branch

### Resources

Project, endpoint key, and deployment given in meeting.


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
