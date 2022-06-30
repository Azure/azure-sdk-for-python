# Release History

## 1.0.0 (Unreleased)

GA Data Plane Python SDK for Confidential Ledger.

### Bugs Fixed
- User ids that are certificate fingerprints are no longer URL-encoded in the request URI.

### Breaking Changes
- Removed all models. Methods now return JSON directly.
- `sub_ledger_id` fields are now named `collection_id`.

### Other Changes
- Python 2.7 is no longer supported. Please use Python version 3.6 or later.
- Add new supported API versions: `2022-20-04-preview` and `2022-05-13`.

## 1.0.0b1 (2021-05-12)

- This is the initial release of the Azure Confidential Ledger library.