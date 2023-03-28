# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
# pylint: disable=too-many-lines
from io import BytesIO
from typing import Any, Dict, IO, Optional, overload, Union, cast, Tuple
from azure.core.credentials import TokenCredential
from azure.core.exceptions import (
    ClientAuthenticationError,
    ResourceNotFoundError,
    ResourceExistsError,
    HttpResponseError,
    map_error,
)
from azure.core.paging import ItemPaged
from azure.core.pipeline import PipelineResponse
from azure.core.tracing.decorator import distributed_trace

from ._base_client import ContainerRegistryBaseClient
from ._generated.models import AcrErrors, OCIManifest, ManifestWrapper
from ._helpers import (
    _compute_digest,
    _is_tag,
    _parse_next_link,
    _serialize_manifest,
    _validate_digest,
    OCI_MANIFEST_MEDIA_TYPE,
    SUPPORTED_API_VERSIONS,
    AZURE_RESOURCE_MANAGER_PUBLIC_CLOUD,
)
from ._models import (
    RepositoryProperties,
    ArtifactTagProperties,
    ArtifactManifestProperties,
    DownloadBlobResult,
    DownloadManifestResult,
)

def _return_response_and_deserialized(pipeline_response, deserialized, _):
    return pipeline_response, deserialized

def _return_response_headers(_, __, response_headers):
    return response_headers


class ContainerRegistryClient(ContainerRegistryBaseClient):
    def __init__(
        self,
        endpoint: str,
        credential: Optional[TokenCredential] = None,
        *,
        api_version: Optional[str] = None,
        audience: str = AZURE_RESOURCE_MANAGER_PUBLIC_CLOUD,
        **kwargs
    ) -> None:
        """Create a ContainerRegistryClient from an ACR endpoint and a credential.

        :param str endpoint: An ACR endpoint.
        :param credential: The credential with which to authenticate. This should be None in anonymous access.
        :type credential: ~azure.core.credentials.TokenCredential or None
        :keyword api_version: API Version. The default value is "2021-07-01". Note that overriding this default value
         may result in unsupported behavior.
        :paramtype api_version: str
        :keyword audience: URL to use for credential authentication with AAD. Its value could be
            "https://management.azure.com", "https://management.chinacloudapi.cn" or
            "https://management.usgovcloudapi.net". The default value is "https://management.azure.com".
        :paramtype audience: str
        :returns: None
        :rtype: None
        :raises ValueError: If the provided api_version keyword-only argument isn't supported.

        .. admonition:: Example:

            .. literalinclude:: ../samples/sample_hello_world.py
                :start-after: [START create_registry_client]
                :end-before: [END create_registry_client]
                :language: python
                :dedent: 8
                :caption: Instantiate an instance of `ContainerRegistryClient`
        """
        if api_version and api_version not in SUPPORTED_API_VERSIONS:
            supported_versions = "\n".join(SUPPORTED_API_VERSIONS)
            raise ValueError(
                f"Unsupported API version '{api_version}'. Please select from:\n{supported_versions}"
            )
        if api_version is not None:
            kwargs["api_version"] = api_version
        defaultScope = [audience + "/.default"]
        if not endpoint.startswith("https://") and not endpoint.startswith("http://"):
            endpoint = "https://" + endpoint
        self._endpoint = endpoint
        self._credential = credential
        super(ContainerRegistryClient, self).__init__(
            endpoint=endpoint, credential=credential, credential_scopes=defaultScope, **kwargs)

    def _get_digest_from_tag(self, repository: str, tag: str) -> str:
        tag_props = self.get_tag_properties(repository, tag)
        return tag_props.digest

    @distributed_trace
    def delete_repository(self, repository: str, **kwargs) -> None:
        """Delete a repository. If the repository cannot be found or a response status code of
        404 is returned an error will not be raised.

        :param str repository: The repository to delete
        :returns: None
        :rtype: None
        :raises: ~azure.core.exceptions.HttpResponseError

        .. admonition:: Example:

            .. literalinclude:: ../samples/sample_hello_world.py
                :start-after: [START delete_repository]
                :end-before: [END delete_repository]
                :language: python
                :dedent: 8
                :caption: Delete a repository from the `ContainerRegistryClient`
        """
        self._client.container_registry.delete_repository(repository, **kwargs)

    @distributed_trace
    def list_repository_names(self, **kwargs) -> ItemPaged[str]:
        """List all repositories

        :keyword results_per_page: Number of repositories to return per page
        :paramtype results_per_page: int
        :returns: An iterable of strings
        :rtype: ~azure.core.paging.ItemPaged[str]
        :raises: ~azure.core.exceptions.HttpResponseError

        .. admonition:: Example:

            .. literalinclude:: ../samples/sample_delete_tags.py
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

        def extract_data(pipeline_response):
            deserialized = self._client._deserialize(  # pylint: disable=protected-access
                "Repositories", pipeline_response
            )
            list_of_elem = deserialized.repositories or []
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
    def get_repository_properties(self, repository: str, **kwargs) -> RepositoryProperties:
        """Get the properties of a repository

        :param str repository: Name of the repository
        :rtype: ~azure.containerregistry.RepositoryProperties
        :raises: ~azure.core.exceptions.ResourceNotFoundError
        """
        return RepositoryProperties._from_generated(  # pylint: disable=protected-access
            self._client.container_registry.get_properties(repository, **kwargs)
        )

    @distributed_trace
    def list_manifest_properties(self, repository: str, **kwargs) -> ItemPaged[ArtifactManifestProperties]:
        """List the artifacts for a repository

        :param str repository: Name of the repository
        :keyword order_by: Query parameter for ordering by time ascending or descending
        :paramtype order_by: ~azure.containerregistry.ArtifactManifestOrder or str
        :keyword results_per_page: Number of repositories to return per page
        :paramtype results_per_page: int
        :returns: An iterable of :class:`~azure.containerregistry.ArtifactManifestProperties`
        :rtype: ~azure.core.paging.ItemPaged[~azure.containerregistry.ArtifactManifestProperties]
        :raises: ~azure.core.exceptions.ResourceNotFoundError
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

        def extract_data(pipeline_response):
            deserialized = self._client._deserialize(  # pylint: disable=protected-access
                "AcrManifests", pipeline_response
            )
            list_of_elem = deserialized.manifests or []
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
    def delete_tag(self, repository: str, tag: str, **kwargs) -> None:
        """Delete a tag from a repository. If the tag cannot be found or a response status code of
        404 is returned an error will not be raised.

        :param str repository: Name of the repository the tag belongs to
        :param str tag: The tag to be deleted
        :returns: None
        :rtype: None
        :raises: ~azure.core.exceptions.HttpResponseError

        Example

        .. code-block:: python

            from azure.containerregistry import ContainerRegistryClient
            from azure.identity import DefaultAzureCredential
            endpoint = os.environ["CONTAINERREGISTRY_ENDPOINT"]
            client = ContainerRegistryClient(endpoint, DefaultAzureCredential(), audience="my_audience")
            for tag in client.list_tag_properties("my_repository"):
                client.delete_tag("my_repository", tag.name)
        """
        self._client.container_registry.delete_tag(repository, tag, **kwargs)

    @distributed_trace
    def get_manifest_properties(self, repository: str, tag_or_digest: str, **kwargs) -> ArtifactManifestProperties:
        """Get the properties of a registry artifact

        :param str repository: Name of the repository
        :param str tag_or_digest: Tag or digest of the manifest
        :rtype: ~azure.containerregistry.ArtifactManifestProperties
        :raises: ~azure.core.exceptions.ResourceNotFoundError

        Example

        .. code-block:: python

            from azure.containerregistry import ContainerRegistryClient
            from azure.identity import DefaultAzureCredential
            endpoint = os.environ["CONTAINERREGISTRY_ENDPOINT"]
            client = ContainerRegistryClient(endpoint, DefaultAzureCredential(), audience="my_audience")
            for artifact in client.list_manifest_properties("my_repository"):
                properties = client.get_manifest_properties("my_repository", artifact.digest)
        """
        if _is_tag(tag_or_digest):
            tag_or_digest = self._get_digest_from_tag(repository, tag_or_digest)

        manifest_properties = self._client.container_registry.get_manifest_properties(
            repository, tag_or_digest, **kwargs
        )
        return ArtifactManifestProperties._from_generated(  # pylint: disable=protected-access
            manifest_properties.manifest, # type: ignore
            repository_name=repository,
            registry=self._endpoint,
        )

    @distributed_trace
    def get_tag_properties(self, repository: str, tag: str, **kwargs) -> ArtifactTagProperties:
        """Get the properties for a tag

        :param str repository: Name of the repository
        :param str tag: The tag to get tag properties for
        :rtype: ~azure.containerregistry.ArtifactTagProperties
        :raises: ~azure.core.exceptions.ResourceNotFoundError

        Example

        .. code-block:: python

            from azure.containerregistry import ContainerRegistryClient
            from azure.identity import DefaultAzureCredential
            endpoint = os.environ["CONTAINERREGISTRY_ENDPOINT"]
            client = ContainerRegistryClient(endpoint, DefaultAzureCredential(), audience="my_audience")
            for tag in client.list_tag_properties("my_repository"):
                tag_properties = client.get_tag_properties("my_repository", tag.name)
        """
        tag_properties = self._client.container_registry.get_tag_properties(repository, tag, **kwargs)
        return ArtifactTagProperties._from_generated(  # pylint: disable=protected-access
            tag_properties.tag, # type: ignore
            repository=repository,
        )

    @distributed_trace
    def list_tag_properties(self, repository: str, **kwargs) -> ItemPaged[ArtifactTagProperties]:
        """List the tags for a repository

        :param str repository: Name of the repository
        :keyword order_by: Query parameter for ordering by time ascending or descending
        :paramtype order_by: ~azure.containerregistry.ArtifactTagOrder or str
        :keyword results_per_page: Number of repositories to return per page
        :paramtype results_per_page: int
        :returns: An iterable of :class:`~azure.containerregistry.ArtifactTagProperties`
        :rtype: ~azure.core.paging.ItemPaged[~azure.containerregistry.ArtifactTagProperties]
        :raises: ~azure.core.exceptions.ResourceNotFoundError

        Example

        .. code-block:: python

            from azure.containerregistry import ContainerRegistryClient
            from azure.identity import DefaultAzureCredential
            endpoint = os.environ["CONTAINERREGISTRY_ENDPOINT"]
            client = ContainerRegistryClient(endpoint, DefaultAzureCredential(), audience="my_audience")
            for tag in client.list_tag_properties("my_repository"):
                tag_properties = client.get_tag_properties("my_repository", tag.name)
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
            list_of_elem = deserialized.tag_attribute_bases or []
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

    @overload
    def update_manifest_properties(
        self,
        repository: str,
        tag_or_digest: str,
        properties: ArtifactManifestProperties,
        **kwargs
    ) -> ArtifactManifestProperties:
        """Set the permission properties for a manifest.

        The updatable properties include: `can_delete`, `can_list`, `can_read`, and `can_write`.

        :param str repository: Repository the manifest belongs to.
        :param str tag_or_digest: Tag or digest of the manifest.
        :param properties: The property's values to be set. This is a positional-only
            parameter. Please provide either this or individual keyword parameters.
        :type properties: ~azure.containerregistry.ArtifactManifestProperties
        :rtype: ~azure.containerregistry.ArtifactManifestProperties
        :raises: ~azure.core.exceptions.ResourceNotFoundError

        Example

        .. code-block:: python

            from azure.containerregistry import ArtifactManifestProperties, ContainerRegistryClient
            from azure.identity import DefaultAzureCredential
            endpoint = os.environ["CONTAINERREGISTRY_ENDPOINT"]
            client = ContainerRegistryClient(endpoint, DefaultAzureCredential(), audience="my_audience")
            manifest_properties = ArtifactManifestProperties(
                can_delete=False, can_list=False, can_read=False, can_write=False
            )
            for artifact in client.list_manifest_properties("my_repository"):
                received_properties = client.update_manifest_properties(
                    "my_repository",
                    artifact.digest,
                    manifest_properties,
                )
        """

    @overload
    def update_manifest_properties(
        self,
        repository: str,
        tag_or_digest: str,
        *,
        can_delete: Optional[bool] = None,
        can_list: Optional[bool] = None,
        can_read: Optional[bool] = None,
        can_write: Optional[bool] = None,
        **kwargs
    ) -> ArtifactManifestProperties:
        """Set the permission properties for a manifest.

        The updatable properties include: `can_delete`, `can_list`, `can_read`, and `can_write`.

        :param str repository: Repository the manifest belongs to.
        :param str tag_or_digest: Tag or digest of the manifest.
        :keyword bool can_delete: Delete permissions for a manifest.
        :keyword bool can_list: List permissions for a manifest.
        :keyword bool can_read: Read permissions for a manifest.
        :keyword bool can_write: Write permissions for a manifest.
        :rtype: ~azure.containerregistry.ArtifactManifestProperties
        :raises: ~azure.core.exceptions.ResourceNotFoundError

        Example

        .. code-block:: python

            from azure.containerregistry import ContainerRegistryClient
            from azure.identity import DefaultAzureCredential
            endpoint = os.environ["CONTAINERREGISTRY_ENDPOINT"]
            client = ContainerRegistryClient(endpoint, DefaultAzureCredential(), audience="my_audience")
            for artifact in client.list_manifest_properties("my_repository"):
                received_properties = client.update_manifest_properties(
                    "my_repository",
                    artifact.digest,
                    can_delete=False,
                    can_list=False,
                    can_read=False,
                    can_write=False,
                )
        """

    @distributed_trace
    def update_manifest_properties(
        self, *args: Union[str, ArtifactManifestProperties], **kwargs
    ) -> ArtifactManifestProperties:
        repository = str(args[0])
        tag_or_digest = str(args[1])
        properties = None
        if len(args) == 3:
            properties = cast(ArtifactManifestProperties, args[2])
        else:
            properties = ArtifactManifestProperties()

        properties.can_delete = kwargs.pop("can_delete", properties.can_delete)
        properties.can_list = kwargs.pop("can_list", properties.can_list)
        properties.can_read = kwargs.pop("can_read", properties.can_read)
        properties.can_write = kwargs.pop("can_write", properties.can_write)

        if _is_tag(tag_or_digest):
            tag_or_digest = self._get_digest_from_tag(repository, tag_or_digest)

        manifest_properties = self._client.container_registry.update_manifest_properties(
            repository,
            tag_or_digest,
            value=properties._to_generated(),  # pylint: disable=protected-access
            **kwargs
        )
        return ArtifactManifestProperties._from_generated(  # pylint: disable=protected-access
            manifest_properties.manifest, # type: ignore
            repository_name=repository,
            registry=self._endpoint
        )

    @overload
    def update_tag_properties(
        self,
        repository: str,
        tag: str,
        properties: ArtifactTagProperties,
        **kwargs
    ) -> ArtifactTagProperties:
        """Set the permission properties for a tag.

        The updatable properties include: `can_delete`, `can_list`, `can_read`, and `can_write`.

        :param str repository: Repository the tag belongs to.
        :param str tag: Tag to set properties for.
        :param properties: The property's values to be set. This is a positional-only
            parameter. Please provide either this or individual keyword parameters.
        :type properties: ~azure.containerregistry.ArtifactTagProperties
        :rtype: ~azure.containerregistry.ArtifactTagProperties
        :raises: ~azure.core.exceptions.ResourceNotFoundError

        Example

        .. code-block:: python

            from azure.containerregistry import ArtifactTagProperties, ContainerRegistryClient
            from azure.identity import DefaultAzureCredential
            endpoint = os.environ["CONTAINERREGISTRY_ENDPOINT"]
            client = ContainerRegistryClient(endpoint, DefaultAzureCredential(), audience="my_audience")
            tag_properties = ArtifactTagProperties(can_delete=False, can_list=False, can_read=False, can_write=False)
            received = client.update_tag_properties(
                "my_repository",
                "latest",
                tag_properties,
            )
        """

    @overload
    def update_tag_properties(
        self,
        repository: str,
        tag: str,
        *,
        can_delete: Optional[bool] = None,
        can_list: Optional[bool] = None,
        can_read: Optional[bool] = None,
        can_write: Optional[bool] = None,
        **kwargs
    ) -> ArtifactTagProperties:
        """Set the permission properties for a tag.

        The updatable properties include: `can_delete`, `can_list`, `can_read`, and `can_write`.

        :param str repository: Repository the tag belongs to.
        :param str tag: Tag to set properties for.
        :keyword bool can_delete: Delete permissions for a tag.
        :keyword bool can_list: List permissions for a tag.
        :keyword bool can_read: Read permissions for a tag.
        :keyword bool can_write: Write permissions for a tag.
        :rtype: ~azure.containerregistry.ArtifactTagProperties
        :raises: ~azure.core.exceptions.ResourceNotFoundError

        Example

        .. code-block:: python

            from azure.containerregistry import ContainerRegistryClient
            from azure.identity import DefaultAzureCredential
            endpoint = os.environ["CONTAINERREGISTRY_ENDPOINT"]
            client = ContainerRegistryClient(endpoint, DefaultAzureCredential(), audience="my_audience")
            received = client.update_tag_properties(
                "my_repository",
                "latest",
                can_delete=False,
                can_list=False,
                can_read=False,
                can_write=False,
            )
        """

    @distributed_trace
    def update_tag_properties(self, *args: Union[str, ArtifactTagProperties], **kwargs) -> ArtifactTagProperties:
        repository = str(args[0])
        tag = str(args[1])
        properties = None
        if len(args) == 3:
            properties = cast(ArtifactTagProperties, args[2])
        else:
            properties = ArtifactTagProperties()

        properties.can_delete = kwargs.pop("can_delete", properties.can_delete)
        properties.can_list = kwargs.pop("can_list", properties.can_list)
        properties.can_read = kwargs.pop("can_read", properties.can_read)
        properties.can_write = kwargs.pop("can_write", properties.can_write)

        tag_attributes = self._client.container_registry.update_tag_attributes(
            repository, tag, value=properties._to_generated(), **kwargs  # pylint: disable=protected-access
        )
        return ArtifactTagProperties._from_generated(  # pylint: disable=protected-access
            tag_attributes.tag, # type: ignore
            repository=repository
        )

    @overload
    def update_repository_properties(
        self,
        repository: str,
        properties: RepositoryProperties,
        **kwargs
    ) -> RepositoryProperties:
        """Set the permission properties of a repository.

        The updatable properties include: `can_delete`, `can_list`, `can_read`, and `can_write`.

        :param str repository: Name of the repository.
        :param properties: Properties to set for the repository. This is a positional-only
            parameter. Please provide either this or individual keyword parameters.
        :type properties: ~azure.containerregistry.RepositoryProperties
        :rtype: ~azure.containerregistry.RepositoryProperties
        :raises: ~azure.core.exceptions.ResourceNotFoundError
        """

    @overload
    def update_repository_properties(
        self,
        repository: str,
        *,
        can_delete: Optional[bool] = None,
        can_list: Optional[bool] = None,
        can_read: Optional[bool] = None,
        can_write: Optional[bool] = None,
        **kwargs
    ) -> RepositoryProperties:
        """Set the permission properties of a repository.

        The updatable properties include: `can_delete`, `can_list`, `can_read`, and `can_write`.

        :param str repository: Name of the repository.
        :keyword bool can_delete: Delete permissions for a repository.
        :keyword bool can_list: List permissions for a repository.
        :keyword bool can_read: Read permissions for a repository.
        :keyword bool can_write: Write permissions for a repository.
        :rtype: ~azure.containerregistry.RepositoryProperties
        :raises: ~azure.core.exceptions.ResourceNotFoundError
        """

    @distributed_trace
    def update_repository_properties(
        self, *args: Union[str, RepositoryProperties], **kwargs
    ) -> RepositoryProperties:
        repository = str(args[0])
        properties = None
        if len(args) == 2:
            properties = cast(RepositoryProperties, args[1])
        else:
            properties = RepositoryProperties()

        properties.can_delete = kwargs.pop("can_delete", properties.can_delete)
        properties.can_list = kwargs.pop("can_list", properties.can_list)
        properties.can_read = kwargs.pop("can_read", properties.can_read)
        properties.can_write = kwargs.pop("can_write", properties.can_write)

        return RepositoryProperties._from_generated(  # pylint: disable=protected-access
            self._client.container_registry.update_properties(
                repository, value=properties._to_generated(), **kwargs  # pylint: disable=protected-access
            )
        )

    @distributed_trace
    def upload_manifest(
        self, repository: str, manifest: Union[OCIManifest, IO], *, tag: Optional[str] = None, **kwargs
    ) -> str:
        """Upload a manifest for an OCI artifact.

        :param str repository: Name of the repository
        :param manifest: The manifest to upload. Note: This must be a seekable stream.
        :type manifest: ~azure.containerregistry.models.OCIManifest or IO
        :keyword tag: Tag of the manifest.
        :paramtype tag: str or None
        :returns: The digest of the uploaded manifest, calculated by the registry.
        :rtype: str
        :raises ValueError: If the parameter repository or manifest is None.
        :raises ~azure.core.exceptions.HttpResponseError:
            If the digest in the response does not match the digest of the uploaded manifest.
        """
        try:
            if isinstance(manifest, OCIManifest):
                data = _serialize_manifest(manifest)
            else:
                data = manifest
            tag_or_digest = tag
            if tag_or_digest is None:
                tag_or_digest = _compute_digest(data)

            response_headers = self._client.container_registry.create_manifest(
                name=repository,
                reference=tag_or_digest,
                payload=data,
                content_type=OCI_MANIFEST_MEDIA_TYPE,
                headers={"Accept": OCI_MANIFEST_MEDIA_TYPE},
                cls=_return_response_headers,
                **kwargs
            )
            digest = response_headers['Docker-Content-Digest']
            if not _validate_digest(data, digest):
                raise ValueError("The digest in the response does not match the digest of the uploaded manifest.")
        except ValueError:
            if repository is None or manifest is None:
                raise ValueError("The parameter repository and manifest cannot be None.")
            raise
        return digest

    @distributed_trace
    def upload_blob(self, repository: str, data: IO, **kwargs) -> str:
        """Upload an artifact blob.

        :param str repository: Name of the repository
        :param data: The blob to upload. Note: This must be a seekable stream.
        :type data: IO
        :returns: The digest of the uploaded blob, calculated by the registry.
        :rtype: str
        :raises ValueError: If the parameter repository or data is None.
        """
        try:
            start_upload_response_headers = cast(Dict[str, str], self._client.container_registry_blob.start_upload(
                repository, cls=_return_response_headers, **kwargs
            ))
            upload_chunk_response_headers = cast(Dict[str, str], self._client.container_registry_blob.upload_chunk(
                start_upload_response_headers['Location'],
                data,
                cls=_return_response_headers,
                **kwargs
            ))
            digest = _compute_digest(data)
            complete_upload_response_headers = cast(
                Dict[str, str],
                self._client.container_registry_blob.complete_upload(
                    digest=digest,
                    next_link=upload_chunk_response_headers['Location'],
                    cls=_return_response_headers,
                    **kwargs
                )
            )
        except ValueError:
            if repository is None or data is None:
                raise ValueError("The parameter repository and data cannot be None.")
            raise
        return complete_upload_response_headers['Docker-Content-Digest']

    @distributed_trace
    def download_manifest(self, repository: str, tag_or_digest: str, **kwargs) -> DownloadManifestResult:
        """Download the manifest for an OCI artifact.

        :param str repository: Name of the repository
        :param str tag_or_digest: The tag or digest of the manifest to download.
            When digest is provided, will use this digest to compare with the one calculated by the response payload.
            When tag is provided, will use the digest in response headers to compare.
        :returns: DownloadManifestResult
        :rtype: ~azure.containerregistry.models.DownloadManifestResult
        :raises ValueError: If the parameter repository or tag_or_digest is None.
        :raises ~azure.core.exceptions.HttpResponseError:
            If the requested digest does not match the digest of the received manifest.
        """
        try:
            response, manifest_wrapper = cast(
                Tuple[PipelineResponse, ManifestWrapper],
                self._client.container_registry.get_manifest(
                    name=repository,
                    reference=tag_or_digest,
                    headers={"Accept": OCI_MANIFEST_MEDIA_TYPE},
                    cls=_return_response_and_deserialized,
                    **kwargs
                )
            )
            manifest = OCIManifest.deserialize(cast(ManifestWrapper, manifest_wrapper).serialize())
            manifest_stream = _serialize_manifest(manifest)
            if tag_or_digest.startswith("sha256:"):
                digest = tag_or_digest
            else:
                digest = response.http_response.headers['Docker-Content-Digest']
            if not _validate_digest(manifest_stream, digest):
                raise ValueError("The requested digest does not match the digest of the received manifest.")
        except ValueError:
            if repository is None or tag_or_digest is None:
                raise ValueError("The parameter repository and tag_or_digest cannot be None.")
            raise
        return DownloadManifestResult(digest=digest, data=manifest_stream, manifest=manifest)

    @distributed_trace
    def download_blob(self, repository: str, digest: str, **kwargs) -> DownloadBlobResult:
        """Download a blob that is part of an artifact.

        :param str repository: Name of the repository
        :param str digest: The digest of the blob to download.
        :returns: DownloadBlobResult
        :rtype: ~azure.containerregistry.DownloadBlobResult
        :raises ValueError: If the parameter repository or digest is None.
        """
        try:
            deserialized = self._client.container_registry_blob.get_blob(repository, digest, **kwargs)
        except ValueError:
            if repository is None or digest is None:
                raise ValueError("The parameter repository and digest cannot be None.")
            raise

        blob_content = b''
        for chunk in deserialized: # type: ignore
            if chunk:
                blob_content += chunk
        return DownloadBlobResult(data=BytesIO(blob_content), digest=digest)

    @distributed_trace
    def delete_manifest(self, repository: str, tag_or_digest: str, **kwargs) -> None:
        """Delete a manifest. If the manifest cannot be found or a response status code of
        404 is returned an error will not be raised.

        :param str repository: Name of the repository the manifest belongs to
        :param str tag_or_digest: Tag or digest of the manifest to be deleted
        :returns: None
        :raises: ~azure.core.exceptions.HttpResponseError

        Example

        .. code-block:: python

            from azure.containerregistry import ContainerRegistryClient
            from azure.identity import DefaultAzureCredential
            endpoint = os.environ["CONTAINERREGISTRY_ENDPOINT"]
            client = ContainerRegistryClient(endpoint, DefaultAzureCredential(), audience="my_audience")
            client.delete_manifest("my_repository", "my_tag_or_digest")
        """
        if _is_tag(tag_or_digest):
            tag_or_digest = self._get_digest_from_tag(repository, tag_or_digest)

        self._client.container_registry.delete_manifest(repository, tag_or_digest, **kwargs)

    @distributed_trace
    def delete_blob(self, repository: str, tag_or_digest: str, **kwargs) -> None:
        """Delete a blob. If the blob cannot be found or a response status code of
        404 is returned an error will not be raised.

        :param str repository: Name of the repository the manifest belongs to
        :param str tag_or_digest: Tag or digest of the blob to be deleted
        :returns: None
        :raises: ~azure.core.exceptions.HttpResponseError

        Example

        .. code-block:: python

            from azure.containerregistry import ContainerRegistryClient
            from azure.identity import DefaultAzureCredential
            endpoint = os.environ["CONTAINERREGISTRY_ENDPOINT"]
            client = ContainerRegistryClient(endpoint, DefaultAzureCredential(), audience="my_audience")
            client.delete_blob("my_repository", "my_tag_or_digest")
        """
        if _is_tag(tag_or_digest):
            tag_or_digest = self._get_digest_from_tag(repository, tag_or_digest)

        self._client.container_registry_blob.delete_blob(repository, tag_or_digest, **kwargs)
