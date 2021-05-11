# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
from typing import TYPE_CHECKING, Dict, Any

from azure.core.exceptions import (
    ClientAuthenticationError,
    ResourceNotFoundError,
    ResourceExistsError,
    HttpResponseError,
    map_error,
)
from azure.core.async_paging import AsyncItemPaged, AsyncList
from azure.core.pipeline import AsyncPipeline
from azure.core.tracing.decorator import distributed_trace
from azure.core.tracing.decorator_async import distributed_trace_async

from ._async_base_client import ContainerRegistryBaseClient, AsyncTransportWrapper
from .._generated.models import AcrErrors
from .._helpers import _parse_next_link
from .._models import (
    ContentProperties,
    DeleteRepositoryResult,
    ArtifactManifestProperties,
    RepositoryProperties,
    ArtifactTagProperties,
)
from ._async_registry_artifact import RegistryArtifact

if TYPE_CHECKING:
    from azure.core.credentials_async import AsyncTokenCredential


class ContainerRepository(ContainerRegistryBaseClient):
    def __init__(
        self, endpoint: str, name: str, credential: "AsyncTokenCredential", **kwargs: Dict[str, Any]
    ) -> None:
        """Create a ContainerRepository from an endpoint, repository name, and credential

        :param str endpoint: An ACR endpoint
        :param str name: The name of a repository
        :param credential: The credential with which to authenticate
        :type credential: :class:`~azure.core.credentials_async.AsyncTokenCredential`
        :returns: None
        :raises: None
        """
        if not endpoint.startswith("https://") and not endpoint.startswith("http://"):
            endpoint = "https://" + endpoint
        self._endpoint = endpoint
        self._credential = credential
        self.name = name
        self.fully_qualified_name = self._endpoint + self.name
        super(ContainerRepository, self).__init__(endpoint=self._endpoint, credential=credential, **kwargs)

    @distributed_trace_async
    async def delete(self, **kwargs: Dict[str, Any]) -> DeleteRepositoryResult:
        """Delete a repository

        :returns: Object containing information about the deleted repository
        :rtype: :class:`~azure.containerregistry.DeleteRepositoryResult`
        :raises: :class:`~azure.core.exceptions.ResourceNotFoundError`
        """
        return DeleteRepositoryResult._from_generated(  # pylint: disable=protected-access
            await self._client.container_registry.delete_repository(self.name, **kwargs)
        )

    @distributed_trace_async
    async def get_properties(self, **kwargs: Dict[str, Any]) -> RepositoryProperties:
        """Get the properties of a repository

        :returns: :class:`~azure.containerregistry.RepositoryProperties`
        :raises: :class:`~azure.core.exceptions.ResourceNotFoundError`
        """
        return RepositoryProperties._from_generated(  # pylint: disable=protected-access
            await self._client.container_registry.get_properties(self.name, **kwargs)
        )

    @distributed_trace
    def list_manifests(self, **kwargs: Dict[str, Any]) -> AsyncItemPaged[ArtifactManifestProperties]:
        """List the artifacts for a repository

        :keyword last: Query parameter for the last item in the previous call. Ensuing
            call will return values after last lexically
        :paramtype last: str
        :keyword order_by: Query parameter for ordering by time ascending or descending
        :paramtype order_by: :class:`~azure.containerregistry.ManifestOrder` or str
        :keyword results_per_page: Number of repositories to return per page
        :paramtype results_per_page: int
        :return: ItemPaged[:class:`~azure.containerregistry.ArtifactManifestProperties`]
        :rtype: :class:`~azure.core.async_paging.AsyncItemPaged`
        :raises: :class:`~azure.core.exceptions.ResourceNotFoundError`
        """
        name = self.name
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
    async def set_properties(self, properties: ContentProperties, **kwargs: Dict[str, Any]) -> RepositoryProperties:
        """Set the properties of a repository

        :returns: :class:`~azure.containerregistry.RepositoryProperties`
        :raises: :class:`~azure.core.exceptions.ResourceNotFoundError`
        """
        return RepositoryProperties._from_generated(  # pylint: disable=protected-access
            await self._client.container_registry.set_properties(
                self.name,
                properties._to_generated(),  # pylint: disable=protected-access
                **kwargs
            )
        )

    @distributed_trace
    def get_artifact(self, tag_or_digest: str, **kwargs: Dict[str, Any]) -> RegistryArtifact:
        """Get a Registry Artifact object

        :param str repository_name: Name of the repository
        :param str tag_or_digest: The tag or digest of the artifact
        :returns: :class:`~azure.containerregistry.RegistryArtifact`
        :raises: None
        """
        _pipeline = AsyncPipeline(
            transport=AsyncTransportWrapper(
                self._client._client._pipeline._transport  # pylint: disable=protected-access
            ),
            policies=self._client._client._pipeline._impl_policies,  # pylint: disable=protected-access
        )
        return RegistryArtifact(
            self._endpoint, self.name, tag_or_digest, self._credential, pipeline=_pipeline, **kwargs
        )
