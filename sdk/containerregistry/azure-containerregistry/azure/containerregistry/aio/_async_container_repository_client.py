# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
from typing import TYPE_CHECKING

from ._async_base_client import ContainerRegistryBaseClient
from .._helpers import _is_tag
from .._models import (
    RegistryArtifactProperties,
    RepositoryProperties,
    TagProperties,
)

if TYPE_CHECKING:
    from .._models import ContentPermissions
    from azure.core.async_paging import AsyncItemPaged
    from azure.core.credentials_async import AsyncTokenCredential
    from typing import Dict, Any


class ContainerRepositoryClient(ContainerRegistryBaseClient):
    def __init__(
        self, endpoint: str, repository: str, credential: "AsyncTokenCredential", **kwargs
    ):  # pylint: disable=client-method-missing-type-annotations
        if not endpoint.startswith("https://"):
            endpoint = "https://" + endpoint
        self._endpoint = endpoint
        self._credential = credential
        self.repository = repository
        super(ContainerRepositoryClient, self).__init__(endpoint=self._endpoint, credential=credential, **kwargs)

    async def _get_digest_from_tag(self, tag):
        # type: (str) -> str
        tag_props = await self.get_tag_properties(tag)
        return tag_props.digest

    async def delete(self, **kwargs):
        # type: (...) -> None
        """Delete a repository

        :returns: None
        :raises: :class:~azure.core.exceptions.ResourceNotFoundError
        """
        await self._client.container_registry.delete_repository(self.repository, **kwargs)

    def delete_registry_artifact(self, digest, **kwargs):
        # type: (str) -> None
        """Delete a registry artifact

        :param digest: The digest of the artifact to be deleted
        :type digest: str
        :returns: None
        :raises: :class:~azure.core.exceptions.ResourceNotFoundError
        """
        raise NotImplementedError("Has not been implemented")

    def delete_tag(self, tag, **kwargs):
        # type: (str) -> None
        """Delete a tag

        :param tag: The digest of the artifact to be deleted
        :type tag: str
        :returns: None
        :raises: :class:~azure.core.exceptions.ResourceNotFoundError
        """
        raise NotImplementedError("Has not been implemented")

    async def get_properties(self, **kwargs):
        # type: (...) -> RepositoryProperties
        """Get the properties of a repository

        :returns: :class:~azure.containerregistry.RepositoryProperties
        :raises: None
        """
        # GET '/acr/v1/{name}'
        return RepositoryProperties._from_generated(  # pylint: disable=protected-access
            await self._client.container_registry_repository.get_properties(self.repository, **kwargs)
        )

    def get_registry_artifact_properties(self, tag_or_digest, **kwargs):
        # type: (str, Dict[str, Any]) -> RegistryArtifactProperties
        """Get the properties of a registry artifact

        :param tag_or_digest: The tag/digest of a registry artifact
        :type tag_or_digest: str
        :returns: :class:~azure.containerregistry.RegistryArtifactProperties
        :raises: :class:~azure.core.exceptions.ResourceNotFoundError
        """
        # GET '/acr/v1/{name}/_manifests/{digest}'
        if _is_tag(tag_or_digest):
            tag_or_digest = self._get_digest_from_tag(tag_or_digest)

        return RegistryArtifactProperties._from_generated(  # pylint: disable=protected-access
            self._client.container_registry_repository.get_registry_artifact_properties(
                self.repository, tag_or_digest, **kwargs
            )
        )

    def get_tag_properties(self, tag, **kwargs):
        # type: (str, Dict[str, Any]) -> TagProperties
        """Get the properties for a tag

        :param tag: The tag to get properties for
        :type tag: str
        :returns: :class:~azure.containerregistry.TagProperties
        :raises: :class:~azure.core.exceptions.ResourceNotFoundError
        """
        # GET '/acr/v1/{name}/_tags/{reference}'
        return TagProperties._from_generated(  # pylint: disable=protected-access
            self._client.container_registry_repository.get_tag_properties(self.repository, tag, **kwargs)
        )

    def list_registry_artifacts(self, **kwargs):
        # type: (...) -> AsyncItemPaged[RegistryArtifactProperties]
        """List the artifacts for a repository

        :keyword last: Query parameter for the last item in the previous query
        :type last: str
        :keyword n: Max number of items to be returned
        :type n: int
        :keyword orderby: Order by query parameter
        :type orderby: :class:~azure.containerregistry.RegistryArtifactOrderBy
        :returns: ~azure.core.paging.AsyncItemPaged[RegistryArtifactProperties]
        :raises: None
        """
        # GET /acr/v1/{name}/_manifests
        last = kwargs.pop("last", None)
        n = kwargs.pop("top", None)
        orderby = kwargs.pop("order_by", None)
        return self._client.container_registry_repository.get_manifests(
            self.repository,
            last=last,
            n=n,
            orderby=orderby,
            cls=lambda objs: [
                RegistryArtifactProperties._from_generated(x) for x in objs  # pylint: disable=protected-access
            ],
        )

    def list_tags(self, **kwargs):
        # type: (...) -> AsyncItemPaged[TagProperties]
        """List the tags for a repository

        :param last: Query parameter for the last item in the previous call. Ensuing
            call will return values after last lexically
        :type last: str
        :param order_by: Query paramter for ordering by time ascending or descending
        :returns: ~azure.core.paging.AsyncItemPaged[TagProperties]
        :raises: None
        """
        return self._client.container_registry_repository.get_tags(
            self.repository,
            last=kwargs.pop("last", None),
            n=kwargs.pop("top", None),
            orderby=kwargs.pop("order_by", None),
            digest=kwargs.pop("digest", None),
            cls=lambda objs: [TagProperties._from_generated(o) for o in objs],  # pylint: disable=protected-access
            **kwargs
        )

    async def set_manifest_properties(self, digest, permissions, **kwargs):
        # type: (str, ContentPermissions) -> None
        """Set the properties for a manifest

        :param digest: Digest of a manifest
        :type digest: str
        :param permissions: The property's values to be set
        :type permissions: ContentPermissions
        :returns: None
        :raises: None
        """

        await self._client.container_registry_repository.update_manifest_attributes(
            self.repository, digest, value=permissions._to_generated(), **kwargs  # pylint: disable=protected-access
        )

    async def set_tag_properties(self, tag_or_digest, permissions, **kwargs):
        # type: (str, ContentPermissions) -> None
        """Set the properties for a tag

        :param tag: Tag to set properties for
        :type tag: str
        :param permissions: The property's values to be set
        :type permissions: ContentPermissions
        :returns: None
        :raises: None
        """
        if _is_tag(tag_or_digest):
            tag_or_digest = self._get_digest_from_tag(tag_or_digest)

        await self._client.container_registry_repository.update_manifest_attributes(
            self.repository, tag_or_digest, value=permissions._to_generated(), **kwargs  # pylint: disable=protected-access
        )
