# Release History

## 1.0.0b4 (2021-06-08)

### Features Added

- Added reset_policy API which was missed in the previous API.
- Added models for all the generated API types.
- Documentation cleanup for several APIs.

### Breaking Changes

- Creating the `StoredAttestationPolicy` model type means that the `attestation_policy`
    kwargs parameter for the constructor has been replaced with a positional `policy` parameter. As a result of this change, this code:

```python
StoredAttestationPolicy(attestation_policy=str(attestation_policy).encode('utf-8')))
```

changes to:

```python
StoredAttestationPolicy(attestation_policy)
```

- Several parameters for the `AttestationResult` type have been renamed, and
    several parameters which were shared with `AttestationToken` have been
    removed. In general, the naming changes removed some protocol specific
    elements and replaced them with friendlier names. Finally, the deprecated
    attributes have been removed from the `AttestationResult`

    Full set of changes:
  - `iss` renamed to `issuer`
  - `cnf` renamed to `confirmation`
  - `jti` renamed to `unique_identifier`
  - `iat` removed
  - `exp` removed
  - `nbf` removed
  - `deprecated_version` removed
  - `deprecated_is_debuggable` removed
  - `deprecated_sgx_collateral` removed
  - `deprecated_enclave_held_data` removed
  - `deprecated_enclave_held_data2` removed
  - `deprecated_product_id` removed
  - `deprecated_mr_enclave` removed
  - `deprecated_mr_signer` removed
  - `deprecated_svn` removed
  - `deprecated_tee` removed
  - `deprecated_policy_signer` removed
  - `deprecated_policy_hash` removed
  - `deprecated_rp_data` removed

  If customers need to access the removed or renamed fields directly, they can
  use the `get_body` method of the `AttestationResponse` object:

  ```python
    if response.token.get_body().deprecated_tee != 'sgx':
        print("Unexpected tee claim in token")
  ```

## 1.0.0b2 (2021-05-11)

### Features Added

- Preliminary implementation of a Track 2 SDK for the attestation service.

### Breaking Changes

- Complete reimplementation of the API surface, follows the API patterns already
established for the attestation service.

## 1.0.0b1 (2021-01-15)

Initial early preview release for MAA Data Plane SDK
Demonstrates use of the machine generated MAA APIs.

- Initial Release
