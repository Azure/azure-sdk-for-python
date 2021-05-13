# Release History

## 1.0.0b2 (2021-05-11)
* Rename `DeletedRepositoryResult` to `DeleteRepositoryResult`
* Rename `DeletedRepositoryResult.deleted_registry_artifact_digests` to `deleted_manifests`
* Rename `TagProperties` to `ArtifactTagProperties`
* Rename `ContentPermissions` to `ContentProperties`
* Rename `content_permissions` attributes on `TagProperties`, `RepositoryProperties`, and `RegistryArtifactProperties` to `writeable_properties`.
* Adds anonymous access capabilities to client by passing in `None` to credential.

## 1.0.0b1 (2021-04-06)
* First release of the Azure Container Registry library for Python
