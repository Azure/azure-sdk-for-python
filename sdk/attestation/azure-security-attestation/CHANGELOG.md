# Release History

## 1.1.0 (Unreleased)

### Features Added

### Breaking Changes
* Added `TpmAttestationResult` model
* Changed `attest_tpm` parameter from str to bytes to match `attest_open_enclave` and `attest_sgx_enclave`

### Bugs Fixed

### Other Changes

* Python 2.7 is no longer supported. Please use Python version 3.6 or later.
* Update attestTpm tests to pass in bytes and handle returned TpmAttestationResult.

## 1.0.0 (2021-07-06)

### Features Added

Sample cleanup - instead of using `ClientSecretCredentials`, the samples now use
DefaultAzureCredential.

### Breaking Changes

* TPM attestation takes a JSON string parameter and returns a JSON string parameter.
  * `TPMAttestationRequest` and `TPMAttestationResponse` type were removed.
* `confirmation` attribute removed from `AttestationResult` type.
* The `AttestationSigningKey` type was removed, replaced with a `signing_key` and
 `signing_certificate` kwargs parameter.
* All certificates and keys accepted and returned by the SDK are now PEM encoded
  strings instead of DER encoded arrays of bytes for easier manipulation and
  interoperability.
* Removed `AttestationResponse` type, token value merged into `AttestationResult`,
  `PolicyResult`, etc.
* Removed `TokenValidationOptions` type and merged the validation options into
  keyword arguments on the APIs which validate returned tokens. Those keyword
  arguments can also be specified on the Client classes to simplify individual
  API invocations.
* Renamed `instance_url` parameter to the constructors to `endpoint`.
* Many optional fields in `AttestationResult` were made non-optional.
* `AttestationToken._validate_token` is made internal-only, and now returns `None`.
  * The caller provided `validation_callback` now must throw exceptions on invalid
  tokens rather than returning `False`.
* Removed the `AttestationData` type, instead the `attest_xxx` APIs take two sets
  of parameters: `inittime_data` and `inittime_json` and `runtime_data` and `runtime_json`.
  if the `_json` value is set, the value of the parameter is an array of UTF8 encoded
  JSON values, if the `_data` value is set, the value of the parameter is an array
  of bytes.
* The `get_policy` API now returns a `Tuple[str, AttestationToken]` to simplify
  the consumption experience.
* The `get_policy_management_certificates` API also returns a `Tuple[list[list[string]], AttestationToken]` to simplify the consumption experience. Note that each of the entries
in the list is a PEM encoded X.509 certificate.

To call into the attest APIs if you care about the attestation policy and token,
you can write:

```python
policy, token = attest_client.get_policy(AttestationType.SGX_ENCLAVE)
```

If you only care about the policy, you can write any of the following:

```python
policy, _ = attest_client.get_policy(AttestationType.SGX_ENCLAVE)
```

or

```python
policy = attest_client.get_policy(AttestationType.SGX_ENCLAVE)[0]
```

or

```python
response = attest_client.get_policy(AttestationType.SGX_ENCLAVE)
policy = response[0]
```

* The `AttestationToken` class no longer inherits from `Generic`.
* The `attest_sgx_enclave`, and `attest_openenclave` APIs now return a tuple of
  `AttestationResult`, `AttestationToken`, similar to the `get_policy` API.
* The `set_policy`, `reset_policy`, `add_policy_management_certificate`, and `remove_policy_management_certificate` APIs all return a tuple.
* The `AttestationToken.get_body()` API was renamed `AttestationToken.body()`
* Several time related properties were renamed to be consistent with the usage from
  keyvault:
  * The `expiration_time` property on `AttestationToken` was renamed to `expires`.
  * The `issuance_time` property on `AttestationToken` was renamed to `issued_on`.
  * The `not_before_time` property on `AttestationToken` was renamed to `not_before`.
* The `StoredAttestationPolicy` model type has been removed. To validate the attestation policy hash, use the `AttestationPolicyToken` model object instead.
* The `get_openidmetadata` API has been renamed `get_open_id_metadata`.

## 1.0.0b4 (2021-06-08)

### Features Added

* Added reset_policy API.
* Added models.
* Documentation cleanup.

### Breaking Changes

* Creating the `StoredAttestationPolicy` model type means that the `attestation_policy`
    kwargs parameter for the constructor has been replaced with a positional `policy` parameter. As a result of this change, this code:

```python
StoredAttestationPolicy(attestation_policy=str(attestation_policy).encode('utf-8')))
```

changes to:

```python
StoredAttestationPolicy(attestation_policy)
```

* Several parameters for the `AttestationResult` type have been renamed, and
    several parameters which were shared with `AttestationToken` have been
    removed. In general, the naming changes removed some protocol specific
    elements and replaced them with friendlier names. Finally, the deprecated
    attributes have been removed from the `AttestationResult`

    Full set of changes:
  * `iss` renamed to `issuer`
  * `cnf` renamed to `confirmation`
  * `jti` renamed to `unique_identifier`
  * `iat` removed
  * `exp` removed
  * `nbf` removed
  * `deprecated_version` removed
  * `deprecated_is_debuggable` removed
  * `deprecated_sgx_collateral` removed
  * `deprecated_enclave_held_data` removed
  * `deprecated_enclave_held_data2` removed
  * `deprecated_product_id` removed
  * `deprecated_mr_enclave` removed
  * `deprecated_mr_signer` removed
  * `deprecated_svn` removed
  * `deprecated_tee` removed
  * `deprecated_policy_signer` removed
  * `deprecated_policy_hash` removed
  * `deprecated_rp_data` removed

  If customers need to access the removed or renamed fields directly, they can
  use the `get_body` method of the `AttestationResponse` object:

  ```python
    if response.token.get_body().deprecated_tee != 'sgx':
        print("Unexpected tee claim in token")
  ```

## 1.0.0b2 (2021-05-11)

### Features Added

* Preliminary implementation of a Track 2 SDK for the attestation service.

### Breaking Changes

* Complete reimplementation of the API surface, follows the API patterns already
established for the attestation service.

## 1.0.0b1 (2021-01-15)

Initial early preview release for MAA Data Plane SDK
Demonstrates use of the machine generated MAA APIs.

* Initial Release
