# coding=utf-8
from collections.abc import MutableMapping
from typing import Any, Callable, Optional, TypeVar

from corehttp.exceptions import (
    ClientAuthenticationError,
    HttpResponseError,
    ResourceExistsError,
    ResourceNotFoundError,
    ResourceNotModifiedError,
    map_error,
)
from corehttp.rest import HttpRequest, HttpResponse
from corehttp.runtime import PipelineClient
from corehttp.runtime.pipeline import PipelineResponse

from ..._configuration import RoutesClientConfiguration
from ..._utils.serialization import Deserializer, Serializer
from ..labelexpansion.operations._operations import PathParametersLabelExpansionOperations
from ..matrixexpansion.operations._operations import PathParametersMatrixExpansionOperations
from ..pathexpansion.operations._operations import PathParametersPathExpansionOperations
from ..reservedexpansion.operations._operations import PathParametersReservedExpansionOperations
from ..simpleexpansion.operations._operations import PathParametersSimpleExpansionOperations

T = TypeVar("T")
ClsType = Optional[Callable[[PipelineResponse[HttpRequest, HttpResponse], T, dict[str, Any]], Any]]

_SERIALIZER = Serializer()
_SERIALIZER.client_side_validation = False


def build_path_parameters_template_only_request(  # pylint: disable=name-too-long
    param: str, **kwargs: Any
) -> HttpRequest:
    # Construct URL
    _url = "/routes/path/template-only/{param}"
    path_format_arguments = {
        "param": _SERIALIZER.url("param", param, "str"),
    }

    _url: str = _url.format(**path_format_arguments)  # type: ignore

    return HttpRequest(method="GET", url=_url, **kwargs)


def build_path_parameters_explicit_request(param: str, **kwargs: Any) -> HttpRequest:
    # Construct URL
    _url = "/routes/path/explicit/{param}"
    path_format_arguments = {
        "param": _SERIALIZER.url("param", param, "str"),
    }

    _url: str = _url.format(**path_format_arguments)  # type: ignore

    return HttpRequest(method="GET", url=_url, **kwargs)


def build_path_parameters_annotation_only_request(  # pylint: disable=name-too-long
    param: str, **kwargs: Any
) -> HttpRequest:
    # Construct URL
    _url = "/routes/path/annotation-only/{param}"
    path_format_arguments = {
        "param": _SERIALIZER.url("param", param, "str"),
    }

    _url: str = _url.format(**path_format_arguments)  # type: ignore

    return HttpRequest(method="GET", url=_url, **kwargs)


class PathParametersOperations:
    """
    .. warning::
        **DO NOT** instantiate this class directly.

        Instead, you should access the following operations through
        :class:`~routes.RoutesClient`'s
        :attr:`path_parameters` attribute.
    """

    def __init__(self, *args, **kwargs) -> None:
        input_args = list(args)
        self._client: PipelineClient = input_args.pop(0) if input_args else kwargs.pop("client")
        self._config: RoutesClientConfiguration = input_args.pop(0) if input_args else kwargs.pop("config")
        self._serialize: Serializer = input_args.pop(0) if input_args else kwargs.pop("serializer")
        self._deserialize: Deserializer = input_args.pop(0) if input_args else kwargs.pop("deserializer")

        self.reserved_expansion = PathParametersReservedExpansionOperations(
            self._client, self._config, self._serialize, self._deserialize
        )
        self.simple_expansion = PathParametersSimpleExpansionOperations(
            self._client, self._config, self._serialize, self._deserialize
        )
        self.path_expansion = PathParametersPathExpansionOperations(
            self._client, self._config, self._serialize, self._deserialize
        )
        self.label_expansion = PathParametersLabelExpansionOperations(
            self._client, self._config, self._serialize, self._deserialize
        )
        self.matrix_expansion = PathParametersMatrixExpansionOperations(
            self._client, self._config, self._serialize, self._deserialize
        )

    def template_only(self, param: str, **kwargs: Any) -> None:  # pylint: disable=inconsistent-return-statements
        """template_only.

        :param param: Required.
        :type param: str
        :return: None
        :rtype: None
        :raises ~corehttp.exceptions.HttpResponseError:
        """
        error_map: MutableMapping = {
            401: ClientAuthenticationError,
            404: ResourceNotFoundError,
            409: ResourceExistsError,
            304: ResourceNotModifiedError,
        }
        error_map.update(kwargs.pop("error_map", {}) or {})

        _headers = kwargs.pop("headers", {}) or {}
        _params = kwargs.pop("params", {}) or {}

        cls: ClsType[None] = kwargs.pop("cls", None)

        _request = build_path_parameters_template_only_request(
            param=param,
            headers=_headers,
            params=_params,
        )
        path_format_arguments = {
            "endpoint": self._serialize.url("self._config.endpoint", self._config.endpoint, "str", skip_quote=True),
        }
        _request.url = self._client.format_url(_request.url, **path_format_arguments)

        _stream = False
        pipeline_response: PipelineResponse = self._client.pipeline.run(_request, stream=_stream, **kwargs)

        response = pipeline_response.http_response

        if response.status_code not in [204]:
            map_error(status_code=response.status_code, response=response, error_map=error_map)
            raise HttpResponseError(response=response)

        if cls:
            return cls(pipeline_response, None, {})  # type: ignore

    def explicit(self, param: str, **kwargs: Any) -> None:  # pylint: disable=inconsistent-return-statements
        """explicit.

        :param param: Required.
        :type param: str
        :return: None
        :rtype: None
        :raises ~corehttp.exceptions.HttpResponseError:
        """
        error_map: MutableMapping = {
            401: ClientAuthenticationError,
            404: ResourceNotFoundError,
            409: ResourceExistsError,
            304: ResourceNotModifiedError,
        }
        error_map.update(kwargs.pop("error_map", {}) or {})

        _headers = kwargs.pop("headers", {}) or {}
        _params = kwargs.pop("params", {}) or {}

        cls: ClsType[None] = kwargs.pop("cls", None)

        _request = build_path_parameters_explicit_request(
            param=param,
            headers=_headers,
            params=_params,
        )
        path_format_arguments = {
            "endpoint": self._serialize.url("self._config.endpoint", self._config.endpoint, "str", skip_quote=True),
        }
        _request.url = self._client.format_url(_request.url, **path_format_arguments)

        _stream = False
        pipeline_response: PipelineResponse = self._client.pipeline.run(_request, stream=_stream, **kwargs)

        response = pipeline_response.http_response

        if response.status_code not in [204]:
            map_error(status_code=response.status_code, response=response, error_map=error_map)
            raise HttpResponseError(response=response)

        if cls:
            return cls(pipeline_response, None, {})  # type: ignore

    def annotation_only(self, param: str, **kwargs: Any) -> None:  # pylint: disable=inconsistent-return-statements
        """annotation_only.

        :param param: Required.
        :type param: str
        :return: None
        :rtype: None
        :raises ~corehttp.exceptions.HttpResponseError:
        """
        error_map: MutableMapping = {
            401: ClientAuthenticationError,
            404: ResourceNotFoundError,
            409: ResourceExistsError,
            304: ResourceNotModifiedError,
        }
        error_map.update(kwargs.pop("error_map", {}) or {})

        _headers = kwargs.pop("headers", {}) or {}
        _params = kwargs.pop("params", {}) or {}

        cls: ClsType[None] = kwargs.pop("cls", None)

        _request = build_path_parameters_annotation_only_request(
            param=param,
            headers=_headers,
            params=_params,
        )
        path_format_arguments = {
            "endpoint": self._serialize.url("self._config.endpoint", self._config.endpoint, "str", skip_quote=True),
        }
        _request.url = self._client.format_url(_request.url, **path_format_arguments)

        _stream = False
        pipeline_response: PipelineResponse = self._client.pipeline.run(_request, stream=_stream, **kwargs)

        response = pipeline_response.http_response

        if response.status_code not in [204]:
            map_error(status_code=response.status_code, response=response, error_map=error_map)
            raise HttpResponseError(response=response)

        if cls:
            return cls(pipeline_response, None, {})  # type: ignore
