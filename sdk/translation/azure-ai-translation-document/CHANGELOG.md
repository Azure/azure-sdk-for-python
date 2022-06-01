# Release History

## 1.0.0 (Unreleased)

### Features Added

### Breaking Changes

### Bugs Fixed

### Other Changes

## 1.0.0b6 (2022-02-08)

### Other Changes
- Python 2.7 is no longer supported. Please use Python version 3.6 or later.

## 1.0.0b5 (2021-09-08)

### Breaking Changes
- Changed: `list_all_translation_statuses` has been renamed to `list_translation_statuses`
- Changed: `list_all_document_statuses` has been renamed to `list_document_statuses`
- Changed: `TranslationStatus` property `documents_cancelled_count` has been renamed to `documents_canceled_count`
- Changed: `FileFormat` has been renamed to `DocumentTranslationFileFormat`
- Changed: Operation statuses `Cancelled` and `Cancelling` have been renamed to `Canceled` and `Canceling`, respectively.

### Bugs Fixed
- The operation `id` under `details` of the poller object now populates correctly.

## 1.0.0b4 (2021-08-10)

### Features Added

- The single translation input version of `begin_translation(source, target, target_language_code)` now accepts keyword arguments
`storage_type`, `glossaries`, `category_id`, `prefix`, `suffix`, and `source_language_code`.

### Breaking Changes

- Changed: renamed kwargs `translated_before` and `translated_after` to `created_before` and `created_after`, respectively,
for `list_all_document_statuses`.
- Changed: renamed `order_by` sorting query option `createdDateTimeUtc` to `created_on` for `list_all_translation_statuses` and
`list_all_document_statuses`.
  

## 1.0.0b3 (2021-07-07)

### Breaking changes

- `TranslationStatusResult` was renamed to `TranslationStatus`.
- `DocumentStatusResult` was renamed to `DocumentStatus`.
- `get_document_formats` was renamed to `get_supported_document_formats`.
- `get_glossary_formats` was renamed to `get_supported_glossary_formats`.

## 1.0.0b2 (2021-06-08)

This version of the SDK defaults to the latest supported service version, which currently is v1.0

**Breaking changes**

- `create_translation_job` was removed and replaced with `begin_translation` which follows a long-running operation (LRO)
approach. The client method now returns a `DocumentTranslationLROPoller` (or `AsyncDocumentTranslationLROPoller`) to begin the
long-running operation. A call to `.result()` can be made on the poller object to wait until the translation is complete.
See the [README](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/translation/azure-ai-translation-document/README.md) for more information about LROs.
- Upon completion of the LRO, `begin_translation` now returns a pageable of `DocumentStatusResult`. All job-level metadata can still
be found on `poller.details`.
- `has_completed` has been removed from `JobStatusResult` and `DocumentStatusResult`. Use `poller.done()` to check if the
translation has completed.
- Client method `wait_until_done` has been removed. Use `poller.result()` to wait for the LRO to complete.
- Client method `list_submitted_jobs` has been renamed to `list_all_translation_statuses`.
- Client method `get_job_status` has been renamed to `get_translation_status`.
- Client method `cancel_job` has been renamed to `cancel_translation`.
- Parameter `job_id` was renamed to `translation_id` for `get_translation_status`, `cancel_translation`, `list_all_document_statuses`, and `get_document_status`.
- `JobStatusResult` has been renamed to `TranslationStatusResult`.
- `DocumentStatusResult` property `translate_to` has been renamed to `translated_to`

**New features**

- Authentication using `azure-identity` credentials now supported.
  - see the [Azure Identity documentation](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/identity/azure-identity/README.md) for more information.
- Added paging and filtering options to `list_all_document_statuses` and `list_submitted_jobs`.
- The input to `begin_translation` now accepts either the parameter `inputs` as a `List[DocumentTranslationInput]` to
perform multiple translations, or the parameters `source_url`, `target_url`, and `target_language_code` to perform a
single translation of your documents.

**Dependency updates**

- Package requires [azure-core](https://pypi.org/project/azure-core/) version 1.14.0 or greater.

## 1.0.0b1 (2021-04-06)

This is the first beta package of the azure-ai-translation-document client library that targets the Document Translation
service version `1.0-preview.1`. This package's documentation and samples demonstrate the new API.
