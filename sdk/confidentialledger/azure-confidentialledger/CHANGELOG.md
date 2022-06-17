# Release History

## 1.0.0 (Unreleased)

GA Data Plane Python SDK for Confidential Ledger.

### Bugs Fixed
- Fixes [[confidentialledger] mypy: function has duplicate type signatures (#23356)](https://github.com/Azure/azure-sdk-for-python/issues/23356)
- User ids that are certificate fingerprints are no longer URL-encoded in the request URI.

### Breaking Changes
- Removed all models. Methods now return JSON directly as a side-effect of migrating to DPG generation.
- In accordance with the updated Swagger, the `sub_ledger_id` fields are now named `collection_id`.
- Renamed `azure.confidentialledger.identity_service` to `azure.confidentialledger_identity_service`.

### Other Changes

- Python 2.7 is no longer supported. Please use Python version 3.6 or later.
- Add new supported API version.
- Updated type hinting.

## 1.0.0b1 (2021-05-12)

- This is the initial release of the Azure Confidential Ledger library.