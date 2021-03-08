# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------


class ContainerRepositoryClient(object):
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
        pass

    def delete(self):
        # type: (...) -> None
        """Delete a repository

        :returns: None
        :raises: :class:~azure.core.exceptions.ResourceNotFoundError
        """
        pass

    def delete_registry_artifact(self, digest):
        # type: (str) -> None
        """Delete a registry artifact

        :param digest: The digest of the artifact to be deleted
        :type digest: str
        :returns: None
        :raises: :class:~azure.core.exceptions.ResourceNotFoundError
        """
        pass

    def delete_tag(self, tag):
        # type: (str) -> None
        """Delete a tag

        :param tag: The digest of the artifact to be deleted
        :type tag: str
        :returns: None
        :raises: :class:~azure.core.exceptions.ResourceNotFoundError
        """
        pass

    def get_properties(self):
        # type: (...) -> RepositoryProperties
        """Get the properties of a repository

        :returns: :class:~azure.containerregistry.RepositoryProperties
        :raises: None
        """
        pass

    def get_registry_artifact_properties(self, tag_or_digest, **kwargs):
        # type: (str) -> RegistryArtifactProperties
        """Get the properties of a registry artifact

        :param tag_or_digest: The tag/digest of a registry artifact
        :type tag_or_digest: str
        :returns: :class:~azure.containerregistry.RegistryArtifactProperties
        :raises: :class:~azure.core.exceptions.ResourceNotFoundError
        """
        pass

    def list_registry_artifacts(self, **kwargs):
        # type: (...) -> ItemPaged[RegistryArtifactProperties]
        """List the registry artifacts for a repository

        :returns: ~azure.core.paging.ItemPaged[RegistryArtifactProperties]
        :raises: None
        """
        pass

    def get_tag_properties(self, tag, **kwargs):
        # type: (str) -> TagProperties
        """Get the properties for a tag

        :param tag: The tag to get properties for
        :type tag: str
        :returns: :class:~azure.containerregistry.TagProperties
        :raises: :class:~azure.core.exceptions.ResourceNotFoundError
        """
        pass

    def list_tags(self, **kwargs):
        # type: (...) -> ItemPaged[TagProperties]
        """List the tags for a repository

        :returns: ~azure.core.paging.ItemPaged[TagProperties]
        :raises: None
        """
        pass

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
        pass

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
        pass
