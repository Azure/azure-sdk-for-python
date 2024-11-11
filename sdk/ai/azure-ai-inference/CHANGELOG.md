# Release History

## 1.0.0b6 (2024-11-11)

### Features Added

* OpenTelemetry tracing:
  * Method `AIInferenceInstrumentor().instrument()` updated with an input argument `enable_content_recording`.
  * Calling `AIInferenceInstrumentor().instrument()` twice no longer results in an exception.
  * Added method `AIInferenceInstrumentor().is_content_recording_enabled()`
* Support [Prompty](https://github.com/microsoft/prompty) and prompt template from string. PromptTemplate class outputs an array of dictionary with OpenAI compatible message format.

### Bugs Fixed

* Fix tracing for asynchronous streaming.

## 1.0.0b5 (2024-10-16)

### Features Added

* Support for OpenTelemetry tracing. Please find more information in the package [README.md](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/ai/azure-ai-inference/README.md).
* When constructing clients using input `credential` of type `AzureKeyCredential`, two HTTP request headers are sent simultaneously for authentication: `Authentication: Beater <key>` and `api-key: <key>` (previously only the first one was sent). This is to support different inference services, removing the need for the application to explicitly specify an additional HTTP request header.

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
