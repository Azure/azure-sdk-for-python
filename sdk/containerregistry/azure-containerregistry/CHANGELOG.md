# Release History

## 1.0.0b4 (2021-07-07)
### Bugs Fixed
* Fixes a bug where `credential_scopes` keyword on `ContainerRegistryClient` was not passed through and the client could not authenticate with foreign clouds.

## 1.0.0b3 (2021-06-08)
* Removes `DeleteRepositoryResult`. `ContainerRegistryClient.delete_repository` now returns `None`
* Removed `writeable_properties` objects, placing `can_delete/read/write/list` properties on the immediate `Repository/Tag/ArtifactManifestProperties` objects
* Removed `ContainerRepository` and `RegistryArtifact` classes. The methods for acting on a repository and a registry artifact are now contained in the `ContainerRegistryClient` object.
* Parses refresh token expiration time from returned JWT.
* The `delete_repository` and `get_repository` methods parameters have been renamed from `repository_name` to `repository`.

## 1.0.0b2 (2021-05-11)
* Rename `DeletedRepositoryResult` to `DeleteRepositoryResult`
* Rename `DeletedRepositoryResult.deleted_registry_artifact_digests` to `deleted_manifests`
* Rename `TagProperties` to `ArtifactTagProperties`
* Rename `ContentPermissions` to `ContentProperties`
* Rename `content_permissions` attributes on `TagProperties`, `RepositoryProperties`, and `RegistryArtifactProperties` to `writeable_properties`.
* Adds anonymous access capabilities to client by passing in `None` to credential.

## 1.0.0b1 (2021-04-06)
* First release of the Azure Container Registry library for Python
