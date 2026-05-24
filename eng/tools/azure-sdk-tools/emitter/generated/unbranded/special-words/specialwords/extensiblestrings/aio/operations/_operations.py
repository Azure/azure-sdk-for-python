# coding=utf-8
from collections.abc import MutableMapping
import json
from typing import Any, Callable, Optional, TypeVar, Union

from corehttp.exceptions import (
    ClientAuthenticationError,
    HttpResponseError,
    ResourceExistsError,
    ResourceNotFoundError,
    ResourceNotModifiedError,
    StreamClosedError,
    StreamConsumedError,
    map_error,
)
from corehttp.rest import AsyncHttpResponse, HttpRequest
from corehttp.runtime import AsyncPipelineClient
from corehttp.runtime.pipeline import PipelineResponse
from corehttp.utils import case_insensitive_dict

from ... import models as _models2
from ...._utils.model_base import SdkJSONEncoder, _deserialize
from ...._utils.serialization import Deserializer, Serializer
from ....aio._configuration import SpecialWordsClientConfiguration
from ...operations._operations import build_extensible_strings_put_extensible_string_value_request

T = TypeVar("T")
ClsType = Optional[Callable[[PipelineResponse[HttpRequest, AsyncHttpResponse], T, dict[str, Any]], Any]]


class ExtensibleStringsOperations:
    """
    .. warning::
        **DO NOT** instantiate this class directly.

        Instead, you should access the following operations through
        :class:`~specialwords.aio.SpecialWordsClient`'s
        :attr:`extensible_strings` attribute.
    """

    def __init__(self, *args, **kwargs) -> None:
        input_args = list(args)
        self._client: AsyncPipelineClient = input_args.pop(0) if input_args else kwargs.pop("client")
        self._config: SpecialWordsClientConfiguration = input_args.pop(0) if input_args else kwargs.pop("config")
        self._serialize: Serializer = input_args.pop(0) if input_args else kwargs.pop("serializer")
        self._deserialize: Deserializer = input_args.pop(0) if input_args else kwargs.pop("deserializer")

    async def put_extensible_string_value(
        self, body: Union[str, _models2.ExtensibleString], **kwargs: Any
    ) -> Union[str, _models2.ExtensibleString]:
        """put_extensible_string_value.

        :param body: Known values are: "and", "as", "assert", "async", "await", "break", "class",
         "constructor", "continue", "def", "del", "elif", "else", "except", "exec", "finally", "for",
         "from", "global", "if", "import", "in", "is", "lambda", "not", "or", "pass", "raise", "return",
         "try", "while", "with", and "yield". Required.
        :type body: str or ~specialwords.extensiblestrings.models.ExtensibleString
        :return: ExtensibleString
        :rtype: str or ~specialwords.extensiblestrings.models.ExtensibleString
        :raises ~corehttp.exceptions.HttpResponseError:
        """
        error_map: MutableMapping = {
            401: ClientAuthenticationError,
            404: ResourceNotFoundError,
            409: ResourceExistsError,
            304: ResourceNotModifiedError,
        }
        error_map.update(kwargs.pop("error_map", {}) or {})

        _headers = case_insensitive_dict(kwargs.pop("headers", {}) or {})
        _params = kwargs.pop("params", {}) or {}

        content_type: str = kwargs.pop("content_type", _headers.pop("content-type", "application/json"))
        cls: ClsType[Union[str, _models2.ExtensibleString]] = kwargs.pop("cls", None)

        _content = json.dumps(body, cls=SdkJSONEncoder, exclude_readonly=True)  # type: ignore

        _request = build_extensible_strings_put_extensible_string_value_request(
            content_type=content_type,
            content=_content,
            headers=_headers,
            params=_params,
        )
        path_format_arguments = {
            "endpoint": self._serialize.url("self._config.endpoint", self._config.endpoint, "str", skip_quote=True),
        }
        _request.url = self._client.format_url(_request.url, **path_format_arguments)

        _decompress = kwargs.pop("decompress", True)
        _stream = kwargs.pop("stream", False)
        pipeline_response: PipelineResponse = await self._client.pipeline.run(_request, stream=_stream, **kwargs)

        response = pipeline_response.http_response

        if response.status_code not in [200]:
            if _stream:
                try:
                    await response.read()  # Load the body in memory and close the socket
                except (StreamConsumedError, StreamClosedError):
                    pass
            map_error(status_code=response.status_code, response=response, error_map=error_map)
            raise HttpResponseError(response=response)

        response_headers = {}
        response_headers["content-type"] = self._deserialize("str", response.headers.get("content-type"))

        if _stream:
            deserialized = response.iter_bytes() if _decompress else response.iter_raw()
        else:
            deserialized = _deserialize(Union[str, _models2.ExtensibleString], response.json())

        if cls:
            return cls(pipeline_response, deserialized, response_headers)  # type: ignore

        return deserialized  # type: ignore
