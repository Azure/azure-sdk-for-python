# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
from typing import TYPE_CHECKING

from ._base_client import ContainerRegistryBaseClient
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
        if not endpoint.startswith("https://"):
            endpoint = "https://" + endpoint
        self._endpoint = endpoint
        self.repository = repository
        super(ContainerRepositoryClient, self).__init__(endpoint=self._endpoint, credential=credential, **kwargs)

    def delete(self, **kwargs):
        # type: (...) -> None
        """Delete a repository

        :returns: None
        :raises: :class:~azure.core.exceptions.ResourceNotFoundError
        """
        self._client.container_registry.delete_repository(self.repository, **kwargs)

    def delete_registry_artifact(self, digest):
        # type: (str) -> None
        """Delete a registry artifact

        :param digest: The digest of the artifact to be deleted
        :type digest: str
        :returns: None
        :raises: :class:~azure.core.exceptions.ResourceNotFoundError
        """
        raise NotImplementedError("Has not been implemented")

    def delete_tag(self, tag):
        # type: (str) -> None
        """Delete a tag

        :param tag: The digest of the artifact to be deleted
        :type tag: str
        :returns: None
        :raises: :class:~azure.core.exceptions.ResourceNotFoundError
        """
        raise NotImplementedError("Has not been implemented")

    def get_digest_from_tag(self, tag):
        # type: (str) -> str
        for t in self.list_tags():
            if t.tag == tag:
                return t.digest
        return ""

    def get_properties(self):
        # type: (...) -> RepositoryProperties
        """Get the properties of a repository

        :returns: :class:~azure.containerregistry.RepositoryProperties
        :raises: None
        """
        # GET '/acr/v1/{name}'
        resp = self._client.container_registry_repository.get_properties(self.repository)
        return RepositoryProperties._from_generated(resp)  # pylint: disable=protected-access

    def get_registry_artifact_properties(self, tag_or_digest, **kwargs):
        # type: (str, Dict[str, Any]) -> RegistryArtifactProperties
        """Get the properties of a registry artifact

        :param tag_or_digest: The tag/digest of a registry artifact
        :type tag_or_digest: str
        :returns: :class:~azure.containerregistry.RegistryArtifactProperties
        :raises: :class:~azure.core.exceptions.ResourceNotFoundError
        """
        # GET '/acr/v1/{name}/_manifests/{digest}'
        # TODO: If `tag_or_digest` is a tag, need to do a get_tags to find the appropriate digest,
        # generated code only takes a digest
        if self._is_tag(tag_or_digest):
            tag_or_digest = self.get_digest_from_tag(tag_or_digest)
        # TODO: The returned object from the generated code is not being deserialized properly
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
        # type: (...) -> ItemPaged[RegistryArtifactProperties]
        """List the registry artifacts for a repository

        :keyword last: Query parameter for the last item in the previous query
        :type last: str
        :keyword n: Max number of items to be returned
        :type n: int
        :keyword orderby: Order by query parameter
        :type orderby: :class:~azure.containerregistry.RegistryArtifactOrderBy
        :returns: ~azure.core.paging.ItemPaged[RegistryArtifactProperties]
        :raises: None
        """
        raise NotImplementedError("Not implemented")
        # TODO: turn this into an ItemPaged
        # artifacts = self._client.manifests.get_list(
        #     self.repository,
        #     last=kwargs.get("last", None),
        #     n=kwargs.get("n", None),
        #     orderby=kwargs.get("orderby"),
        # )  # ,
        # # cls=lambda objs: [RegistryArtifacts._from_generated(x) for x in objs])

        # return RegistryArtifactProperties._from_generated(artifacts)

    def list_tags(self, **kwargs):
        # type: (...) -> ItemPaged[TagProperties]
        """List the tags for a repository

        :param last: Query parameter for the last item in the previous call. Ensuing
            call will return values after last lexically
        :type last: str
        :param order_by: Query paramter for ordering by time ascending or descending
        :returns: ~azure.core.paging.ItemPaged[TagProperties]
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

    def set_manifest_properties(self, digest, value):
        # type: (str, ContentPermissions) -> None
        """Set the properties for a manifest

        :param digest: Digest of a manifest
        :type digest: str
        :param value: The property's values to be set
        :type value: ContentPermissions
        :returns: ~azure.core.paging.ItemPaged[TagProperties]
        :raises: None
        """
        raise NotImplementedError("Has not been implemented")

    def set_tag_properties(self, tag, permissions):
        # type: (str, ContentPermissions) -> None
        """Set the properties for a tag

        :param tag: Tag to set properties for
        :type tag: str
        :param value: The property's values to be set
        :type value: ContentPermissions
        :returns: ~azure.core.paging.ItemPaged[TagProperties]
        :raises: None
        """
        raise NotImplementedError("Has not been implemented")
