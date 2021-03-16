# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

from ._base_client import ContainerRegistryBaseClient
from ._models import RepositoryProperties


class ContainerRepositoryClient(ContainerRegistryBaseClient):
    def __init__(self, endpoint, repository, credential, **kwargs):
        # type: (str, str, TokenCredential) -> None
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
        self.endpoint = endpoint
        self.repository = repository
        super(ContainerRepositoryClient, self).__init__(
            endpoint=self.endpoint, credential=credential, **kwargs
        )


    def delete(self, **kwargs):
        # type: (...) -> None
        """Delete a repository

        :returns: None
        :raises: :class:~azure.core.exceptions.ResourceNotFoundError
        """
        self._client.container_registry.delete(self.repository, **kwargs)

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

    def get_properties(self):
        # type: (...) -> RepositoryProperties
        """Get the properties of a repository

        :returns: :class:~azure.containerregistry.RepositoryProperties
        :raises: None
        """
        resp = self._client.container_registry.get_repository_attributes(self.repository)
        return RepositoryProperties.from_generated(resp)

    def get_registry_artifact_properties(self, tag_or_digest, **kwargs):
        # type: (str) -> RegistryArtifactProperties
        """Get the properties of a registry artifact

        :param tag_or_digest: The tag/digest of a registry artifact
        :type tag_or_digest: str
        :returns: :class:~azure.containerregistry.RegistryArtifactProperties
        :raises: :class:~azure.core.exceptions.ResourceNotFoundError
        """
        raise NotImplementedError("Has not been implemented")

    def get_tag_properties(self, tag, **kwargs):
        # type: (str) -> TagProperties
        """Get the properties for a tag

        :param tag: The tag to get properties for
        :type tag: str
        :returns: :class:~azure.containerregistry.TagProperties
        :raises: :class:~azure.core.exceptions.ResourceNotFoundError
        """
        return self._client.tag.get_attributes()

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
        artifacts = self._client.manifests.get_list(
            self.repository,
            last=kwargs.get("last", None),
            n=kwargs.get("n", None),
            orderby=kwargs.get("orderby"))#,
            # cls=lambda objs: [RegistryArtifacts.from_generated(x) for x in objs])

        return RegistryArtifactProperties.from_generated(artifacts)

    def list_tags(self, **kwargs):
        # type: (...) -> ItemPaged[TagProperties]
        """List the tags for a repository

        :returns: ~azure.core.paging.ItemPaged[TagProperties]
        :raises: None
        """
        raise NotImplementedError("Not implemented")
        tags = self._client.container_registry.get_attributes(
            self.repository, **kwargs
        )
        return tags

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
