# coding=utf-8
from collections.abc import MutableMapping
import json
from typing import Any, Callable, Optional, TYPE_CHECKING, TypeVar, overload

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

from ... import models as _models
from ..._utils.model_base import SdkJSONEncoder, _deserialize
from ..._utils.serialization import Deserializer, Serializer
from ...operations._operations import (
    build_envelope_object_custom_properties_get_request,
    build_envelope_object_custom_properties_put_request,
    build_envelope_object_default_get_request,
    build_envelope_object_default_put_request,
    build_no_envelope_custom_discriminator_get_request,
    build_no_envelope_custom_discriminator_put_request,
    build_no_envelope_default_get_request,
    build_no_envelope_default_put_request,
)
from .._configuration import DiscriminatedClientConfiguration

if TYPE_CHECKING:
    from ... import _types
T = TypeVar("T")
ClsType = Optional[Callable[[PipelineResponse[HttpRequest, AsyncHttpResponse], T, dict[str, Any]], Any]]


class EnvelopeOperations:
    """
    .. warning::
        **DO NOT** instantiate this class directly.

        Instead, you should access the following operations through
        :class:`~typetest.discriminatedunion.aio.DiscriminatedClient`'s
        :attr:`envelope` attribute.
    """

    def __init__(self, *args, **kwargs) -> None:
        input_args = list(args)
        self._client: AsyncPipelineClient = input_args.pop(0) if input_args else kwargs.pop("client")
        self._config: DiscriminatedClientConfiguration = input_args.pop(0) if input_args else kwargs.pop("config")
        self._serialize: Serializer = input_args.pop(0) if input_args else kwargs.pop("serializer")
        self._deserialize: Deserializer = input_args.pop(0) if input_args else kwargs.pop("deserializer")

        self.object = EnvelopeObjectOperations(self._client, self._config, self._serialize, self._deserialize)


class NoEnvelopeOperations:
    """
    .. warning::
        **DO NOT** instantiate this class directly.

        Instead, you should access the following operations through
        :class:`~typetest.discriminatedunion.aio.DiscriminatedClient`'s
        :attr:`no_envelope` attribute.
    """

    def __init__(self, *args, **kwargs) -> None:
        input_args = list(args)
        self._client: AsyncPipelineClient = input_args.pop(0) if input_args else kwargs.pop("client")
        self._config: DiscriminatedClientConfiguration = input_args.pop(0) if input_args else kwargs.pop("config")
        self._serialize: Serializer = input_args.pop(0) if input_args else kwargs.pop("serializer")
        self._deserialize: Deserializer = input_args.pop(0) if input_args else kwargs.pop("deserializer")

        self.default = NoEnvelopeDefaultOperations(self._client, self._config, self._serialize, self._deserialize)
        self.custom_discriminator = NoEnvelopeCustomDiscriminatorOperations(
            self._client, self._config, self._serialize, self._deserialize
        )


class EnvelopeObjectOperations:
    """
    .. warning::
        **DO NOT** instantiate this class directly.

        Instead, you should access the following operations through
        :class:`~typetest.discriminatedunion.aio.DiscriminatedClient`'s
        :attr:`object` attribute.
    """

    def __init__(self, *args, **kwargs) -> None:
        input_args = list(args)
        self._client: AsyncPipelineClient = input_args.pop(0) if input_args else kwargs.pop("client")
        self._config: DiscriminatedClientConfiguration = input_args.pop(0) if input_args else kwargs.pop("config")
        self._serialize: Serializer = input_args.pop(0) if input_args else kwargs.pop("serializer")
        self._deserialize: Deserializer = input_args.pop(0) if input_args else kwargs.pop("deserializer")

        self.default = EnvelopeObjectDefaultOperations(self._client, self._config, self._serialize, self._deserialize)
        self.custom_properties = EnvelopeObjectCustomPropertiesOperations(
            self._client, self._config, self._serialize, self._deserialize
        )


class NoEnvelopeDefaultOperations:
    """
    .. warning::
        **DO NOT** instantiate this class directly.

        Instead, you should access the following operations through
        :class:`~typetest.discriminatedunion.aio.DiscriminatedClient`'s
        :attr:`default` attribute.
    """

    def __init__(self, *args, **kwargs) -> None:
        input_args = list(args)
        self._client: AsyncPipelineClient = input_args.pop(0) if input_args else kwargs.pop("client")
        self._config: DiscriminatedClientConfiguration = input_args.pop(0) if input_args else kwargs.pop("config")
        self._serialize: Serializer = input_args.pop(0) if input_args else kwargs.pop("serializer")
        self._deserialize: Deserializer = input_args.pop(0) if input_args else kwargs.pop("deserializer")

    async def get(self, *, kind: Optional[str] = None, **kwargs: Any) -> "_types.PetInline":
        """get.

        :keyword kind: Default value is None.
        :paramtype kind: str
        :return: Cat or Dog
        :rtype: ~typetest.discriminatedunion.models.Cat or ~typetest.discriminatedunion.models.Dog
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

        cls: ClsType["_types.PetInline"] = kwargs.pop("cls", None)

        _request = build_no_envelope_default_get_request(
            kind=kind,
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

        if _stream:
            deserialized = response.iter_bytes() if _decompress else response.iter_raw()
        else:
            deserialized = _deserialize("_types.PetInline", response.json())

        if cls:
            return cls(pipeline_response, deserialized, {})  # type: ignore

        return deserialized  # type: ignore

    @overload
    async def put(
        self, input: _models.Cat, *, content_type: str = "application/json", **kwargs: Any
    ) -> "_types.PetInline":
        """put.

        :param input: Required.
        :type input: ~typetest.discriminatedunion.models.Cat
        :keyword content_type: Body Parameter content-type. Content type parameter for JSON body.
         Default value is "application/json".
        :paramtype content_type: str
        :return: Cat or Dog
        :rtype: ~typetest.discriminatedunion.models.Cat or ~typetest.discriminatedunion.models.Dog
        :raises ~corehttp.exceptions.HttpResponseError:
        """

    @overload
    async def put(
        self, input: _models.Dog, *, content_type: str = "application/json", **kwargs: Any
    ) -> "_types.PetInline":
        """put.

        :param input: Required.
        :type input: ~typetest.discriminatedunion.models.Dog
        :keyword content_type: Body Parameter content-type. Content type parameter for JSON body.
         Default value is "application/json".
        :paramtype content_type: str
        :return: Cat or Dog
        :rtype: ~typetest.discriminatedunion.models.Cat or ~typetest.discriminatedunion.models.Dog
        :raises ~corehttp.exceptions.HttpResponseError:
        """

    async def put(self, input: "_types.PetInline", **kwargs: Any) -> "_types.PetInline":
        """put.

        :param input: Is either a Cat type or a Dog type. Required.
        :type input: ~typetest.discriminatedunion.models.Cat or ~typetest.discriminatedunion.models.Dog
        :return: Cat or Dog
        :rtype: ~typetest.discriminatedunion.models.Cat or ~typetest.discriminatedunion.models.Dog
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

        content_type: Optional[str] = kwargs.pop("content_type", _headers.pop("Content-Type", None))
        cls: ClsType["_types.PetInline"] = kwargs.pop("cls", None)

        content_type = content_type or "application/json"
        _content = json.dumps(input, cls=SdkJSONEncoder, exclude_readonly=True)  # type: ignore

        _request = build_no_envelope_default_put_request(
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

        if _stream:
            deserialized = response.iter_bytes() if _decompress else response.iter_raw()
        else:
            deserialized = _deserialize("_types.PetInline", response.json())

        if cls:
            return cls(pipeline_response, deserialized, {})  # type: ignore

        return deserialized  # type: ignore


class NoEnvelopeCustomDiscriminatorOperations:
    """
    .. warning::
        **DO NOT** instantiate this class directly.

        Instead, you should access the following operations through
        :class:`~typetest.discriminatedunion.aio.DiscriminatedClient`'s
        :attr:`custom_discriminator` attribute.
    """

    def __init__(self, *args, **kwargs) -> None:
        input_args = list(args)
        self._client: AsyncPipelineClient = input_args.pop(0) if input_args else kwargs.pop("client")
        self._config: DiscriminatedClientConfiguration = input_args.pop(0) if input_args else kwargs.pop("config")
        self._serialize: Serializer = input_args.pop(0) if input_args else kwargs.pop("serializer")
        self._deserialize: Deserializer = input_args.pop(0) if input_args else kwargs.pop("deserializer")

    async def get(self, *, type: Optional[str] = None, **kwargs: Any) -> "_types.PetInlineWithCustomDiscriminator":
        """get.

        :keyword type: Default value is None.
        :paramtype type: str
        :return: Cat or Dog
        :rtype: ~typetest.discriminatedunion.models.Cat or ~typetest.discriminatedunion.models.Dog
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

        cls: ClsType["_types.PetInlineWithCustomDiscriminator"] = kwargs.pop("cls", None)

        _request = build_no_envelope_custom_discriminator_get_request(
            type=type,
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

        if _stream:
            deserialized = response.iter_bytes() if _decompress else response.iter_raw()
        else:
            deserialized = _deserialize("_types.PetInlineWithCustomDiscriminator", response.json())

        if cls:
            return cls(pipeline_response, deserialized, {})  # type: ignore

        return deserialized  # type: ignore

    @overload
    async def put(
        self, input: _models.Cat, *, content_type: str = "application/json", **kwargs: Any
    ) -> "_types.PetInlineWithCustomDiscriminator":
        """put.

        :param input: Required.
        :type input: ~typetest.discriminatedunion.models.Cat
        :keyword content_type: Body Parameter content-type. Content type parameter for JSON body.
         Default value is "application/json".
        :paramtype content_type: str
        :return: Cat or Dog
        :rtype: ~typetest.discriminatedunion.models.Cat or ~typetest.discriminatedunion.models.Dog
        :raises ~corehttp.exceptions.HttpResponseError:
        """

    @overload
    async def put(
        self, input: _models.Dog, *, content_type: str = "application/json", **kwargs: Any
    ) -> "_types.PetInlineWithCustomDiscriminator":
        """put.

        :param input: Required.
        :type input: ~typetest.discriminatedunion.models.Dog
        :keyword content_type: Body Parameter content-type. Content type parameter for JSON body.
         Default value is "application/json".
        :paramtype content_type: str
        :return: Cat or Dog
        :rtype: ~typetest.discriminatedunion.models.Cat or ~typetest.discriminatedunion.models.Dog
        :raises ~corehttp.exceptions.HttpResponseError:
        """

    async def put(
        self, input: "_types.PetInlineWithCustomDiscriminator", **kwargs: Any
    ) -> "_types.PetInlineWithCustomDiscriminator":
        """put.

        :param input: Is either a Cat type or a Dog type. Required.
        :type input: ~typetest.discriminatedunion.models.Cat or ~typetest.discriminatedunion.models.Dog
        :return: Cat or Dog
        :rtype: ~typetest.discriminatedunion.models.Cat or ~typetest.discriminatedunion.models.Dog
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

        content_type: Optional[str] = kwargs.pop("content_type", _headers.pop("Content-Type", None))
        cls: ClsType["_types.PetInlineWithCustomDiscriminator"] = kwargs.pop("cls", None)

        content_type = content_type or "application/json"
        _content = json.dumps(input, cls=SdkJSONEncoder, exclude_readonly=True)  # type: ignore

        _request = build_no_envelope_custom_discriminator_put_request(
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

        if _stream:
            deserialized = response.iter_bytes() if _decompress else response.iter_raw()
        else:
            deserialized = _deserialize("_types.PetInlineWithCustomDiscriminator", response.json())

        if cls:
            return cls(pipeline_response, deserialized, {})  # type: ignore

        return deserialized  # type: ignore


class EnvelopeObjectDefaultOperations:
    """
    .. warning::
        **DO NOT** instantiate this class directly.

        Instead, you should access the following operations through
        :class:`~typetest.discriminatedunion.aio.DiscriminatedClient`'s
        :attr:`default` attribute.
    """

    def __init__(self, *args, **kwargs) -> None:
        input_args = list(args)
        self._client: AsyncPipelineClient = input_args.pop(0) if input_args else kwargs.pop("client")
        self._config: DiscriminatedClientConfiguration = input_args.pop(0) if input_args else kwargs.pop("config")
        self._serialize: Serializer = input_args.pop(0) if input_args else kwargs.pop("serializer")
        self._deserialize: Deserializer = input_args.pop(0) if input_args else kwargs.pop("deserializer")

    async def get(self, *, kind: Optional[str] = None, **kwargs: Any) -> "_types.PetWithEnvelope":
        """get.

        :keyword kind: Default value is None.
        :paramtype kind: str
        :return: Cat or Dog
        :rtype: ~typetest.discriminatedunion.models.Cat or ~typetest.discriminatedunion.models.Dog
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

        cls: ClsType["_types.PetWithEnvelope"] = kwargs.pop("cls", None)

        _request = build_envelope_object_default_get_request(
            kind=kind,
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

        if _stream:
            deserialized = response.iter_bytes() if _decompress else response.iter_raw()
        else:
            deserialized = _deserialize("_types.PetWithEnvelope", response.json())

        if cls:
            return cls(pipeline_response, deserialized, {})  # type: ignore

        return deserialized  # type: ignore

    @overload
    async def put(
        self, input: _models.Cat, *, content_type: str = "application/json", **kwargs: Any
    ) -> "_types.PetWithEnvelope":
        """put.

        :param input: Required.
        :type input: ~typetest.discriminatedunion.models.Cat
        :keyword content_type: Body Parameter content-type. Content type parameter for JSON body.
         Default value is "application/json".
        :paramtype content_type: str
        :return: Cat or Dog
        :rtype: ~typetest.discriminatedunion.models.Cat or ~typetest.discriminatedunion.models.Dog
        :raises ~corehttp.exceptions.HttpResponseError:
        """

    @overload
    async def put(
        self, input: _models.Dog, *, content_type: str = "application/json", **kwargs: Any
    ) -> "_types.PetWithEnvelope":
        """put.

        :param input: Required.
        :type input: ~typetest.discriminatedunion.models.Dog
        :keyword content_type: Body Parameter content-type. Content type parameter for JSON body.
         Default value is "application/json".
        :paramtype content_type: str
        :return: Cat or Dog
        :rtype: ~typetest.discriminatedunion.models.Cat or ~typetest.discriminatedunion.models.Dog
        :raises ~corehttp.exceptions.HttpResponseError:
        """

    async def put(self, input: "_types.PetWithEnvelope", **kwargs: Any) -> "_types.PetWithEnvelope":
        """put.

        :param input: Is either a Cat type or a Dog type. Required.
        :type input: ~typetest.discriminatedunion.models.Cat or ~typetest.discriminatedunion.models.Dog
        :return: Cat or Dog
        :rtype: ~typetest.discriminatedunion.models.Cat or ~typetest.discriminatedunion.models.Dog
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

        content_type: Optional[str] = kwargs.pop("content_type", _headers.pop("Content-Type", None))
        cls: ClsType["_types.PetWithEnvelope"] = kwargs.pop("cls", None)

        content_type = content_type or "application/json"
        _content = json.dumps(input, cls=SdkJSONEncoder, exclude_readonly=True)  # type: ignore

        _request = build_envelope_object_default_put_request(
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

        if _stream:
            deserialized = response.iter_bytes() if _decompress else response.iter_raw()
        else:
            deserialized = _deserialize("_types.PetWithEnvelope", response.json())

        if cls:
            return cls(pipeline_response, deserialized, {})  # type: ignore

        return deserialized  # type: ignore


class EnvelopeObjectCustomPropertiesOperations:
    """
    .. warning::
        **DO NOT** instantiate this class directly.

        Instead, you should access the following operations through
        :class:`~typetest.discriminatedunion.aio.DiscriminatedClient`'s
        :attr:`custom_properties` attribute.
    """

    def __init__(self, *args, **kwargs) -> None:
        input_args = list(args)
        self._client: AsyncPipelineClient = input_args.pop(0) if input_args else kwargs.pop("client")
        self._config: DiscriminatedClientConfiguration = input_args.pop(0) if input_args else kwargs.pop("config")
        self._serialize: Serializer = input_args.pop(0) if input_args else kwargs.pop("serializer")
        self._deserialize: Deserializer = input_args.pop(0) if input_args else kwargs.pop("deserializer")

    async def get(self, *, pet_type: Optional[str] = None, **kwargs: Any) -> "_types.PetWithCustomNames":
        """get.

        :keyword pet_type: Default value is None.
        :paramtype pet_type: str
        :return: Cat or Dog
        :rtype: ~typetest.discriminatedunion.models.Cat or ~typetest.discriminatedunion.models.Dog
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

        cls: ClsType["_types.PetWithCustomNames"] = kwargs.pop("cls", None)

        _request = build_envelope_object_custom_properties_get_request(
            pet_type=pet_type,
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

        if _stream:
            deserialized = response.iter_bytes() if _decompress else response.iter_raw()
        else:
            deserialized = _deserialize("_types.PetWithCustomNames", response.json())

        if cls:
            return cls(pipeline_response, deserialized, {})  # type: ignore

        return deserialized  # type: ignore

    @overload
    async def put(
        self, input: _models.Cat, *, content_type: str = "application/json", **kwargs: Any
    ) -> "_types.PetWithCustomNames":
        """put.

        :param input: Required.
        :type input: ~typetest.discriminatedunion.models.Cat
        :keyword content_type: Body Parameter content-type. Content type parameter for JSON body.
         Default value is "application/json".
        :paramtype content_type: str
        :return: Cat or Dog
        :rtype: ~typetest.discriminatedunion.models.Cat or ~typetest.discriminatedunion.models.Dog
        :raises ~corehttp.exceptions.HttpResponseError:
        """

    @overload
    async def put(
        self, input: _models.Dog, *, content_type: str = "application/json", **kwargs: Any
    ) -> "_types.PetWithCustomNames":
        """put.

        :param input: Required.
        :type input: ~typetest.discriminatedunion.models.Dog
        :keyword content_type: Body Parameter content-type. Content type parameter for JSON body.
         Default value is "application/json".
        :paramtype content_type: str
        :return: Cat or Dog
        :rtype: ~typetest.discriminatedunion.models.Cat or ~typetest.discriminatedunion.models.Dog
        :raises ~corehttp.exceptions.HttpResponseError:
        """

    async def put(self, input: "_types.PetWithCustomNames", **kwargs: Any) -> "_types.PetWithCustomNames":
        """put.

        :param input: Is either a Cat type or a Dog type. Required.
        :type input: ~typetest.discriminatedunion.models.Cat or ~typetest.discriminatedunion.models.Dog
        :return: Cat or Dog
        :rtype: ~typetest.discriminatedunion.models.Cat or ~typetest.discriminatedunion.models.Dog
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

        content_type: Optional[str] = kwargs.pop("content_type", _headers.pop("Content-Type", None))
        cls: ClsType["_types.PetWithCustomNames"] = kwargs.pop("cls", None)

        content_type = content_type or "application/json"
        _content = json.dumps(input, cls=SdkJSONEncoder, exclude_readonly=True)  # type: ignore

        _request = build_envelope_object_custom_properties_put_request(
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

        if _stream:
            deserialized = response.iter_bytes() if _decompress else response.iter_raw()
        else:
            deserialized = _deserialize("_types.PetWithCustomNames", response.json())

        if cls:
            return cls(pipeline_response, deserialized, {})  # type: ignore

        return deserialized  # type: ignore
