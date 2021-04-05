# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
from typing import TYPE_CHECKING

from azure.core.tracing.decorator import distributed_trace

from ._base_client import ContainerRegistryBaseClient
from ._helpers import _is_tag
from ._models import RepositoryProperties, TagProperties, RegistryArtifactProperties

if TYPE_CHECKING:
    from typing import Any, Dict
    from azure.core.paging import ItemPaged
    from azure.core.credentials import TokenCredential
    from ._models import ContentPermissions


class ContainerRepositoryClient(ContainerRegistryBaseClient):
    def __init__(self, endpoint, repository, credential, **kwargs):
        # type: (str, str, TokenCredential, Dict[str, Any]) -> None
        """Create a ContainerRepositoryClient from an endpoint, repository name, and credential

        :param endpoint: An ACR endpoint
        :type endpoint: str
        :param repository: The name of a repository
        :type repository: str
        :param credential: The credential with which to authenticate
        :type credential: TokenCredential
        :returns: None
        :raises: None
        """
        if not endpoint.startswith("https://") and not endpoint.startswith("http://"):
            endpoint = "https://" + endpoint
        self._endpoint = endpoint
        self.repository = repository
        super(ContainerRepositoryClient, self).__init__(endpoint=self._endpoint, credential=credential, **kwargs)

    def _get_digest_from_tag(self, tag):
        # type: (str) -> str
        tag_props = self.get_tag_properties(tag)
        return tag_props.digest

    @distributed_trace
    def delete(self, **kwargs):
        # type: (...) -> None
        """Delete a repository

        :returns: None
        :raises: :class:~azure.core.exceptions.ResourceNotFoundError
        """
        self._client.container_registry.delete_repository(self.repository, **kwargs)

    @distributed_trace
    def delete_registry_artifact(self, digest, **kwargs):
        # type: (str) -> None
        """Delete a registry artifact. A registry artifact can only be deleted from the digest

        :param digest: The digest of the artifact to be deleted
        :type digest: str
        :returns: None
        :raises: :class:~azure.core.exceptions.ResourceNotFoundError
        """
        self._client.container_registry_repository.delete_manifest(self.repository, digest, **kwargs)

    @distributed_trace
    def delete_tag(self, tag, **kwargs):
        # type: (str) -> None
        """Delete a tag from a repository

        :param tag: The digest of the artifact to be deleted
        :type tag: str
        :returns: None
        :raises: :class:~azure.core.exceptions.ResourceNotFoundError
        """
        self._client.container_registry_repository.delete_tag(self.repository, tag, **kwargs)

    @distributed_trace
    def get_properties(self, **kwargs):
        # type: (...) -> RepositoryProperties
        """Get the properties of a repository

        :returns: :class:~azure.containerregistry.RepositoryProperties
        :raises: None
        """
        # GET '/acr/v1/{name}'
        return RepositoryProperties._from_generated(  # pylint: disable=protected-access
            self._client.container_registry_repository.get_properties(self.repository, **kwargs)
        )

    @distributed_trace
    def get_registry_artifact_properties(self, tag_or_digest, **kwargs):
        # type: (str, Dict[str, Any]) -> RegistryArtifactProperties
        """Get the properties of a registry artifact

        :param tag_or_digest: The tag/digest of a registry artifact
        :type tag_or_digest: str
        :returns: :class:~azure.containerregistry.RegistryArtifactProperties
        :raises: :class:~azure.core.exceptions.ResourceNotFoundError
        """
        if _is_tag(tag_or_digest):
            tag_or_digest = self._get_digest_from_tag(tag_or_digest)

        return RegistryArtifactProperties._from_generated(  # pylint: disable=protected-access
            self._client.container_registry_repository.get_registry_artifact_properties(
                self.repository, tag_or_digest, **kwargs
            )
        )

    @distributed_trace
    def get_tag_properties(self, tag, **kwargs):
        # type: (str, Dict[str, Any]) -> TagProperties
        """Get the properties for a tag

        :param tag: The tag to get properties for
        :type tag: str
        :returns: :class:~azure.containerregistry.TagProperties
        :raises: :class:~azure.core.exceptions.ResourceNotFoundError
        """
        return TagProperties._from_generated(  # pylint: disable=protected-access
            self._client.container_registry_repository.get_tag_properties(self.repository, tag, **kwargs)
        )

    @distributed_trace
    def list_registry_artifacts(self, **kwargs):
        # type: (...) -> ItemPaged[RegistryArtifactProperties]
        """List the artifacts for a repository

        :keyword last: Query parameter for the last item in the previous query
        :type last: str
        :keyword page_size: Number of items per page
        :type page_size: int
        :keyword order_by: Query parameter for ordering by time ascending or descending
        :type order_by: :class:~azure.containerregistry.RegistryArtifactOrderBy
        :returns: ~azure.core.paging.ItemPaged[RegistryArtifactProperties]
        :raises: None
        """
        last = kwargs.pop("last", None)
        n = kwargs.pop("page_size", None)
        orderby = kwargs.pop("order_by", None)
        return self._client.container_registry_repository.get_manifests(
            self.repository,
            last=last,
            n=n,
            orderby=orderby,
            cls=lambda objs: [
                RegistryArtifactProperties._from_generated(x) for x in objs  # pylint: disable=protected-access
            ],
            **kwargs
        )

    @distributed_trace
    def list_tags(self, **kwargs):
        # type: (...) -> ItemPaged[TagProperties]
        """List the tags for a repository

        :keyword last: Query parameter for the last item in the previous call. Ensuing
            call will return values after last lexically
        :type last: str
        :keyword order_by: Query parameter for ordering by time ascending or descending
        :type order_by: :class:~azure.containerregistry.TagOrderBy
        :returns: ~azure.core.paging.ItemPaged[TagProperties]
        :raises: None
        """
        return self._client.container_registry_repository.get_tags(
            self.repository,
            last=kwargs.pop("last", None),
            n=kwargs.pop("page_size", None),
            orderby=kwargs.pop("order_by", None),
            digest=kwargs.pop("digest", None),
            cls=lambda objs: [TagProperties._from_generated(o) for o in objs],  # pylint: disable=protected-access
            **kwargs
        )

    @distributed_trace
    def set_manifest_properties(self, digest, permissions, **kwargs):
        # type: (str, ContentPermissions) -> RegistryArtifactProperties
        """Set the properties for a manifest

        :param digest: Digest of a manifest
        :type digest: str
        :param permissions: The property's values to be set
        :type permissions: ContentPermissions
        :returns: :class:~azure.containerregistry.RegistryArtifactProperties
        :raises: ResourceNotFoundError
        """
        return RegistryArtifactProperties._from_generated(  # pylint: disable=protected-access
            self._client.container_registry_repository.update_manifest_attributes(
                self.repository, digest, value=permissions._to_generated(), **kwargs  # pylint: disable=protected-access
            )
        )

    @distributed_trace
    def set_tag_properties(self, tag, permissions, **kwargs):
        # type: (str, ContentPermissions) -> TagProperties
        """Set the properties for a tag

        :param tag: Tag to set properties for
        :type tag: str
        :param permissions: The property's values to be set
        :type permissions: ContentPermissions
        :returns: TagProperties
        :raises: ResourceNotFoundError
        """
        return TagProperties._from_generated(  # pylint: disable=protected-access
            self._client.container_registry_repository.update_tag_attributes(
                self.repository, tag, value=permissions._to_generated(), **kwargs  # pylint: disable=protected-access
            )
        )
