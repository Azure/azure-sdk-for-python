# Release History

## 1.0.0b2 (Unreleased)

This version of the SDK defaults to the latest supported service version, which currently is v1.0

**Breaking changes**

- `create_translation_job` was renamed to `begin_translation` and now returns a `DocumentTranslationPoller`
(or `AsyncDocumentTranslationPoller`) to begin the long-running operation. Call `.result()` on the poller object
to wait until the translation is complete. See the README for more information about LROs.
- Upon completion of the LRO, `begin_translation` now returns a pageable of `DocumentStatusResult`. All job-level metadata can still
be found on `poller.details`.
- `has_completed` has been removed from `JobStatusResult` and `DocumentStatusResult`. Use `poller.done()` to check if the 
translation has completed.

**New features**

- Authentication using `azure-identity` credentials now supported.
  - see the [Azure Identity documentation](https://github.com/Azure/azure-sdk-for-python/blob/master/sdk/identity/azure-identity/README.md) for more information.
- Added paging and filtering options to `list_all_document_statuses` and `list_submitted_jobs`.

**Dependency updates**

- Package requires [azure-core](https://pypi.org/project/azure-core/) version 1.14.0 or greater.

## 1.0.0b1 (2021-04-06)

This is the first beta package of the azure-ai-translation-document client library that targets the Document Translation 
service version `1.0-preview.1`. This package's documentation and samples demonstrate the new API.
