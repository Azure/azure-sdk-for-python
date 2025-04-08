# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""Customize generated code here.

Follow our quickstart for examples: https://aka.ms/azsdk/python/dpcodegen/python/customize
"""
from typing import Optional, Any, Dict, List, IO, Union, overload
from azure.core.credentials import AzureKeyCredential
from azure.core.tracing.decorator_async import distributed_trace_async
from azure.core.exceptions import (
    ClientAuthenticationError,
    HttpResponseError,
    ResourceExistsError,
    ResourceNotFoundError,
    ResourceNotModifiedError,
    map_error,
)
from azure.core.utils import case_insensitive_dict
from ._operations import (
    WebPubSubServiceClientOperationsMixin as WebPubSubServiceClientOperationsMixinGenerated,
    JSON,
    build_web_pub_sub_service_send_to_all_request,
    build_web_pub_sub_service_send_to_connection_request,
    build_web_pub_sub_service_send_to_user_request,
    build_web_pub_sub_service_send_to_group_request,
)
from ..._operations._patch import get_token_by_key


class WebPubSubServiceClientOperationsMixin(WebPubSubServiceClientOperationsMixinGenerated):
    @distributed_trace_async
    async def get_client_access_token(  # pylint: disable=arguments-differ
        self,
        *,
        user_id: Optional[str] = None,
        roles: Optional[List[str]] = None,
        minutes_to_expire: Optional[int] = 60,
        jwt_headers: Dict[str, Any] = None,
        groups: Optional[List[str]] = None,
        client_protocol: Optional[str] = "Default",
        **kwargs: Any
    ) -> JSON:
        """Generate token for the client to connect Azure Web PubSub service.

        :keyword user_id: User Id.
        :paramtype user_id: str
        :keyword roles: Roles that the connection with the generated token will have.
        :paramtype roles: list[str]
        :keyword minutes_to_expire: The expire time of the generated token.
        :paramtype minutes_to_expire: int
        :keyword dict[str, any] jwt_headers: Any headers you want to pass to jwt encoding.
        :keyword groups: Groups that the connection will join when it connects. Default value is None.
        :paramtype groups: list[str]
        :keyword api_version: Api Version. The default value is "2021-10-01". Note that overriding this
         default value may result in unsupported behavior.
        :paramtype api_version: str
        :keyword client_protocol: The type of client protocol. Case-insensitive. If not set, it's "Default". For Web
         PubSub for Socket.IO, "SocketIO" type is supported. For Web PubSub, the valid values are
         'Default', 'MQTT'. Known values are: "Default", "MQTT" and "SocketIO". Default value is "Default".
        :paramtype client_type: str
        :return: JSON object
        :rtype: JSON
        :raises: ~azure.core.exceptions.HttpResponseError

        Example:

                >>> get_client_access_token()
                {
                    'baseUrl': 'wss://contoso.com/api/webpubsub/client/hubs/theHub',
                    'token': '<access-token>...',
                    'url': 'wss://contoso.com/api/webpubsub/client/hubs/theHub?access_token=<access-token>...'
                }
        """
        endpoint = self._config.endpoint.lower()
        if not endpoint.startswith("http://") and not endpoint.startswith("https://"):
            raise ValueError(
                "Invalid endpoint: '{}' has unknown scheme - expected 'http://' or 'https://'".format(endpoint)
            )
        # Ensure endpoint has no trailing slash

        endpoint = endpoint.rstrip("/")

        # Switch from http(s) to ws(s) scheme

        client_endpoint = "ws" + endpoint[4:]
        hub = self._config.hub
        path = "/client/hubs/"
        if client_protocol.lower() == "mqtt":
            path = "/clients/mqtt/hubs/" 
        elif client_protocol.lower() == "socketio":
            path = "/clients/socketio/hubs/"
        client_url = client_endpoint + path + hub
        if isinstance(self._config.credential, AzureKeyCredential):
            token = get_token_by_key(
                endpoint,
                path,
                hub,
                self._config.credential.key,
                user_id=user_id,
                roles=roles,
                minutes_to_expire=minutes_to_expire,
                jwt_headers=jwt_headers or {},
                groups=groups,
                **kwargs
            )
        else:
            access_token = await super().get_client_access_token(
                user_id=user_id,
                roles=roles,
                minutes_to_expire=minutes_to_expire,
                groups=groups,
                client_protocol=client_protocol,
                **kwargs
            )
            token = access_token.get("token")
        return {
            "baseUrl": client_url,
            "token": token,
            "url": "{}?access_token={}".format(client_url, token),
        }

    get_client_access_token.metadata = {"url": "/api/hubs/{hub}/:generateToken"}  # type: ignore

    @overload
    async def send_to_all(  # pylint: disable=inconsistent-return-statements
        self,
        message: Union[str, JSON],
        *,
        excluded: Optional[List[str]] = None,
        filter: Optional[str] = None,
        content_type: Optional[str] = "application/json",
        **kwargs: Any
    ) -> None:
        """Broadcast content inside request body to all the connected client connections.

        Broadcast content inside request body to all the connected client connections.

        :param message: The payload body. Required.
        :type message: Union[str, JSON]
        :keyword excluded: Excluded connection Ids. Default value is None.
        :paramtype excluded: list[str]
        :keyword filter: Following OData filter syntax to filter out the subscribers receiving the
         messages. Default value is None.
        :paramtype filter: str
        :keyword content_type: The content type of the payload. Default value is None. Allowed values are 'application/json', 'application/octet-stream' and 'text/plain'
        :paramtype content_type: str
        :return: None
        :rtype: None
        :raises ~azure.core.exceptions.HttpResponseError:
        """

    @overload
    async def send_to_all(  # pylint: disable=inconsistent-return-statements
        self,
        message: str,
        *,
        excluded: Optional[List[str]] = None,
        filter: Optional[str] = None,
        content_type: Optional[str] = "text/plain",
        **kwargs: Any
    ) -> None:
        """Broadcast content inside request body to all the connected client connections.

        Broadcast content inside request body to all the connected client connections.

        :param message: The payload body. Required.
        :type message: str
        :keyword excluded: Excluded connection Ids. Default value is None.
        :paramtype excluded: list[str]
        :keyword filter: Following OData filter syntax to filter out the subscribers receiving the
         messages. Default value is None.
        :paramtype filter: str
        :keyword content_type: The content type of the payload. Default value is None. Allowed values are 'application/json', 'application/octet-stream' and 'text/plain'
        :paramtype content_type: str
        :return: None
        :rtype: None
        :raises ~azure.core.exceptions.HttpResponseError:
        """

    @overload
    async def send_to_all(  # pylint: disable=inconsistent-return-statements
        self,
        message: IO,
        *,
        excluded: Optional[List[str]] = None,
        filter: Optional[str] = None,
        content_type: Optional[str] = "application/octet-stream",
        **kwargs: Any
    ) -> None:
        """Broadcast content inside request body to all the connected client connections.

        Broadcast content inside request body to all the connected client connections.

        :param message: The payload body. Required.
        :type message: IO
        :keyword excluded: Excluded connection Ids. Default value is None.
        :paramtype excluded: list[str]
        :keyword filter: Following OData filter syntax to filter out the subscribers receiving the
         messages. Default value is None.
        :paramtype filter: str
        :keyword content_type: The content type of the payload. Default value is None. Allowed values are 'application/json', 'application/octet-stream' and 'text/plain'
        :paramtype content_type: str
        :return: None
        :rtype: None
        :raises ~azure.core.exceptions.HttpResponseError:
        """

    @distributed_trace_async
    async def send_to_all(  # pylint: disable=inconsistent-return-statements
        self,
        message: Union[IO, str, JSON],
        *,
        excluded: Optional[List[str]] = None,
        filter: Optional[str] = None,
        content_type: Optional[str] = None,
        **kwargs: Any
    ) -> None:
        """Broadcast content inside request body to all the connected client connections.

        Broadcast content inside request body to all the connected client connections.

        :param message: The payload body. Required.
        :type message: Union[IO, str, JSON]
        :keyword excluded: Excluded connection Ids. Default value is None.
        :paramtype excluded: list[str]
        :keyword filter: Following OData filter syntax to filter out the subscribers receiving the
         messages. Default value is None.
        :paramtype filter: str
        :keyword content_type: The content type of the payload. Default value is None. Allowed values are 'application/json', 'application/octet-stream' and 'text/plain'
        :paramtype content_type: str
        :return: None
        :rtype: None
        :raises ~azure.core.exceptions.HttpResponseError:
        """
        error_map = {
            401: ClientAuthenticationError,
            404: ResourceNotFoundError,
            409: ResourceExistsError,
            304: ResourceNotModifiedError,
        }
        error_map.update(kwargs.pop("error_map", {}) or {})

        _headers = case_insensitive_dict(kwargs.pop("headers", {}) or {})
        _params = kwargs.pop("params", {}) or {}

        content_type = (
            _headers.pop("Content-Type", "application/json") if content_type is None else content_type
        )  # type: str
        cls = kwargs.pop("cls", None)  # type: ClsType[None]

        _json = None
        _content = None
        content_type = content_type or ""
        if content_type.split(";")[0] in ["application/json"]:
            _json = message
        elif content_type.split(";")[0] in ["application/octet-stream", "text/plain"]:
            _content = message
        else:
            raise ValueError(
                "The content_type '{}' is not one of the allowed values: "
                "['application/json', 'application/octet-stream', 'text/plain']".format(content_type)
            )
        request = build_web_pub_sub_service_send_to_all_request(
            hub=self._config.hub,
            excluded=excluded,
            filter=filter,
            content_type=content_type,
            api_version=self._config.api_version,
            content=_content,
            json=_json,
            headers=_headers,
            params=_params,
        )
        path_format_arguments = {
            "endpoint": self._serialize.url("self._config.endpoint", self._config.endpoint, "str", skip_quote=True),
        }
        request.url = self._client.format_url(request.url, **path_format_arguments)  # type: ignore

        pipeline_response = await self._client._pipeline.run(  # type: ignore # pylint: disable=protected-access
            request, stream=False, **kwargs
        )

        response = pipeline_response.http_response

        if response.status_code not in [202]:
            map_error(status_code=response.status_code, response=response, error_map=error_map)
            raise HttpResponseError(response=response)
        if cls:
            return cls(pipeline_response, None, {})

    @overload
    async def send_to_group(  # pylint: disable=inconsistent-return-statements
        self,
        group: str,
        message: Union[str, JSON],
        *,
        excluded: Optional[List[str]] = None,
        filter: Optional[str] = None,
        content_type: Optional[str] = "application/json",
        **kwargs: Any
    ) -> None:
        """Send content inside request body to a group of connections.

        Send content inside request body to a group of connections.

        :param group: Target group name, which length should be greater than 0 and less than 1025.
         Required.
        :type group: str
        :param message: The payload body. Required.
        :type message: Union[str, JSON]
        :keyword excluded: Excluded connection Ids. Default value is None.
        :paramtype excluded: list[str]
        :keyword filter: Following OData filter syntax to filter out the subscribers receiving the
         messages. Default value is None.
        :paramtype filter: str
        :keyword content_type: The content type of the payload. Default value is None. Allowed values are 'application/json', 'application/octet-stream' and 'text/plain'
        :paramtype content_type: str
        :return: None
        :rtype: None
        :raises ~azure.core.exceptions.HttpResponseError:
        """

    @overload
    async def send_to_group(  # pylint: disable=inconsistent-return-statements
        self,
        group: str,
        message: str,
        *,
        excluded: Optional[List[str]] = None,
        filter: Optional[str] = None,
        content_type: Optional[str] = "text/plain",
        **kwargs: Any
    ) -> None:
        """Send content inside request body to a group of connections.

        Send content inside request body to a group of connections.

        :param group: Target group name, which length should be greater than 0 and less than 1025.
         Required.
        :type group: str
        :param message: The payload body. Required.
        :type message: str
        :keyword excluded: Excluded connection Ids. Default value is None.
        :paramtype excluded: list[str]
        :keyword filter: Following OData filter syntax to filter out the subscribers receiving the
         messages. Default value is None.
        :paramtype filter: str
        :keyword content_type: The content type of the payload. Default value is None. Allowed values are 'application/json', 'application/octet-stream' and 'text/plain'
        :paramtype content_type: str
        :return: None
        :rtype: None
        :raises ~azure.core.exceptions.HttpResponseError:
        """

    @overload
    async def send_to_group(  # pylint: disable=inconsistent-return-statements
        self,
        group: str,
        message: IO,
        *,
        excluded: Optional[List[str]] = None,
        filter: Optional[str] = None,
        content_type: Optional[str] = "application/octet-stream",
        **kwargs: Any
    ) -> None:
        """Send content inside request body to a group of connections.

        Send content inside request body to a group of connections.

        :param group: Target group name, which length should be greater than 0 and less than 1025.
         Required.
        :type group: str
        :param message: The payload body. Required.
        :type message: IO
        :keyword excluded: Excluded connection Ids. Default value is None.
        :paramtype excluded: list[str]
        :keyword filter: Following OData filter syntax to filter out the subscribers receiving the
         messages. Default value is None.
        :paramtype filter: str
        :keyword content_type: The content type of the payload. Default value is None. Allowed values are 'application/json', 'application/octet-stream' and 'text/plain'
        :paramtype content_type: str
        :return: None
        :rtype: None
        :raises ~azure.core.exceptions.HttpResponseError:
        """

    @distributed_trace_async
    async def send_to_group(  # pylint: disable=inconsistent-return-statements
        self,
        group: str,
        message: Union[IO, str, JSON],
        *,
        excluded: Optional[List[str]] = None,
        filter: Optional[str] = None,
        content_type: Optional[str] = None,
        **kwargs: Any
    ) -> None:
        """Send content inside request body to a group of connections.

        Send content inside request body to a group of connections.

        :param group: Target group name, which length should be greater than 0 and less than 1025.
         Required.
        :type group: str
        :param message: The payload body. Required.
        :type message: Union[IO, str, JSON]
        :keyword excluded: Excluded connection Ids. Default value is None.
        :paramtype excluded: list[str]
        :keyword filter: Following OData filter syntax to filter out the subscribers receiving the
         messages. Default value is None.
        :paramtype filter: str
        :keyword content_type: The content type of the payload. Default value is None. Allowed values are 'application/json', 'application/octet-stream' and 'text/plain'
        :paramtype content_type: str
        :return: None
        :rtype: None
        :raises ~azure.core.exceptions.HttpResponseError:
        """
        error_map = {
            401: ClientAuthenticationError,
            404: ResourceNotFoundError,
            409: ResourceExistsError,
            304: ResourceNotModifiedError,
        }
        error_map.update(kwargs.pop("error_map", {}) or {})

        _headers = case_insensitive_dict(kwargs.pop("headers", {}) or {})
        _params = kwargs.pop("params", {}) or {}

        content_type = (
            _headers.pop("Content-Type", "application/json") if content_type is None else content_type
        )  # type: str
        cls = kwargs.pop("cls", None)  # type: ClsType[None]

        _json = None
        _content = None
        content_type = content_type or ""
        if content_type.split(";")[0] in ["application/json"]:
            _json = message
        elif content_type.split(";")[0] in ["application/octet-stream", "text/plain"]:
            _content = message
        else:
            raise ValueError(
                "The content_type '{}' is not one of the allowed values: "
                "['application/json', 'application/octet-stream', 'text/plain']".format(content_type)
            )
        request = build_web_pub_sub_service_send_to_group_request(
            group=group,
            hub=self._config.hub,
            excluded=excluded,
            filter=filter,
            content_type=content_type,
            api_version=self._config.api_version,
            content=_content,
            json=_json,
            headers=_headers,
            params=_params,
        )
        path_format_arguments = {
            "endpoint": self._serialize.url("self._config.endpoint", self._config.endpoint, "str", skip_quote=True),
        }
        request.url = self._client.format_url(request.url, **path_format_arguments)  # type: ignore

        pipeline_response = await self._client._pipeline.run(  # type: ignore # pylint: disable=protected-access
            request, stream=False, **kwargs
        )

        response = pipeline_response.http_response

        if response.status_code not in [202]:
            map_error(status_code=response.status_code, response=response, error_map=error_map)
            raise HttpResponseError(response=response)
        if cls:
            return cls(pipeline_response, None, {})

    @overload
    async def send_to_connection(  # pylint: disable=inconsistent-return-statements
        self,
        connection_id: str,
        message: Union[str, JSON],
        *,
        content_type: Optional[str] = "application/json",
        **kwargs: Any
    ) -> None:
        """Send content inside request body to the specific connection.

        Send content inside request body to the specific connection.

        :param connection_id: The connection Id. Required.
        :type connection_id: str
        :param message: The payload body. Required.
        :type message: Union[str, JSON]
        :keyword content_type: The content type of the payload. Default value is None. Allowed values are 'application/json', 'application/octet-stream' and 'text/plain'
        :paramtype content_type: str
        :return: None
        :rtype: None
        :raises ~azure.core.exceptions.HttpResponseError:
        """

    @overload
    async def send_to_connection(  # pylint: disable=inconsistent-return-statements
        self, connection_id: str, message: str, *, content_type: Optional[str] = "text/plain", **kwargs: Any
    ) -> None:
        """Send content inside request body to the specific connection.

        Send content inside request body to the specific connection.

        :param connection_id: The connection Id. Required.
        :type connection_id: str
        :param message: The payload body. Required.
        :type message: str
        :keyword content_type: The content type of the payload. Default value is None. Allowed values are 'application/json', 'application/octet-stream' and 'text/plain'
        :paramtype content_type: str
        :return: None
        :rtype: None
        :raises ~azure.core.exceptions.HttpResponseError:
        """

    @overload
    async def send_to_connection(  # pylint: disable=inconsistent-return-statements
        self,
        connection_id: str,
        message: IO,
        *,
        content_type: Optional[str] = "application/octet-stream",
        **kwargs: Any
    ) -> None:
        """Send content inside request body to the specific connection.

        Send content inside request body to the specific connection.

        :param connection_id: The connection Id. Required.
        :type connection_id: str
        :param message: The payload body. Required.
        :type message: IO
        :keyword content_type: The content type of the payload. Default value is None. Allowed values are 'application/json', 'application/octet-stream' and 'text/plain'
        :paramtype content_type: str
        :return: None
        :rtype: None
        :raises ~azure.core.exceptions.HttpResponseError:
        """

    @distributed_trace_async
    async def send_to_connection(  # pylint: disable=inconsistent-return-statements
        self, connection_id: str, message: Union[IO, str, JSON], *, content_type: Optional[str] = None, **kwargs: Any
    ) -> None:
        """Send content inside request body to the specific connection.

        Send content inside request body to the specific connection.

        :param connection_id: The connection Id. Required.
        :type connection_id: str
        :param message: The payload body. Required.
        :type message: Union[IO, str, JSON]
        :keyword content_type: The content type of the payload. Default value is None. Allowed values are 'application/json', 'application/octet-stream' and 'text/plain'
        :paramtype content_type: str
        :return: None
        :rtype: None
        :raises ~azure.core.exceptions.HttpResponseError:
        """
        error_map = {
            401: ClientAuthenticationError,
            404: ResourceNotFoundError,
            409: ResourceExistsError,
            304: ResourceNotModifiedError,
        }
        error_map.update(kwargs.pop("error_map", {}) or {})

        _headers = case_insensitive_dict(kwargs.pop("headers", {}) or {})
        _params = kwargs.pop("params", {}) or {}

        content_type = (
            _headers.pop("Content-Type", "application/json") if content_type is None else content_type
        )  # type: str
        cls = kwargs.pop("cls", None)  # type: ClsType[None]

        _json = None
        _content = None
        content_type = content_type or ""
        if content_type.split(";")[0] in ["application/json"]:
            _json = message
        elif content_type.split(";")[0] in ["application/octet-stream", "text/plain"]:
            _content = message
        else:
            raise ValueError(
                "The content_type '{}' is not one of the allowed values: "
                "['application/json', 'application/octet-stream', 'text/plain']".format(content_type)
            )
        request = build_web_pub_sub_service_send_to_connection_request(
            connection_id=connection_id,
            hub=self._config.hub,
            content_type=content_type,
            api_version=self._config.api_version,
            content=_content,
            json=_json,
            headers=_headers,
            params=_params,
        )
        path_format_arguments = {
            "endpoint": self._serialize.url("self._config.endpoint", self._config.endpoint, "str", skip_quote=True),
        }
        request.url = self._client.format_url(request.url, **path_format_arguments)  # type: ignore

        pipeline_response = await self._client._pipeline.run(  # type: ignore # pylint: disable=protected-access
            request, stream=False, **kwargs
        )

        response = pipeline_response.http_response

        if response.status_code not in [202]:
            map_error(status_code=response.status_code, response=response, error_map=error_map)
            raise HttpResponseError(response=response)
        if cls:
            return cls(pipeline_response, None, {})

    @overload
    async def send_to_user(  # pylint: disable=inconsistent-return-statements
        self,
        user_id: str,
        message: Union[str, JSON],
        *,
        filter: Optional[str] = None,
        content_type: Optional[str] = "application/json",
        **kwargs: Any
    ) -> None:
        """Send content inside request body to the specific user.

        Send content inside request body to the specific user.

        :param user_id: The user Id. Required.
        :type user_id: str
        :param message: The payload body. Required.
        :type message: Union[str, JSON]
        :keyword filter: Following OData filter syntax to filter out the subscribers receiving the
         messages. Default value is None.
        :paramtype filter: str
        :keyword content_type: The content type of the payload. Default value is None. Allowed values are 'application/json', 'application/octet-stream' and 'text/plain'
        :paramtype content_type: str
        :return: None
        :rtype: None
        :raises ~azure.core.exceptions.HttpResponseError:
        """

    @overload
    async def send_to_user(  # pylint: disable=inconsistent-return-statements
        self,
        user_id: str,
        message: str,
        *,
        filter: Optional[str] = None,
        content_type: Optional[str] = "text/plain",
        **kwargs: Any
    ) -> None:
        """Send content inside request body to the specific user.

        Send content inside request body to the specific user.

        :param user_id: The user Id. Required.
        :type user_id: str
        :param message: The payload body. Required.
        :type message: str
        :keyword filter: Following OData filter syntax to filter out the subscribers receiving the
         messages. Default value is None.
        :paramtype filter: str
        :keyword content_type: The content type of the payload. Default value is None. Allowed values are 'application/json', 'application/octet-stream' and 'text/plain'
        :paramtype content_type: str
        :return: None
        :rtype: None
        :raises ~azure.core.exceptions.HttpResponseError:
        """

    @overload
    async def send_to_user(  # pylint: disable=inconsistent-return-statements
        self,
        user_id: str,
        message: IO,
        *,
        filter: Optional[str] = None,
        content_type: Optional[str] = "application/octet-stream",
        **kwargs: Any
    ) -> None:
        """Send content inside request body to the specific user.

        Send content inside request body to the specific user.

        :param user_id: The user Id. Required.
        :type user_id: str
        :param message: The payload body. Required.
        :type message: IO
        :keyword filter: Following OData filter syntax to filter out the subscribers receiving the
         messages. Default value is None.
        :paramtype filter: str
        :keyword content_type: The content type of the payload. Default value is None. Allowed values are 'application/json', 'application/octet-stream' and 'text/plain'
        :paramtype content_type: str
        :return: None
        :rtype: None
        :raises ~azure.core.exceptions.HttpResponseError:
        """

    @distributed_trace_async
    async def send_to_user(  # pylint: disable=inconsistent-return-statements
        self,
        user_id: str,
        message: Union[IO, str, JSON],
        *,
        filter: Optional[str] = None,
        content_type: Optional[str] = None,
        **kwargs: Any
    ) -> None:
        """Send content inside request body to the specific user.

        Send content inside request body to the specific user.

        :param user_id: The user Id. Required.
        :type user_id: str
        :param message: The payload body. Required.
        :type message: Union[IO, str, JSON]
        :keyword filter: Following OData filter syntax to filter out the subscribers receiving the
         messages. Default value is None.
        :paramtype filter: str
        :keyword content_type: The content type of the payload. Default value is None. Allowed values are 'application/json', 'application/octet-stream' and 'text/plain'
        :paramtype content_type: str
        :return: None
        :rtype: None
        :raises ~azure.core.exceptions.HttpResponseError:
        """
        error_map = {
            401: ClientAuthenticationError,
            404: ResourceNotFoundError,
            409: ResourceExistsError,
            304: ResourceNotModifiedError,
        }
        error_map.update(kwargs.pop("error_map", {}) or {})

        _headers = case_insensitive_dict(kwargs.pop("headers", {}) or {})
        _params = kwargs.pop("params", {}) or {}

        content_type = (
            _headers.pop("Content-Type", "application/json") if content_type is None else content_type
        )  # type: str
        cls = kwargs.pop("cls", None)  # type: ClsType[None]

        _json = None
        _content = None
        content_type = content_type or ""
        if content_type.split(";")[0] in ["application/json"]:
            _json = message
        elif content_type.split(";")[0] in ["application/octet-stream", "text/plain"]:
            _content = message
        else:
            raise ValueError(
                "The content_type '{}' is not one of the allowed values: "
                "['application/json', 'application/octet-stream', 'text/plain']".format(content_type)
            )
        request = build_web_pub_sub_service_send_to_user_request(
            user_id=user_id,
            hub=self._config.hub,
            filter=filter,
            content_type=content_type,
            api_version=self._config.api_version,
            content=_content,
            json=_json,
            headers=_headers,
            params=_params,
        )
        path_format_arguments = {
            "endpoint": self._serialize.url("self._config.endpoint", self._config.endpoint, "str", skip_quote=True),
        }
        request.url = self._client.format_url(request.url, **path_format_arguments)  # type: ignore

        pipeline_response = await self._client._pipeline.run(  # type: ignore # pylint: disable=protected-access
            request, stream=False, **kwargs
        )

        response = pipeline_response.http_response

        if response.status_code not in [202]:
            map_error(status_code=response.status_code, response=response, error_map=error_map)
            raise HttpResponseError(response=response)
        if cls:
            return cls(pipeline_response, None, {})


__all__: List[str] = [
    "WebPubSubServiceClientOperationsMixin"
]  # Add all objects you want publicly available to users at this package level


def patch_sdk():
    """Do not remove from this file.

    `patch_sdk` is a last resort escape hatch that allows you to do customizations
    you can't accomplish using the techniques described in
    https://aka.ms/azsdk/python/dpcodegen/python/customize
    """
