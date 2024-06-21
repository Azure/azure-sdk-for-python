# Release History

## 1.0.0b2 (2024-06-24)

### Features Added

Add `model` as an optional input argument to the `complete` method of `ChatCompletionsClient`.

### Other Changes

- Indicate that `complete` method with `stream=True` returns `Iterable[StreamingChatCompletionsUpdate]` for
the synchronous `ChatComletionsClient`, and `AsyncIterable[StreamingChatCompletionsUpdate]` for the asynchronous
`ChatCompletionsClient`.

- Additional tests

## 1.0.0b1 (2024-06-11)

- Initial beta version
