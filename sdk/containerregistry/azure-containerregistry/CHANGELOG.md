# Release History

## 1.1.0b5 (Unreleased)

### Features Added

### Breaking Changes

### Bugs Fixed

### Other Changes
- Changed the digest validation exception type to `ManifestDigestValidationError` in `set/get manifest` and `upload/download blob` operations.

## 1.1.0b4 (2023-04-25)

### Features Added
- Added an optional kwarg `media_type` in `set_manifest()` to enable uploading image manifests of any type.

### Breaking Changes
- Renamed `upload_manifest()` to `set_manifest()`, and changed to consume manifest in `JSON` instead of `OCIManifest` type.
- Renamed `download_manifest()` to `get_manifest()`, and changed it's return type from `DownloadManifestResult` to `GetManifestResult`.

### Other Changes
- Changed the default audience to `"https://containerregistry.azure.net"` which works for all clouds.

## 1.1.0b3 (2023-04-04)

### Features Added
- Supported uploading and downding large OCI artifact blobs in synchronous and asynchronous `ContainerRegistryClient`.
- Published model `DownloadManifestResult`, `DownloadBlobStream` and `AsyncDownloadBlobStream`.

### Breaking Changes
- Suppress the response error with status code `404` in `delete_blob()`.
- Added to return blob size in bytes in `upload_blob()`.
- Changed `download_blob()` return type from `DownloadBlobResult` to `DownloadBlobStream` and `AsyncDownloadBlobStream`.

## 1.1.0b2 (2023-03-24)

### Bugs Fixed
- Fixed a `TypeError` when call `list_tag()` in an empty repository. ([#28234](https://github.com/Azure/azure-sdk-for-python/issues/28234))
- Fixed a `TypeError` when call `list_manifest()` in an empty repository. ([#28432](https://github.com/Azure/azure-sdk-for-python/issues/28432))

### Other Changes
- Added default value `"https://management.azure.com"` to kwarg `audience` in `ContainerRegistryClient`. ([#22229](https://github.com/Azure/azure-sdk-for-python/issues/22229))
- Python 3.6 is no longer supported. Please use Python version 3.7 or later.
- Bumped minimum dependency on `azure-core` to `>=1.24.0`
- Dropped `msrest` requirement.
- Added dependency `isodate` with version range `>=0.6.0`(`isodate` was required by `msrest`).

## 1.1.0b1 (2022-05-10)

### Features Added
- Supported uploading and downloading OCI manifests and artifact blobs in synchronous `ContainerRegistryClient`.
### Other Changes

- Fixed a spell error in a property of `RepositoryProperties` to `last_updated_on`.
- Bumped dependency on `azure-core` to `>=1.23.0`.

## 1.0.0 (2022-01-25)

### Features Added

- Supported passing the rest api version via `ContainerRegistryClient`.

### Breaking Changes

- Renamed the property `size` of `ArtifactManifestProperties` to `size_in_bytes`.
- Renamed `TagOrder` to `ArtifactTagOrder`.
- Renamed `ManifestOrder` to `ArtifactManifestOrder`.

### Other Changes

- Python 2.7 is no longer supported. Please use Python version 3.6 or later.

## 1.0.0b7 (2021-11-19)

### Features Added

- Updated the supported rest api version to be the stable "2021-07-01".
- Removed the property `teleport_enabled` in `RepositoryProperties`.

## 1.0.0b6 (2021-09-08)

### Breaking Changes

- Removed `credential_scopes` keyword.
- Added `audience` keyword, which allows customers to select from available audiences or provide their own audience string. This keyword is required when creating a client.

## 1.0.0b5 (2021-08-11)

### Bugs Fixed

- Closed session of `ChallengePolicyClient` in context manager    #20000

### Other Changes

- Bumped dependency on `msrest` to `>=0.6.21`

## 1.0.0b4 (2021-07-07)

### Bugs Fixed

- Fixed a bug where `credential_scopes` keyword on `ContainerRegistryClient` was not passed through and the client could not authenticate with foreign clouds.

## 1.0.0b3 (2021-06-08)

- Removed `DeleteRepositoryResult`. `ContainerRegistryClient.delete_repository` now returns `None`
- Removed `writeable_properties` objects, placing `can_delete/read/write/list` properties on the immediate `Repository/Tag/ArtifactManifestProperties` objects
- Removed `ContainerRepository` and `RegistryArtifact` classes. The methods for acting on a repository and a registry artifact are now contained in the `ContainerRegistryClient` object.
- Parsed refresh token expiration time from returned JWT.
- The `delete_repository` and `get_repository` methods parameters have been renamed from `repository_name` to `repository`.

## 1.0.0b2 (2021-05-11)

- Renamed `DeletedRepositoryResult` to `DeleteRepositoryResult`
- Renamed `DeletedRepositoryResult.deleted_registry_artifact_digests` to `deleted_manifests`
- Renamed `TagProperties` to `ArtifactTagProperties`
- Renamed `ContentPermissions` to `ContentProperties`
- Renamed `content_permissions` attributes on `TagProperties`, `RepositoryProperties`, and `RegistryArtifactProperties` to `writeable_properties`.
- Added anonymous access capabilities to client by passing in `None` to credential.

## 1.0.0b1 (2021-04-06)

- First release of the Azure Container Registry library for Python
