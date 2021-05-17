# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
from typing import TYPE_CHECKING
from azure.core.exceptions import (
    ClientAuthenticationError,
    ResourceNotFoundError,
    ResourceExistsError,
    HttpResponseError,
    map_error,
)
from azure.core.paging import ItemPaged
from azure.core.pipeline import Pipeline
from azure.core.tracing.decorator import distributed_trace

from ._base_client import ContainerRegistryBaseClient, TransportWrapper
# from ._container_repository import ContainerRepository
from ._generated.models import AcrErrors
from ._helpers import _parse_next_link
# from ._registry_artifact import RegistryArtifact
# from ._models import DeleteRepositoryResult

if TYPE_CHECKING:
    from typing import Any, Dict, Optional
    from azure.core.credentials import TokenCredential
    from ._models import ArtifactTagProperties, ArtifactManifestProperties


class ContainerRegistryClient(ContainerRegistryBaseClient):
    def __init__(self, endpoint, credential=None, **kwargs):
        # type: (str, Optional[TokenCredential], **Any) -> None
        """Create a ContainerRegistryClient from an ACR endpoint and a credential
        :param str endpoint: An ACR endpoint
        :param credential: The credential with which to authenticate
        :type credential: :class:`~azure.core.credentials.TokenCredential`
        :returns: None
        :raises: None

        .. admonition:: Example:

            .. literalinclude:: ../samples/sample_create_client.py
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

    @distributed_trace
    def delete_repository(self, repository_name, **kwargs):
        # type: (str, **Any) -> None
        """Delete a repository

        :param str repository_name: The repository to delete
        :returns: None
        :rtype: None
        :raises: :class:`~azure.core.exceptions.ResourceNotFoundError`

        .. admonition:: Example:

            .. literalinclude:: ../samples/sample_create_client.py
                :start-after: [START delete_repository]
                :end-before: [END delete_repository]
                :language: python
                :dedent: 8
                :caption: Delete a repository from the `ContainerRegistryClient`
        """
        # return DeleteRepositoryResult._from_generated(  # pylint: disable=protected-access
        self._client.container_registry.delete_repository(repository_name, **kwargs)
        # )

    @distributed_trace
    def list_repository_names(self, **kwargs):
        # type: (**Any) -> ItemPaged[str]
        """List all repositories
        :keyword max: Maximum number of repositories to return
        :paramtype max: int
        :keyword last: Query parameter for the last item in the previous call. Ensuing
            call will return values after last lexically
        :paramtype last: str
        :keyword results_per_page: Number of repositories to return per page
        :paramtype results_per_page: int
        :return: ItemPaged[str]
        :rtype: :class:`~azure.core.paging.ItemPaged`
        :raises: :class:`~azure.core.exceptions.ResourceNotFoundError`

        .. admonition:: Example:

            .. literalinclude:: ../samples/sample_delete_old_tags.py
                :start-after: [START list_repository_names]
                :end-before: [END list_repository_names]
                :language: python
                :dedent: 8
                :caption: List repositories in a container registry account
        """
        n = kwargs.pop("results_per_page", None)
        last = kwargs.pop("last", None)

        cls = kwargs.pop("cls", None)  # type: ClsType["_models.Repositories"]
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
            elif "link" in pipeline_response.http_response.headers.keys():  # python 2.7 turns this into lowercase
                link = _parse_next_link(pipeline_response.http_response.headers["link"])
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
    def get_repository_properties(self, repository, **kwargs):
        # type: (str, **Any) -> RepositoryProperties
        """Get the properties of a repository

        :param str repository:
        :returns: :class:`~azure.containerregistry.RepositoryProperties`
        :raises: :class:`~azure.core.exceptions.ResourceNotFoundError`
        """
        return RepositoryProperties._from_generated(  # pylint: disable=protected-access
            self._client.container_registry.get_properties(self.name, **kwargs)
        )

    @distributed_trace
    def list_manifests(self, repository, **kwargs):
        # type: (str, **Any) -> ItemPaged[ArtifactManifestProperties]
        """List the artifacts for a repository

        :param str repository:
        :keyword order_by: Query parameter for ordering by time ascending or descending
        :paramtype order_by: :class:`~azure.containerregistry.ManifestOrder` or str
        :keyword results_per_page: Number of repositories to return per page
        :paramtype results_per_page: int
        :return: ItemPaged[:class:`ArtifactManifestProperties`]
        :rtype: :class:`~azure.core.paging.ItemPaged`
        :raises: :class:`~azure.core.exceptions.ResourceNotFoundError`
        """
        name = repository
        last = kwargs.pop("last", None)
        n = kwargs.pop("results_per_page", None)
        orderby = kwargs.pop("order_by", None)
        cls = kwargs.pop(
            "cls",
            lambda objs: [
                ArtifactManifestProperties._from_generated(x, repository_name=self.name)  # pylint: disable=protected-access
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
    def set_repository_properties(self, repository, properties, **kwargs):
        # type: (str, RepositoryProperties, **Any) -> RepositoryProperties
        """Set the properties of a repository

        :param str repository:
        :param properties: Properties to set for the repository
        :type properties: :class:`~azure.containerregistry.RepositoryProperties`
        :returns: :class:`~azure.containerregistry.RepositoryProperties`
        :raises: :class:`~azure.core.exceptions.ResourceNotFoundError`
        """
        return RepositoryProperties._from_generated(  # pylint: disable=protected-access
            self._client.container_registry.set_properties(
                self.name,
                properties._to_generated(),  # pylint: disable=protected-access
                **kwargs
            )
        )

    @distributed_trace
    def delete_manifest(self, repository, tag_or_digest, **kwargs):
        # type: (str, str, **Any) -> None
        """Delete a manifest

        :param str repository:
        :param str tag_or_digest:
        :returns: None
        :rtype: None
        :raises: :class:`~azure.core.exceptions.ResourceNotFoundError`

        Example

        .. code-block:: python
            from azure.containerregistry import ContainerRepositoryClient
            from azure.identity import DefaultAzureCredential
            account_url = os.environ["CONTAINERREGISTRY_ENDPOINT"]
            client = ContainerRepositoryClient(account_url, "my_repository", DefaultAzureCredential())
            client.delete()
        """
        if not self._digest:
            self._digest = self.tag_or_digest if not _is_tag(self.tag_or_digest) else self._get_digest_from_tag()
        self._client.container_registry.delete_manifest(self.repository, self._digest)
        # return DeleteRepositoryResult._from_generated(  # pylint: disable=protected-access
        #     self._client.container_registry.delete_repository(self.repository, **kwargs)
        # )

    @distributed_trace
    def delete_tag(self, repository, tag, **kwargs):
        # type: (str, str, **Any) -> None
        """Delete a tag from a repository

        :param str repository:
        :param str tag: The tag to be deleted
        :returns: None
        :rtype: None
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
    def get_manifest_properties(self, repository, tag_or_digest, **kwargs):
        # type: (str, str, **Any) -> ArtifactManifestProperties
        """Get the properties of a registry artifact

        :param str repository:
        :param str tag_or_digest:
        :returns: :class:`~azure.containerregistry.ArtifactManifestProperties`
        :raises: :class:`~azure.core.exceptions.ResourceNotFoundError`

        Example

        .. code-block:: python
            from azure.containerregistry import ContainerRepositoryClient
            from azure.identity import DefaultAzureCredential
            account_url = os.environ["CONTAINERREGISTRY_ENDPOINT"]
            client = ContainerRepositoryClient(account_url, "my_repository", DefaultAzureCredential())
            for artifact in client.list_manifests():
                properties = client.get_registry_artifact_properties(artifact.digest)
        """
        if not self._digest:
            self._digest = self.tag_or_digest if not _is_tag(self.tag_or_digest) else self._get_digest_from_tag()

        return ArtifactManifestProperties._from_generated(  # pylint: disable=protected-access
            self._client.container_registry.get_manifest_properties(self.repository, self._digest, **kwargs),
            repository_name=self.repository,
        )

    @distributed_trace
    def get_tag_properties(self, repository, tag, **kwargs):
        # type: (str, str, **Any) -> ArtifactTagProperties
        """Get the properties for a tag

        :param str repository:
        :param str tag: The tag to get properties for
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
    def list_tags(self, repository, **kwargs):
        # type: (str, **Any) -> ItemPaged[ArtifactTagProperties]
        """List the tags for a repository

        :param str repository:
        :keyword order_by: Query parameter for ordering by time ascending or descending
        :paramtype order_by: :class:`~azure.containerregistry.TagOrder` or str
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
    def set_manifest_properties(self, repository, tag_or_digest, properties, **kwargs):
        # type: (str, str, ArtifactManifestProperties, **Any) -> ArtifactManifestProperties
        """Set the properties for a manifest

        :param str repository:
        :param str tag_or_digest:
        :param properties: The property's values to be set
        :type properties: :class:`~azure.containerregistry.ArtifactManifestProperties`
        :returns: :class:`~azure.containerregistry.ArtifactManifestProperties`
        :raises: :class:`~azure.core.exceptions.ResourceNotFoundError`

        Example

        .. code-block:: python
            from azure.containerregistry import ContainerRepositoryClient
            from azure.identity import DefaultAzureCredential
            account_url = os.environ["CONTAINERREGISTRY_ENDPOINT"]
            client = ContainerRepositoryClient(account_url, "my_repository", DefaultAzureCredential())
            for artifact in client.list_manifests():
                received_properties = client.set_manifest_properties(
                    artifact.digest,
                    ManifestWriteableProperties(
                        can_delete=False,
                        can_list=False,
                        can_read=False,
                        can_write=False,
                    ),
                )
        """
        if not self._digest:
            self._digest = self.tag_or_digest if _is_tag(self.tag_or_digest) else self._get_digest_from_tag()

        return ArtifactManifestProperties._from_generated(  # pylint: disable=protected-access
            self._client.container_registry.update_manifest_properties(
                self.repository,
                self._digest,
                value=properties._to_generated(),  # pylint: disable=protected-access
                **kwargs
            ),
            repository_name=self.repository,
        )

    @distributed_trace
    def set_tag_properties(self, repository, tag, properties, **kwargs):
        # type: (str, str, ArtifactTagProperties, **Any) -> ArtifactTagProperties
        """Set the properties for a tag

        :param str repository:
        :param str tag: Tag to set properties for
        :param properties: The property's values to be set
        :type properties: ArtifactTagProperties
        :returns: :class:`~azure.containerregistry.ArtifactTagProperties`
        :raises: :class:`~azure.core.exceptions.ResourceNotFoundError`

        Example

        .. code-block:: python
            from azure.containerregistry import ContainerRepositoryClient, TagWriteableProperties
            from azure.identity import DefaultAzureCredential
            account_url = os.environ["CONTAINERREGISTRY_ENDPOINT"]
            client = ContainerRepositoryClient(account_url, "my_repository", DefaultAzureCredential())
            tag_identifier = "latest"
            received = client.set_tag_properties(
                tag_identifier,
                TagWriteableProperties(
                    can_delete=False,
                    can_list=False,
                    can_read=False,
                    can_write=False,
                ),
            )
        """
        return ArtifactTagProperties._from_generated(  # pylint: disable=protected-access
            self._client.container_registry.update_tag_attributes(
                self.repository, tag, value=properties._to_generated(), **kwargs  # pylint: disable=protected-access
            ),
            repository=self.repository,
        )
