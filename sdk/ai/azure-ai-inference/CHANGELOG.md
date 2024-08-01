# Release History

## 1.0.0b4 (Unreleased)

### Features Added

### Breaking Changes

### Bugs Fixed

### Other Changes

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
