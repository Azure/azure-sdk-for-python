# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
from typing import Any, Dict, TYPE_CHECKING, Optional, overload, Union

from azure.core.async_paging import AsyncItemPaged, AsyncList
from azure.core.exceptions import (
    ClientAuthenticationError,
    ResourceExistsError,
    ResourceNotFoundError,
    HttpResponseError,
    map_error,
)
from azure.core.tracing.decorator import distributed_trace
from azure.core.tracing.decorator_async import distributed_trace_async

from ._async_base_client import ContainerRegistryBaseClient
from .._generated.models import AcrErrors
from .._helpers import _is_tag, _parse_next_link
from .._models import RepositoryProperties, ArtifactManifestProperties, ArtifactTagProperties

if TYPE_CHECKING:
    from azure.core.credentials_async import AsyncTokenCredential


class ContainerRegistryClient(ContainerRegistryBaseClient):
    def __init__(self, endpoint: str, credential: Optional["AsyncTokenCredential"] = None, **kwargs: Any) -> None:
        """Create a ContainerRegistryClient from an endpoint and a credential

        :param endpoint: An ACR endpoint
        :type endpoint: str
        :param credential: The credential with which to authenticate
        :type credential: :class:`~azure.core.credentials_async.AsyncTokenCredential`
        :keyword authentication_scope: URL for credential authentication if different from the default
        :paramtype authentication_scope: str
        :returns: None
        :raises: None

        .. admonition:: Example:

            .. literalinclude:: ../samples/async_samples/sample_create_client_async.py
                :start-after: [START create_registry_client]
                :end-before: [END create_registry_client]
                :language: python
                :dedent: 8
                :caption: Instantiate an instance of `ContainerRegistryClient`
        """
        if not endpoint.startswith("https://") and not endpoint.startswith("http://"):
            endpoint = "https://" + endpoint
        self._endpoint = endpoint
        self._credential = credential
        super(ContainerRegistryClient, self).__init__(endpoint=endpoint, credential=credential, **kwargs)

    async def _get_digest_from_tag(self, repository: str, tag: str) -> str:
        tag_props = await self.get_tag_properties(repository, tag)
        return tag_props.digest

    @distributed_trace_async
    async def delete_repository(self, repository: str, **kwargs: Any) -> None:
        """Delete a repository. If the repository cannot be found or a response status code of
        404 is returned an error will not be raised.

        :param str repository: The repository to delete
        :returns: None
        :rtype: None
        :raises: :class:`~azure.core.exceptions.HttpResponseError`

        .. admonition:: Example:

            .. literalinclude:: ../samples/async_samples/sample_create_client_async.py
                :start-after: [START delete_repository]
                :end-before: [END delete_repository]
                :language: python
                :dedent: 8
                :caption: Delete a repository from the `ContainerRegistryClient`
        """
        await self._client.container_registry.delete_repository(repository, **kwargs)

    @distributed_trace
    def list_repository_names(self, **kwargs: Any) -> AsyncItemPaged[str]:
        """List all repositories

        :keyword results_per_page: Number of repositories to return per page
        :paramtype results_per_page: int
        :returns: An iterable of strings
        :rtype: ~azure.core.async_paging.AsyncItemPaged[str]
        :raises: :class:`~azure.core.exceptions.HttpResponseError`

        .. admonition:: Example:

            .. literalinclude:: ../samples/async_samples/sample_delete_old_tags_async.py
                :start-after: [START list_repository_names]
                :end-before: [END list_repository_names]
                :language: python
                :dedent: 8
                :caption: List repositories in a container registry account
        """
        n = kwargs.pop("results_per_page", None)
        last = kwargs.pop("last", None)

        cls = kwargs.pop("cls", None)
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
                url = "/acr/v1/_catalog"
                path_format_arguments = {
                    "url": self._client._serialize.url(  # pylint: disable=protected-access
                        "self._config.url",
                        self._client._config.url,  # pylint: disable=protected-access
                        "str",
                        skip_quote=True,
                    ),
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

                request = self._client._client.get(  # pylint: disable=protected-access
                    url, query_parameters, header_parameters
                )
            else:
                url = next_link
                query_parameters = {}  # type: Dict[str, Any]
                path_format_arguments = {
                    "url": self._client._serialize.url(  # pylint: disable=protected-access
                        "self._config.url",
                        self._client._config.url,  # pylint: disable=protected-access
                        "str",
                        skip_quote=True,
                    ),
                }
                url = self._client._client.format_url(url, **path_format_arguments)  # pylint: disable=protected-access
                request = self._client._client.get(  # pylint: disable=protected-access
                    url, query_parameters, header_parameters
                )
            return request

        async def extract_data(pipeline_response):
            deserialized = self._client._deserialize(  # pylint: disable=protected-access
                "Repositories", pipeline_response
            )
            list_of_elem = deserialized.repositories or []
            if cls:
                list_of_elem = cls(list_of_elem)
            link = None
            if "Link" in pipeline_response.http_response.headers.keys():
                link = _parse_next_link(pipeline_response.http_response.headers["Link"])
            return link, AsyncList(list_of_elem)

        async def get_next(next_link=None):
            request = prepare_request(next_link)

            pipeline_response = await self._client._client._pipeline.run(  # pylint: disable=protected-access
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

        return AsyncItemPaged(get_next, extract_data)

    @distributed_trace_async
    async def get_repository_properties(self, repository: str, **kwargs: Any) -> RepositoryProperties:
        """Get the properties of a repository

        :param str repository: Name of the repository
        :returns: :class:`~azure.containerregistry.RepositoryProperties`
        :raises: :class:`~azure.core.exceptions.ResourceNotFoundError`
        """
        return RepositoryProperties._from_generated(  # pylint: disable=protected-access
            await self._client.container_registry.get_properties(repository, **kwargs)
        )

    @distributed_trace
    def list_manifest_properties(self, repository: str, **kwargs: Any) -> AsyncItemPaged[ArtifactManifestProperties]:
        """List the manifests of a repository

        :param str repository: Name of the repository
        :keyword order_by: Query parameter for ordering by time ascending or descending
        :paramtype order_by: :class:`~azure.containerregistry.ManifestOrder` or str
        :keyword results_per_page: Number of repositories to return per page
        :paramtype results_per_page: int
        :returns: An iterable of :class:`~azure.containerregistry.ArtifactManifestProperties`
        :rtype: ~azure.core.async_paging.AsyncItemPaged[~azure.containerregistry.ArtifactManifestProperties]
        :raises: :class:`~azure.core.exceptions.HttpResponseError`
        """
        name = repository
        last = kwargs.pop("last", None)
        n = kwargs.pop("results_per_page", None)
        orderby = kwargs.pop("order_by", None)
        cls = kwargs.pop(
            "cls",
            lambda objs: [
                ArtifactManifestProperties._from_generated(  # pylint: disable=protected-access
                    x, repository_name=repository, registry=self._endpoint
                )
                for x in objs
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

        async def extract_data(pipeline_response):
            deserialized = self._client._deserialize(  # pylint: disable=protected-access
                "AcrManifests", pipeline_response
            )
            list_of_elem = deserialized.manifests
            if cls:
                list_of_elem = cls(list_of_elem)
            link = None
            if "Link" in pipeline_response.http_response.headers.keys():
                link = _parse_next_link(pipeline_response.http_response.headers["Link"])
            return link, AsyncList(list_of_elem)

        async def get_next(next_link=None):
            request = prepare_request(next_link)

            pipeline_response = await self._client._client._pipeline.run(  # pylint: disable=protected-access
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

        return AsyncItemPaged(get_next, extract_data)

    @distributed_trace_async
    async def delete_manifest(self, repository: str, tag_or_digest: str, **kwargs: Any) -> None:
        """Delete a manifest. If the manifest cannot be found or a response status code of
        404 is returned an error will not be raised.

        :param str repository: Repository the manifest belongs to
        :param str tag_or_digest: Tag or digest of the manifest to be deleted.
        :returns: None
        :rtype: None
        :raises: :class:`~azure.core.exceptions.HttpResponseError`

        Example

        .. code-block:: python

            from azure.containerregistry.aio import ContainerRepositoryClient
            from azure.identity.aio import DefaultAzureCredential
            account_url = os.environ["CONTAINERREGISTRY_ENDPOINT"]
            client = ContainerRepositoryClient(account_url, DefaultAzureCredential())
            await client.delete_manifest("my_repository", "my_tag_or_digest")
        """
        if _is_tag(tag_or_digest):
            tag_or_digest = await self._get_digest_from_tag(repository, tag_or_digest)

        await self._client.container_registry.delete_manifest(repository, tag_or_digest, **kwargs)

    @distributed_trace_async
    async def delete_tag(self, repository: str, tag: str, **kwargs: Any) -> None:
        """Delete a tag from a repository. If the tag cannot be found or a response status code of
        404 is returned an error will not be raised.

        :param str repository: Repository the tag belongs to
        :param str tag: The tag to be deleted
        :returns: None
        :rtype: None
        :raises: :class:`~azure.core.exceptions.HttpResponseError`

        Example

        .. code-block:: python

            from azure.containerregistry.aio import ContainerRepositoryClient
            from azure.identity.aio import DefaultAzureCredential
            account_url = os.environ["CONTAINERREGISTRY_ENDPOINT"]
            client = ContainerRepositoryClient(account_url, "my_repository", DefaultAzureCredential())
            async for artifact in client.list_tag_properties():
                await client.delete_tag("my_repository", tag.name)
        """
        await self._client.container_registry.delete_tag(repository, tag, **kwargs)

    @distributed_trace_async
    async def get_manifest_properties(
        self, repository: str, tag_or_digest: str, **kwargs: Any
    ) -> ArtifactManifestProperties:
        """Get the properties of a registry artifact

        :param str repository: Name of the repository
        :param str tag_or_digest: The tag or digest of the manifest
        :returns: :class:`~azure.containerregistry.ArtifactManifestProperties`
        :raises: :class:`~azure.core.exceptions.ResourceNotFoundError`

        Example

        .. code-block:: python

            from azure.containerregistry.aio import ContainerRepositoryClient
            from azure.identity.aio import DefaultAzureCredential
            account_url = os.environ["CONTAINERREGISTRY_ENDPOINT"]
            client = ContainerRepositoryClient(account_url, "my_repository", DefaultAzureCredential())
            async for artifact in client.list_manifest_properties():
                properties = await client.get_manifest_properties("my_repository", artifact.digest)
        """
        if _is_tag(tag_or_digest):
            tag_or_digest = await self._get_digest_from_tag(repository, tag_or_digest)

        return ArtifactManifestProperties._from_generated(  # pylint: disable=protected-access
            await self._client.container_registry.get_manifest_properties(repository, tag_or_digest, **kwargs),
            repository_name=repository,
            registry=self._endpoint,
        )

    @distributed_trace_async
    async def get_tag_properties(self, repository: str, tag: str, **kwargs: Any) -> ArtifactTagProperties:
        """Get the properties for a tag

        :param str repository: Repository the tag belongs to
        :param tag: The tag to get properties for
        :type tag: str
        :returns: :class:`~azure.containerregistry.ArtifactTagProperties`
        :raises: :class:`~azure.core.exceptions.ResourceNotFoundError`

        Example

        .. code-block:: python

            from azure.containerregistry.aio import ContainerRepositoryClient
            from azure.identity.aio import DefaultAzureCredential
            account_url = os.environ["CONTAINERREGISTRY_ENDPOINT"]
            client = ContainerRepositoryClient(account_url, "my_repository", DefaultAzureCredential())
            async for tag in client.list_tag_properties():
                tag_properties = await client.get_tag_properties("my_repository", tag.name)
        """
        return ArtifactTagProperties._from_generated(  # pylint: disable=protected-access
            await self._client.container_registry.get_tag_properties(repository, tag, **kwargs),
            repository=repository,
        )

    @distributed_trace
    def list_tag_properties(self, repository: str, **kwargs: Any) -> AsyncItemPaged[ArtifactTagProperties]:
        """List the tags for a repository

        :param str repository: Name of the repository
        :keyword order_by: Query parameter for ordering by time ascending or descending
        :paramtype order_by: :class:`~azure.containerregistry.TagOrder` or str
        :keyword results_per_page: Number of repositories to return per page
        :paramtype results_per_page: int
        :returns: An iterable of :class:`~azure.containerregistry.ArtifactTagProperties`
        :rtype: ~azure.core.async_paging.AsyncItemPaged[~azure.containerregistry.ArtifactTagProperties]
        :raises: :class:`~azure.core.exceptions.ResourceNotFoundError`

        Example

        .. code-block:: python

            from azure.containerregistry.aio import ContainerRepositoryClient
            from azure.identity.aio import DefaultAzureCredential
            account_url = os.environ["CONTAINERREGISTRY_ENDPOINT"]
            client = ContainerRepositoryClient(account_url, "my_repository", DefaultAzureCredential())
            async for tag in client.list_tag_properties():
                tag_properties = await client.get_tag_properties(tag.name)
        """
        name = repository
        last = kwargs.pop("last", None)
        n = kwargs.pop("results_per_page", None)
        orderby = kwargs.pop("order_by", None)
        digest = kwargs.pop("digest", None)
        cls = kwargs.pop(
            "cls",
            lambda objs: [
                ArtifactTagProperties._from_generated(o, repository=repository)  # pylint: disable=protected-access
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

        async def extract_data(pipeline_response):
            deserialized = self._client._deserialize("TagList", pipeline_response)  # pylint: disable=protected-access
            list_of_elem = deserialized.tag_attribute_bases
            if cls:
                list_of_elem = cls(list_of_elem)
            link = None
            if "Link" in pipeline_response.http_response.headers.keys():
                link = _parse_next_link(pipeline_response.http_response.headers["Link"])
            return link, AsyncList(list_of_elem)

        async def get_next(next_link=None):
            request = prepare_request(next_link)

            pipeline_response = await self._client._client._pipeline.run(  # pylint: disable=protected-access
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

        return AsyncItemPaged(get_next, extract_data)

    @overload
    def update_repository_properties(
        self, repository: str, properties: RepositoryProperties, **kwargs: Any
    ) -> RepositoryProperties:
        ...

    @overload
    def update_repository_properties(self, repository: str, **kwargs: Any) -> RepositoryProperties:
        ...

    @distributed_trace_async
    async def update_repository_properties(
        self, *args: Union[str, RepositoryProperties], **kwargs: Any
    ) -> RepositoryProperties:
        """Set the properties of a repository

        :param args:
        :type args: Union[str, ~azure.containerregistry.RepositoryProperties]
        :param str repository: Name of the repository
        :param properties: Properties to set for the repository
        :type properties: :class:`~azure.containerregistry.RepositoryProperties`
        :returns: :class:`~azure.containerregistry.RepositoryProperties`
        :raises: :class:`~azure.core.exceptions.ResourceNotFoundError`
        """
        repository, properties = None, None
        if len(args) == 2:
            repository = args[0]
            properties = args[1]
        else:
            repository = args[0]
            properties = RepositoryProperties()

        properties.can_delete = kwargs.pop("can_delete", properties.can_delete)
        properties.can_list = kwargs.pop("can_list", properties.can_list)
        properties.can_read = kwargs.pop("can_read", properties.can_read)
        properties.can_write = kwargs.pop("can_write", properties.can_write)
        properties.teleport_enabled = kwargs.pop("teleport_enabled", None)

        return RepositoryProperties._from_generated(  # pylint: disable=protected-access
            await self._client.container_registry.set_properties(
                repository, properties._to_generated(), **kwargs  # pylint: disable=protected-access
            )
        )

    @overload
    def update_manifest_properties(
        self, repository: str, tag_or_digest: str, properties: ArtifactManifestProperties, **kwargs: Any
    ) -> ArtifactManifestProperties:
        ...

    @overload
    def update_manifest_properties(
        self, repository: str, tag_or_digest: str, **kwargs: Any
    ) -> ArtifactManifestProperties:
        ...

    @distributed_trace_async
    async def update_manifest_properties(
        self, *args: Union[str, ArtifactManifestProperties], **kwargs: Any
    ) -> ArtifactManifestProperties:
        """Set the properties for a manifest

        :param args:
        :type args: Union[str, ~azure.containerregistry.ArtifactManifestProperties]
        :param str repository: Name of the repository
        :param str tag_or_digest: Tag or digest of the manifest
        :param properties: The property's values to be set
        :type properties: ArtifactManifestProperties
        :returns: :class:`~azure.containerregistry.ArtifactManifestProperties`
        :raises: :class:`~azure.core.exceptions.ResourceNotFoundError`

        Example

        .. code-block:: python

            from azure.containerregistry.aio import ContainerRepositoryClient
            from azure.identity.aio import DefaultAzureCredential
            account_url = os.environ["CONTAINERREGISTRY_ENDPOINT"]
            client = ContainerRepositoryClient(account_url, "my_repository", DefaultAzureCredential())
            async for artifact in client.list_manifest_properties():
                received_properties = await client.update_manifest_properties(
                    "my_repository",
                    artifact.digest,
                    can_delete=False,
                    can_list=False,
                    can_read=False,
                    can_write=False,
                )
        """
        repository = args[0]
        tag_or_digest = args[1]
        properties = None
        if len(args) == 3:
            properties = args[2]
        else:
            properties = ArtifactManifestProperties()

        properties.can_delete = kwargs.pop("can_delete", properties.can_delete)
        properties.can_list = kwargs.pop("can_list", properties.can_list)
        properties.can_read = kwargs.pop("can_read", properties.can_read)
        properties.can_write = kwargs.pop("can_write", properties.can_write)

        if _is_tag(tag_or_digest):
            tag_or_digest = await self._get_digest_from_tag(repository, tag_or_digest)

        return ArtifactManifestProperties._from_generated(  # pylint: disable=protected-access
            await self._client.container_registry.update_manifest_properties(
                repository,
                tag_or_digest,
                value=properties._to_generated(),  # pylint: disable=protected-access
                **kwargs
            ),
            repository_name=repository,
            registry=self._endpoint,
        )

    @overload
    def update_tag_properties(
        self, repository: str, tag: str, properties: ArtifactTagProperties, **kwargs: Any
    ) -> ArtifactTagProperties:
        ...

    @overload
    def update_tag_properties(self, repository: str, tag: str, **kwargs: Any) -> ArtifactTagProperties:
        ...

    @distributed_trace_async
    async def update_tag_properties(
        self, *args: Union[str, ArtifactTagProperties], **kwargs: Any
    ) -> ArtifactTagProperties:
        """Set the properties for a tag

        :param args:
        :type args: Union[str, ~azure.containerregistry.ArtifactTagProperties]
        :param str repository: Repository the tag belongs to
        :param str tag: Tag to set properties for
        :param properties: The property's values to be set
        :type properties: ArtifactTagProperties
        :returns: :class:`~azure.containerregistry.ArtifactTagProperties`
        :raises: :class:`~azure.core.exceptions.ResourceNotFoundError`

        Example

        .. code-block:: python

            from azure.containerregistry.aio import ContainerRepositoryClient
            from azure.identity.aio import DefaultAzureCredential
            account_url = os.environ["CONTAINERREGISTRY_ENDPOINT"]
            client = ContainerRepositoryClient(account_url, "my_repository", DefaultAzureCredential())
            tag_identifier = "latest"
            received = await client.update_tag_properties(
                "my_repository",
                tag_identifier,
                can_delete=False,
                can_list=False,
                can_read=False,
                can_write=False
            )
        """
        repository = args[0]
        tag = args[1]
        properties = None
        if len(args) == 3:
            properties = args[2]
        else:
            properties = ArtifactTagProperties()

        properties.can_delete = kwargs.pop("can_delete", properties.can_delete)
        properties.can_list = kwargs.pop("can_list", properties.can_list)
        properties.can_read = kwargs.pop("can_read", properties.can_read)
        properties.can_write = kwargs.pop("can_write", properties.can_write)

        return ArtifactTagProperties._from_generated(  # pylint: disable=protected-access
            await self._client.container_registry.update_tag_attributes(
                repository, tag, value=properties._to_generated(), **kwargs  # pylint: disable=protected-access
            ),
            repository=repository,
        )
