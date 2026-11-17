# Evaluation TypeSpec Issues

## General issues

* All TypeSpec model names need to be reviewed, as those get emitted as SDK class names. In particular, we need to decide on a common pattern to identify Azure-specific sub models, when we extend existing OpenAI-defined base model.
Also avoid one-word generic model names, like this one:
```
/** Base class for targets with discriminator support. */
@discriminator("type")
model Target {
  /** The type of target. */
  type: string;
}
```

* Decide if and how we enumerate the many evaluators (around 40?). Should we have a TypeSpec for them, and TypedDicts in emitted Python code? Or do we only have one for the base class?

## Model `AzureAIDataSourceConfig`, property `scenario`

Values there should be defined as enum: 

```
@discriminator("scenario")
model AzureAIDataSourceConfig extends DataSourceConfig {
  /** The object type, which is always `azure_ai_source`. */
  type: "azure_ai_source";

  /** Data schema scenario. */
  #suppress "@azure-tools/typespec-azure-core/no-unnamed-union" "Auto-suppressed warnings non-applicable rules during import."
  scenario:
    | "red_team"
    | "responses"
    | "traces_preview"
    | "synthetic_data_gen_preview"
    | "benchmark_preview";
}
```

## Model `TargetCompletionEvalRunDataSource`, property `input_messages`

The TypeSpec model TargetCompletionEvalRunDataSource has a property:

```
/** Input messages configuration. */
  input_messages?: OpenAI.CreateEvalCompletionsRunDataSourceInputMessagesItemReference;
```

where OpenAI.CreateEvalCompletionsRunDataSourceInputMessagesItemReference has a type discriminator: "item_reference".
 
Now looking at the Python sample `sample_agent_evaluation.py` it defines input_messages as the following:

``` 
"input_messages": {
    "type": "template",
    "template": [
        {"type": "message", "role": "user", "content": {"type": "input_text", "text": "{{item.query}}"}}
    ],
},
```
 
So it uses type discriminator "template", not "item_reference".
 
So I think our TypeSpec is missing a Union with other OpenAI TypeSpec models.

##  Model `ResponseRetrievalItemGenerationParams`, property `max_runs_hourly`

Is defined in TypeSpec (using type discriminator "response_retrieval"), having `max_runs_hourly` as required properties. Yet the sample code `sample_agent_evaluation.py` does not set it. Should it be made optional in TypeSpec? Removed?

## Model AzureAIResponsesEvalRunDataSource, properties `max_runs_hourly` and `event_configuration_id`

Is defined in TypeSpec (using type discriminator "azure_ai_responses"), having required properties max_runs_hourly and event_configuration_id. Yet the same sample code `sample_agent_evaluation.py` does not set them. Should they be made optional in TypeSpec?

## Score Model Grader

Python OpenAI package defines this:

```python
class ScoreModelGraderParam(TypedDict, total=False):
    """A ScoreModelGrader object that uses a model to assign a score to the input."""

    input: Required[Iterable[Input]]
    """The input messages evaluated by the grader.

    Supports text, output text, input image, and input audio content blocks, and may
    include template strings.
    """

    model: Required[str]
    """The model to use for the evaluation."""

    name: Required[str]
    """The name of the grader."""

    type: Required[Literal["score_model"]]
    """The object type, which is always `score_model`."""

    range: Iterable[float]
    """The range of the score. Defaults to `[0, 1]`."""

    sampling_params: SamplingParams
    """The sampling parameters for the model."""
```

Our OpenAI TypeSpec defines it like this:

```
model GraderScoreModel {
  /** The object type, which is always `score_model`. */
  #suppress "@azure-tools/typespec-azure-core/no-openapi" "Auto-suppressed warnings non-applicable rules during import."
  @extension("x-stainless-const", true)
  type: "score_model";

  /** The name of the grader. */
  name: string;

  /** The model to use for the evaluation. */
  `model`: string;

  /** The sampling parameters for the model. */
  #suppress "@azure-tools/typespec-azure-core/casing-style" "Auto-suppressed warnings non-applicable rules during import."
  sampling_params?: EvalGraderScoreModelSamplingParams;

  /** The input messages evaluated by the grader. Supports text, output text, input image, and input audio content blocks, and may include template strings. */
  input: EvalItem[];

  /** The range of the score. Defaults to `[0, 1]`. */
  range?: numeric[];
}
```

Yet sample code `sample_evaluations_graders.py` sets this additional property: `"image_tag": "2025-05-08"`. Where did that come from?


## EvalGraderAzureAIEvaluator

Why this nested definition? Just define EvalGraderAzureAIEvaluator once.

```
@summary("AzureAIEvaluatorGrader")
model EvalGraderAzureAIEvaluator {
  ...GraderAzureAIEvaluator;
}
```

## Should all properties on `ModelSamplingParams` be required?

Out TypeSpec defines:

```
/** Represents a target specifying an Azure AI model for operations requiring model selection. */
model AzureAIModelTarget extends Target {
  /** The type of target, always `azure_ai_model`. */
  type: "azure_ai_model";

  /** The unique identifier of the Azure AI model. */
  `model`?: string;

  /** The parameters used to control the sampling behavior of the model during text generation. */
  sampling_params?: ModelSamplingParams;
}

/** Represents a set of parameters used to control the sampling behavior of a language model during text generation. */
model ModelSamplingParams {
  /** The temperature parameter for sampling. */
  temperature: float32;

  /** The top-p parameter for nucleus sampling. */
  top_p: float32;

  /** The random seed for reproducibility. */
  seed: int32;

  /** The maximum number of tokens allowed in the completion. */
  max_completion_tokens: int32;
}
```

Note that all properties are REQUIRED on ModelSamplingParam. Yet when I look at the sample `samples\evaluations\sample_model_evaluation.py` it has:

```
"sampling_params": {  # Note: model sampling parameters are optional and can differ per model
    "top_p": 1.0,
    "max_completion_tokens": 2048,
},
```

so only 2 out of the 4 are set. 

## ModelSamplingParams vs. the open from OpenAI

We define this in Foundry TypeSpec

```
/** Represents a set of parameters used to control the sampling behavior of a language model during text generation. */
model ModelSamplingParams {
  /** The temperature parameter for sampling. */
  temperature: float32;

  /** The top-p parameter for nucleus sampling. */
  top_p: float32;

  /** The random seed for reproducibility. */
  seed: int32;

  /** The maximum number of tokens allowed in the completion. */
  max_completion_tokens: int32;
}
```

Yet OpenAI has a similar definition... below is from OpenAI TypeSpec package. Is it intentional that we have our own one?

```
model EvalGraderScoreModelSamplingParams {
  seed?: integer | null;
  top_p?: numeric | null = 1;
  temperature?: numeric | null;
  max_completions_tokens?: integer | null;
  reasoning_effort?: ReasoningEffort;
}
```
