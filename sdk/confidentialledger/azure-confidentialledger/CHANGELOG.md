# Release History

## 1.0.0 (Unreleased)

### Bugs Fixed
- Fixes [[confidentialledger] mypy: function has duplicate type signatures (#23356)](https://github.com/Azure/azure-sdk-for-python/issues/23356)
- User ids that are certificate fingerprints are no longer URL-encoded in the request URI.

### Breaking Changes
- Removed `TransactionStatus` model.
- `get_ledger_entry` and `wait_until_durable` align with [Azure Python SDK conventions](https://docs.microsoft.com/en-us/python/api/azure-core/azure.core.pipeline.policies.retrypolicy?view=azure-python).

### Other Changes

- Python 2.7 is no longer supported. Please use Python version 3.6 or later.
- Add new supported API version.
- Updated type hinting.

## 1.0.0b1 (2021-05-12)

- This is the initial release of the Azure Confidential Ledger library.