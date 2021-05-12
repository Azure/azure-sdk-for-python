# Release History

## 1.0.0b3 (2021-05-12)
First bug fix release for Python SDK

### Features Added

- Added reset_policy API which was missed in the previous API.
- Added models for all the generated API types.
- Documentation cleanup for several APIs.

### Breaking Changes

- Creating the `StoredAttestationPolicy` model type means that the `attestation_policy`
    kwargs parameter for the constructor is no longer needed.
- Several parameters for the `AttestationResult` type have been renamed, and
    several parameters which were shared with `AttestationToken` have been
    removed. In general, the naming changes removed some protocol specific
    elements and replaced them with friendlier names. For instance the `iss`
    attribute was renamed `issuer`.

## 1.0.0b2 (2021-05-11)

Preliminary release for Python SDK

### Features Added

- Preliminary implementation of a Track 2 SDK for the attestation service.

### Breaking Changes

- Complete reimplementation of the API surface, follows the API patterns already
established for the attestation service.

## 1.0.0b1 (2021-01-15)

Initial early preview release for MAA Data Plane SDK
Demonstrates use of the machine generated MAA APIs.

- Initial Release
