# coding=utf-8
from collections.abc import MutableMapping
from typing import Any, Callable, Optional, TypeVar, Union, overload

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
from corehttp.utils import case_insensitive_dict

from .. import models as _models1
from ....._configuration import MultiPartClientConfiguration
from ....._utils.model_base import Model as _Model
from ....._utils.serialization import Deserializer, Serializer
from ....._utils.utils import prepare_multipart_form_data

JSON = MutableMapping[str, Any]
T = TypeVar("T")
ClsType = Optional[Callable[[PipelineResponse[HttpRequest, HttpResponse], T, dict[str, Any]], Any]]

_SERIALIZER = Serializer()
_SERIALIZER.client_side_validation = False


def build_form_data_http_parts_non_string_float_request(**kwargs: Any) -> HttpRequest:  # pylint: disable=name-too-long
    _headers = case_insensitive_dict(kwargs.pop("headers", {}) or {})

    # Construct URL
    _url = "/multipart/form-data/non-string-float"

    return HttpRequest(method="POST", url=_url, headers=_headers, **kwargs)


class FormDataHttpPartsNonStringOperations:
    """
    .. warning::
        **DO NOT** instantiate this class directly.

        Instead, you should access the following operations through
        :class:`~payload.multipart.MultiPartClient`'s
        :attr:`non_string` attribute.
    """

    def __init__(self, *args, **kwargs) -> None:
        input_args = list(args)
        self._client: PipelineClient = input_args.pop(0) if input_args else kwargs.pop("client")
        self._config: MultiPartClientConfiguration = input_args.pop(0) if input_args else kwargs.pop("config")
        self._serialize: Serializer = input_args.pop(0) if input_args else kwargs.pop("serializer")
        self._deserialize: Deserializer = input_args.pop(0) if input_args else kwargs.pop("deserializer")

    @overload
    def float(self, body: _models1.FloatRequest, **kwargs: Any) -> None:
        """Test content-type: multipart/form-data for non string.

        :param body: Required.
        :type body: ~payload.multipart.formdata.httpparts.nonstring.models.FloatRequest
        :return: None
        :rtype: None
        :raises ~corehttp.exceptions.HttpResponseError:
        """

    @overload
    def float(self, body: JSON, **kwargs: Any) -> None:
        """Test content-type: multipart/form-data for non string.

        :param body: Required.
        :type body: JSON
        :return: None
        :rtype: None
        :raises ~corehttp.exceptions.HttpResponseError:
        """

    def float(  # pylint: disable=inconsistent-return-statements
        self, body: Union[_models1.FloatRequest, JSON], **kwargs: Any
    ) -> None:
        """Test content-type: multipart/form-data for non string.

        :param body: Is either a FloatRequest type or a JSON type. Required.
        :type body: ~payload.multipart.formdata.httpparts.nonstring.models.FloatRequest or JSON
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

        _body = body.as_dict() if isinstance(body, _Model) else body
        _file_fields: list[str] = []
        _data_fields: list[str] = ["temperature"]
        _files = prepare_multipart_form_data(_body, _file_fields, _data_fields)

        _request = build_form_data_http_parts_non_string_float_request(
            files=_files,
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
