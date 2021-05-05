# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
from typing import TYPE_CHECKING, Any, Dict

from azure.core.exceptions import (
    ClientAuthenticationError,
    ResourceNotFoundError,
    ResourceExistsError,
    HttpResponseError,
    map_error,
)
from azure.core.paging import ItemPaged
from azure.core.tracing.decorator import distributed_trace

from ._base_client import ContainerRegistryBaseClient
from ._generated.models import AcrErrors
from ._helpers import _is_tag, _parse_next_link
from ._models import (
    DeleteRepositoryResult,
    ArtifactManifestProperties,
    RepositoryProperties,
    ArtifactTagProperties,
)

if TYPE_CHECKING:
    from azure.core.credentials import TokenCredential
    from ._models import ContentProperties


class ContainerRepositoryClient(ContainerRegistryBaseClient):
    def __init__(self, endpoint, repository, credential, **kwargs):
        # type: (str, str, TokenCredential, Dict[str, Any]) -> None
        """Create a ContainerRepositoryClient from an endpoint, repository name, and credential

        :param endpoint: An ACR endpoint
        :type endpoint: str
        :param repository: The name of a repository
        :type repository: str
        :param credential: The credential with which to authenticate
        :type credential: :class:`~azure.core.credentials.TokenCredential`
        :returns: None
        :raises: None

        .. admonition:: Example:

            .. literalinclude:: ../samples/sample_create_client.py
                :start-after: [START create_repository_client]
                :end-before: [END create_repository_client]
                :language: python
                :dedent: 8
                :caption: Instantiate an instance of `ContainerRepositoryClient`
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
        # type: (Dict[str, Any]) -> None
        """Delete a repository

        :returns: Object containing information about the deleted repository
        :rtype: :class:`~azure.containerregistry.DeleteRepositoryResult`
        :raises: :class:`~azure.core.exceptions.ResourceNotFoundError`

        Example

        .. code-block:: python

            from azure.containerregistry import ContainerRepositoryClient
            from azure.identity import DefaultAzureCredential

            account_url = os.environ["CONTAINERREGISTRY_ENDPOINT"]
            client = ContainerRepositoryClient(account_url, "my_repository", DefaultAzureCredential())
            client.delete()
        """
        return DeleteRepositoryResult._from_generated(  # pylint: disable=protected-access
            self._client.container_registry.delete_repository(self.repository, **kwargs)
        )

    @distributed_trace
    def delete_registry_artifact(self, digest, **kwargs):
        # type: (str, Dict[str, Any]) -> None
        """Delete a registry artifact

        :param digest: The digest of the artifact to be deleted
        :type digest: str
        :returns: None
        :raises: :class:`~azure.core.exceptions.ResourceNotFoundError`

        Example

        .. code-block:: python

            from azure.containerregistry import ContainerRepositoryClient
            from azure.identity import DefaultAzureCredential

            account_url = os.environ["CONTAINERREGISTRY_ENDPOINT"]
            client = ContainerRepositoryClient(account_url, "my_repository", DefaultAzureCredential())
            for artifact in client.list_registry_artifacts():
                client.delete_registry_artifact(artifact.digest)
        """
        self._client.container_registry.delete_manifest(self.repository, digest, **kwargs)

    @distributed_trace
    def delete_tag(self, tag, **kwargs):
        # type: (str, Dict[str, Any]) -> None
        """Delete a tag from a repository

        :param str tag: The tag to be deleted
        :returns: None
        :raises: :class:`~azure.core.exceptions.ResourceNotFoundError`

        Example

        .. code-block:: python

            from azure.containerregistry import ContainerRepositoryClient
            from azure.identity import DefaultAzureCredential

            account_url = os.environ["CONTAINERREGISTRY_ENDPOINT"]
            client = ContainerRepositoryClient(account_url, "my_repository", DefaultAzureCredential())
            for artifact in client.list_tags():
                client.delete_tag(tag.name)
        """
        self._client.container_registry.delete_tag(self.repository, tag, **kwargs)

    @distributed_trace
    def get_properties(self, **kwargs):
        # type: (Dict[str, Any]) -> RepositoryProperties
        """Get the properties of a repository

        :returns: :class:`~azure.containerregistry.RepositoryProperties`
        :raises: :class:`~azure.core.exceptions.ResourceNotFoundError`

        Example

        .. code-block:: python

            from azure.containerregistry import ContainerRepositoryClient
            from azure.identity import DefaultAzureCredential

            account_url = os.environ["CONTAINERREGISTRY_ENDPOINT"]
            client = ContainerRepositoryClient(account_url, "my_repository", DefaultAzureCredential())
            repository_properties = client.get_properties()
            print(repository_properties.name)
            print(repository_properties.content_permissions)
            print(repository_properties.created_on)
            print(repository_properties.last_updated_on)
            print(repository_properties.manifest_count)
            print(repository_properties.registry)
            print(repository_properties.tag_count)
        """
        return RepositoryProperties._from_generated(  # pylint: disable=protected-access
            self._client.container_registry.get_properties(self.repository, **kwargs)
        )

    @distributed_trace
    def get_registry_artifact_properties(self, tag_or_digest, **kwargs):
        # type: (str, Dict[str, Any]) -> ArtifactManifestProperties
        """Get the properties of a registry artifact

        :param tag_or_digest: The tag/digest of a registry artifact
        :type tag_or_digest: str
        :returns: :class:`~azure.containerregistry.ArtifactManifestProperties`
        :raises: :class:`~azure.core.exceptions.ResourceNotFoundError`

        Example

        .. code-block:: python

            from azure.containerregistry import ContainerRepositoryClient
            from azure.identity import DefaultAzureCredential

            account_url = os.environ["CONTAINERREGISTRY_ENDPOINT"]
            client = ContainerRepositoryClient(account_url, "my_repository", DefaultAzureCredential())
            for artifact in client.list_registry_artifacts():
                properties = client.get_registry_artifact_properties(artifact.digest)
        """
        if _is_tag(tag_or_digest):
            tag_or_digest = self._get_digest_from_tag(tag_or_digest)

        return ArtifactManifestProperties._from_generated(  # pylint: disable=protected-access
            self._client.container_registry.get_manifest_properties(self.repository, tag_or_digest, **kwargs),
            repository=self.repository
        )

    @distributed_trace
    def get_tag_properties(self, tag, **kwargs):
        # type: (str, Dict[str, Any]) -> ArtifactTagProperties
        """Get the properties for a tag

        :param tag: The tag to get properties for
        :type tag: str
        :returns: :class:`~azure.containerregistry.ArtifactTagProperties`
        :raises: :class:`~azure.core.exceptions.ResourceNotFoundError`

        Example

        .. code-block:: python

            from azure.containerregistry import ContainerRepositoryClient
            from azure.identity import DefaultAzureCredential

            account_url = os.environ["CONTAINERREGISTRY_ENDPOINT"]
            client = ContainerRepositoryClient(account_url, "my_repository", DefaultAzureCredential())
            for tag in client.list_tags():
                tag_properties = client.get_tag_properties(tag.name)
        """
        return ArtifactTagProperties._from_generated(  # pylint: disable=protected-access
            self._client.container_registry.get_tag_properties(self.repository, tag, **kwargs),
            repository=self.repository,
        )

    @distributed_trace
    def list_registry_artifacts(self, **kwargs):
        # type: (Dict[str, Any]) -> ItemPaged[ArtifactManifestProperties]
        """List the artifacts for a repository

        :keyword last: Query parameter for the last item in the previous call. Ensuing
            call will return values after last lexically
        :paramtype last: str
        :keyword order_by: Query parameter for ordering by time ascending or descending
        :paramtype order_by: :class:`~azure.containerregistry.ManifestOrderBy`
        :keyword results_per_page: Number of repositories to return per page
        :paramtype results_per_page: int
        :return: ItemPaged[:class:`ArtifactManifestProperties`]
        :rtype: :class:`~azure.core.paging.ItemPaged`
        :raises: :class:`~azure.core.exceptions.ResourceNotFoundError`

        Example

        .. code-block:: python

            from azure.containerregistry import ContainerRepositoryClient
            from azure.identity import DefaultAzureCredential

            account_url = os.environ["CONTAINERREGISTRY_ENDPOINT"]
            client = ContainerRepositoryClient(account_url, "my_repository", DefaultAzureCredential())
            for artifact in client.list_registry_artifacts():
                print(artifact.digest)
        """
        name = self.repository
        last = kwargs.pop("last", None)
        n = kwargs.pop("results_per_page", None)
        orderby = kwargs.pop("order_by", None)
        cls = kwargs.pop(
            "cls",
            lambda objs: [
                ArtifactManifestProperties._from_generated(x, repository=self.repository) for x in objs  # pylint: disable=protected-access
            ],
        )

        error_map = {401: ClientAuthenticationError, 404: ResourceNotFoundError, 409: ResourceExistsError}
        error_map.update(kwargs.pop("error_map", {}))
        accept = "application/json"

        def prepare_request(next_link=None):
            # Construct headers
            header_parameters = {}  # type: Dict[str, Any]
            header_parameters["Accept"] = self._client._serialize.header(  # pylint: disable=protected-access
                "accept", accept, "str"
            )

            if not next_link:
                # Construct URL
                url = "/acr/v1/{name}/_manifests"
                path_format_arguments = {
                    "url": self._client._serialize.url(  # pylint: disable=protected-access
                        "self._client._config.url",
                        self._client._config.url,  # pylint: disable=protected-access
                        "str",
                        skip_quote=True,
                    ),
                    "name": self._client._serialize.url("name", name, "str"),  # pylint: disable=protected-access
                }
                url = self._client._client.format_url(url, **path_format_arguments)  # pylint: disable=protected-access
                # Construct parameters
                query_parameters = {}  # type: Dict[str, Any]
                if last is not None:
                    query_parameters["last"] = self._client._serialize.query(  # pylint: disable=protected-access
                        "last", last, "str"
                    )
                if n is not None:
                    query_parameters["n"] = self._client._serialize.query(  # pylint: disable=protected-access
                        "n", n, "int"
                    )
                if orderby is not None:
                    query_parameters["orderby"] = self._client._serialize.query(  # pylint: disable=protected-access
                        "orderby", orderby, "str"
                    )

                request = self._client._client.get(  # pylint: disable=protected-access
                    url, query_parameters, header_parameters
                )
            else:
                url = next_link
                query_parameters = {}  # type: Dict[str, Any]
                path_format_arguments = {
                    "url": self._client._serialize.url(  # pylint: disable=protected-access
                        "self._client._config.url",
                        self._client._config.url,  # pylint: disable=protected-access
                        "str",
                        skip_quote=True,
                    ),
                    "name": self._client._serialize.url("name", name, "str"),  # pylint: disable=protected-access
                }
                url = self._client._client.format_url(url, **path_format_arguments)  # pylint: disable=protected-access
                request = self._client._client.get(  # pylint: disable=protected-access
                    url, query_parameters, header_parameters
                )
            return request

        def extract_data(pipeline_response):
            deserialized = self._client._deserialize(  # pylint: disable=protected-access
                "AcrManifests", pipeline_response
            )
            list_of_elem = deserialized.manifests
            if cls:
                list_of_elem = cls(list_of_elem)
            link = None
            if "Link" in pipeline_response.http_response.headers.keys():
                link = _parse_next_link(pipeline_response.http_response.headers["Link"])
            return link, iter(list_of_elem)

        def get_next(next_link=None):
            request = prepare_request(next_link)

            pipeline_response = self._client._client._pipeline.run(  # pylint: disable=protected-access
                request, stream=False, **kwargs
            )
            response = pipeline_response.http_response

            if response.status_code not in [200]:
                error = self._client._deserialize.failsafe_deserialize(  # pylint: disable=protected-access
                    AcrErrors, response
                )
                map_error(status_code=response.status_code, response=response, error_map=error_map)
                raise HttpResponseError(response=response, model=error)

            return pipeline_response

        return ItemPaged(get_next, extract_data)

    @distributed_trace
    def list_tags(self, **kwargs):
        # type: (Dict[str, Any]) -> ItemPaged[ArtifactTagProperties]
        """List the tags for a repository

        :keyword last: Query parameter for the last item in the previous call. Ensuing
            call will return values after last lexically
        :paramtype last: str
        :keyword order_by: Query parameter for ordering by time ascending or descending
        :paramtype order_by: :class:`~azure.containerregistry.TagOrderBy`
        :keyword results_per_page: Number of repositories to return per page
        :paramtype results_per_page: int
        :return: ItemPaged[:class:`~azure.containerregistry.ArtifactTagProperties`]
        :rtype: :class:`~azure.core.paging.ItemPaged`
        :raises: :class:`~azure.core.exceptions.ResourceNotFoundError`

        Example

        .. code-block:: python

            from azure.containerregistry import ContainerRepositoryClient
            from azure.identity import DefaultAzureCredential

            account_url = os.environ["CONTAINERREGISTRY_ENDPOINT"]
            client = ContainerRepositoryClient(account_url, "my_repository", DefaultAzureCredential())
            for tag in client.list_tags():
                tag_properties = client.get_tag_properties(tag.name)
        """
        name = self.repository
        last = kwargs.pop("last", None)
        n = kwargs.pop("results_per_page", None)
        orderby = kwargs.pop("order_by", None)
        digest = kwargs.pop("digest", None)
        cls = kwargs.pop(
            "cls",
            lambda objs: [
                ArtifactTagProperties._from_generated(o, repository=self.repository)  # pylint: disable=protected-access
                for o in objs
            ],
        )

        error_map = {401: ClientAuthenticationError, 404: ResourceNotFoundError, 409: ResourceExistsError}
        error_map.update(kwargs.pop("error_map", {}))
        accept = "application/json"

        def prepare_request(next_link=None):
            # Construct headers
            header_parameters = {}  # type: Dict[str, Any]
            header_parameters["Accept"] = self._client._serialize.header(  # pylint: disable=protected-access
                "accept", accept, "str"
            )

            if not next_link:
                # Construct URL
                url = "/acr/v1/{name}/_tags"
                path_format_arguments = {
                    "url": self._client._serialize.url(  # pylint: disable=protected-access
                        "self._config.url",
                        self._client._config.url,  # pylint: disable=protected-access
                        "str",
                        skip_quote=True,
                    ),
                    "name": self._client._serialize.url("name", name, "str"),  # pylint: disable=protected-access
                }
                url = self._client._client.format_url(url, **path_format_arguments)  # pylint: disable=protected-access
                # Construct parameters
                query_parameters = {}  # type: Dict[str, Any]
                if last is not None:
                    query_parameters["last"] = self._client._serialize.query(  # pylint: disable=protected-access
                        "last", last, "str"
                    )
                if n is not None:
                    query_parameters["n"] = self._client._serialize.query(  # pylint: disable=protected-access
                        "n", n, "int"
                    )
                if orderby is not None:
                    query_parameters["orderby"] = self._client._serialize.query(  # pylint: disable=protected-access
                        "orderby", orderby, "str"
                    )
                if digest is not None:
                    query_parameters["digest"] = self._client._serialize.query(  # pylint: disable=protected-access
                        "digest", digest, "str"
                    )

                request = self._client._client.get(  # pylint: disable=protected-access
                    url, query_parameters, header_parameters
                )
            else:
                url = next_link
                query_parameters = {}  # type: Dict[str, Any]
                path_format_arguments = {
                    "url": self._client._serialize.url(  # pylint: disable=protected-access
                        "self._client._config.url",
                        self._client._config.url,  # pylint: disable=protected-access
                        "str",
                        skip_quote=True,
                    ),
                    "name": self._client._serialize.url("name", name, "str"),  # pylint: disable=protected-access
                }
                url = self._client._client.format_url(url, **path_format_arguments)  # pylint: disable=protected-access
                request = self._client._client.get(  # pylint: disable=protected-access
                    url, query_parameters, header_parameters
                )
            return request

        def extract_data(pipeline_response):
            deserialized = self._client._deserialize("TagList", pipeline_response)  # pylint: disable=protected-access
            list_of_elem = deserialized.tag_attribute_bases
            if cls:
                list_of_elem = cls(list_of_elem)
            link = None
            if "Link" in pipeline_response.http_response.headers.keys():
                link = _parse_next_link(pipeline_response.http_response.headers["Link"])
            return link, iter(list_of_elem)

        def get_next(next_link=None):
            request = prepare_request(next_link)

            pipeline_response = self._client._client._pipeline.run(  # pylint: disable=protected-access
                request, stream=False, **kwargs
            )
            response = pipeline_response.http_response

            if response.status_code not in [200]:
                error = self._client._deserialize.failsafe_deserialize(  # pylint: disable=protected-access
                    AcrErrors, response
                )
                map_error(status_code=response.status_code, response=response, error_map=error_map)
                raise HttpResponseError(response=response, model=error)

            return pipeline_response

        return ItemPaged(get_next, extract_data)

    @distributed_trace
    def set_manifest_properties(self, digest, permissions, **kwargs):
        # type: (str, ContentProperties, Dict[str, Any]) -> ArtifactManifestProperties
        """Set the properties for a manifest

        :param digest: Digest of a manifest
        :type digest: str
        :param permissions: The property's values to be set
        :type permissions: ContentProperties
        :returns: :class:`~azure.containerregistry.ArtifactManifestProperties`
        :raises: :class:`~azure.core.exceptions.ResourceNotFoundError`

        Example

        .. code-block:: python

            from azure.containerregistry import ContainerRepositoryClient
            from azure.identity import DefaultAzureCredential

            account_url = os.environ["CONTAINERREGISTRY_ENDPOINT"]
            client = ContainerRepositoryClient(account_url, "my_repository", DefaultAzureCredential())
            for artifact in client.list_registry_artifacts():
                received_permissions = client.set_manifest_properties(
                    artifact.digest,
                    ContentPermissions(
                        can_delete=False,
                        can_list=False,
                        can_read=False,
                        can_write=False,
                    ),
                )
        """
        return ArtifactManifestProperties._from_generated(  # pylint: disable=protected-access
            self._client.container_registry.update_manifest_properties(
                self.repository, digest, value=permissions._to_generated(), **kwargs  # pylint: disable=protected-access
            ),
            repository=self.repository
        )

    @distributed_trace
    def set_tag_properties(self, tag, permissions, **kwargs):
        # type: (str, ContentProperties, Dict[str, Any]) -> ArtifactTagProperties
        """Set the properties for a tag

        :param tag: Tag to set properties for
        :type tag: str
        :param permissions: The property's values to be set
        :type permissions: ContentProperties
        :returns: :class:`~azure.containerregistry.ArtifactTagProperties`
        :raises: :class:`~azure.core.exceptions.ResourceNotFoundError`

        Example

        .. code-block:: python

            from azure.containerregistry import ContainerRepositoryClient
            from azure.identity import DefaultAzureCredential

            account_url = os.environ["CONTAINERREGISTRY_ENDPOINT"]
            client = ContainerRepositoryClient(account_url, "my_repository", DefaultAzureCredential())
            tag_identifier = "latest"
            received = client.set_tag_properties(
                tag_identifier,
                ContentPermissions(
                    can_delete=False,
                    can_list=False,
                    can_read=False,
                    can_write=False,
                ),
            )
        """
        return ArtifactTagProperties._from_generated(  # pylint: disable=protected-access
            self._client.container_registry.update_tag_attributes(
                self.repository, tag, value=permissions._to_generated(), **kwargs  # pylint: disable=protected-access
            ),
            repository=self.repository,
        )
