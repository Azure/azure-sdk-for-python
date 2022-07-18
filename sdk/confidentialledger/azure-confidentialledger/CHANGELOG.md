# Release History

## 1.0.0 (2022-07-19)

GA Data Plane Python SDK for Confidential Ledger.

### Bugs Fixed
- User ids that are certificate fingerprints are no longer URL-encoded in the request URI.

### Breaking Changes
- Removed all models. Methods now return JSON directly.
- `sub_ledger_id` fields are now named `collection_id`.
- `azure.confidentialledger.identity_service` has been renamed to `azure.confidentialledger.certificate`.
- `ConfidentialLedgerIdentityServiceClient` is now `ConfidentialLedgerCertificateClient`.
- `post_ledger_entry` has been renamed to `create_ledger_entry`.

### Other Changes
- Python 2.7 is no longer supported. Please use Python version 3.7 or later.
- Convenience poller methods added for certain long-running operations.
- Add new supported API version: `2022-05-13`.

## 1.0.0b1 (2021-05-12)

- This is the initial release of the Azure Confidential Ledger library.