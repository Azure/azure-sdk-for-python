# Release History

## 1.2.0 (2023-04-26)
Add support for computing the claims digest from Azure Confidential Ledger application claims in the `azure.confidentialledger.receipt` module.

### Features Added
- Add `compute_claims_digest` function to compute the claims digest from a list of application claims JSON objects. 
- Add optional argument in `verify_receipt` function to accept a list of application claims and compare the claims digest in the receipt with the computed digest from the plain claims.
- Modify sample code to get and verify a write receipt from a running Confidential Ledger instance, with the option to pass application claims in the verification function.
- Update README with examples and documentation for application claims.

### Other Changes
- Add tests for application claims models and digest computation public method.

## 1.1.0 (2022-12-21)
Add `azure.confidentialledger.receipt` module for Azure Confidential Ledger write transaction receipt verification.

### Features Added
- Add `verify_receipt` function to verify write transaction receipts from a receipt JSON object.
- Add sample code to get and verify a write receipt from a running Confidential Ledger instance.
- Update README with examples and documentation for receipt verification.

### Other Changes
- Add dependency on Python `cryptography` library (`>= 2.1.4`)
- Add tests for receipt verification models and receipt verification public method.

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
