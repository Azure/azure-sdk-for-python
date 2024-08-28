# Release History

## 1.0.0b4 (2024-08-30)

### Features Added

* Support chat completion streaming response with function arguments (tool calls). Add new classes
`StreamingChatResponseMessageUpdate` and `StreamingChatResponseToolCallUpdate`.
* Support text embeddings result in base64 encoded string format.
* Nicely formated print of chat completions and embeddings result objects.

### Breaking Changes

* Classes `ChatCompletionsToolSelectionPreset`, `ChatCompletionsNamedToolSelection` and `ChatCompletionsFunctionToolSelection` renamed to `ChatCompletionsToolChoicePreset` `ChatCompletionsNamedToolChoice` and `ChatCompletionsNamedToolChoiceFunction` respectively.
* Update the object type of `embeddings` property on `EmbeddingsResult`, from `embedding: List[float]` to `embedding: Union[str, List[float]]`.
* Instead of base class `ChatCompletionsToolCall` and derived class `ChatCompletionsFunctionToolCall`, we now have a flat representation of only one class `ChatCompletionsToolCall` that that represents a function tool. This is because the only support tool is a function call.

### Bugs Fixed

* Fix setting of chat completions response format, to allow response in JSON format. See classes `ChatCompletionsResponseFormat` (base class) and
derived classes `ChatCompletionsResponseFormatJSON` and `ChatCompletionsResponseFormatText`.

## 1.0.0b3 (2024-07-31)

### Features Added

* Allow setting default chat completions configuration in the `ChatCompletionsClient` constructor.
* Allow setting default embeddings configuration in the `EmbeddingsClient` constructor.
* Add `model` as an optional input argument to the `embed` method of `EmbeddingsClient`.

## 1.0.0b2 (2024-06-24)

### Features Added

Add `model` as an optional input argument to the `complete` method of `ChatCompletionsClient`.

### Breaking Changes

The field `input_tokens` was removed from class `EmbeddingsUsage`, as this was never defined in the
REST API and the service never returned this value.

## 1.0.0b1 (2024-06-11)

* Initial beta version
