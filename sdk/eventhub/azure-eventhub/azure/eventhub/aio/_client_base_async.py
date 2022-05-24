# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
from __future__ import unicode_literals

import logging
import asyncio
import time
import functools
from typing import TYPE_CHECKING, Any, Dict, List, Callable, Optional, Union, cast
import six

from azure.core.credentials import (
    AccessToken,
    AzureSasCredential,
    AzureNamedKeyCredential,
)

from .._client_base import (
    ClientBase,
    _generate_sas_token,
    _parse_conn_str,
    _get_backoff_time,
)

from .._pyamqp.message import Message
from .._pyamqp import constants, error as errors, utils as pyamqp_utils
from .._pyamqp.aio import AMQPClientAsync
from .._pyamqp.aio._authentication_async import JWTTokenAuthAsync
from .._utils import utc_from_timestamp, parse_sas_credential
from ..exceptions import ClientClosedError, ConnectError
from .._constants import (
    JWT_TOKEN_SCOPE,
    MGMT_OPERATION,
    MGMT_PARTITION_OPERATION,
    MGMT_STATUS_CODE,
    MGMT_STATUS_DESC, READ_OPERATION,
)
from ._async_utils import get_dict_with_loop_if_needed
from ._error_async import _handle_exception

if TYPE_CHECKING:
    from azure.core.credentials_async import AsyncTokenCredential

    try:
        from typing_extensions import Protocol
    except ImportError:
        Protocol = object  # type: ignore

_LOGGER = logging.getLogger(__name__)


class EventHubSharedKeyCredential(object):
    """The shared access key credential used for authentication.

    :param str policy: The name of the shared access policy.
    :param str key: The shared access key.
    """

    def __init__(self, policy: str, key: str):
        self.policy = policy
        self.key = key
        self.token_type = b"servicebus.windows.net:sastoken"

    async def get_token(self, *scopes, **kwargs) -> AccessToken:  # pylint:disable=unused-argument
        if not scopes:
            raise ValueError("No token scope provided.")
        return _generate_sas_token(scopes[0], self.policy, self.key)


class EventHubSASTokenCredential(object):
    """The shared access token credential used for authentication.

    :param str token: The shared access token string
    :param int expiry: The epoch timestamp
    """

    def __init__(self, token: str, expiry: int) -> None:
        """
        :param str token: The shared access token string
        :param int expiry: The epoch timestamp
        """
        self.token = token
        self.expiry = expiry
        self.token_type = b"servicebus.windows.net:sastoken"

    async def get_token(
        self, *scopes: str, **kwargs: Any  # pylint:disable=unused-argument
    ) -> AccessToken:
        """
        This method is automatically called when token is about to expire.
        """
        return AccessToken(self.token, self.expiry)


class EventhubAzureNamedKeyTokenCredentialAsync(object):
    """The named key credential used for authentication.

    :param credential: The AzureNamedKeyCredential that should be used.
    :type credential: ~azure.core.credentials.AzureNamedKeyCredential
    """

    def __init__(self, azure_named_key_credential):
        # type: (AzureNamedKeyCredential) -> None
        self._credential = azure_named_key_credential
        self.token_type = b"servicebus.windows.net:sastoken"

    async def get_token(self, *scopes, **kwargs) -> AccessToken:  # pylint:disable=unused-argument
        if not scopes:
            raise ValueError("No token scope provided.")
        name, key = self._credential.named_key
        return _generate_sas_token(scopes[0], name, key)


class EventhubAzureSasTokenCredentialAsync(object):
    """The shared access token credential used for authentication
    when AzureSasCredential is provided.

    :param azure_sas_credential: The credential to be used for authentication.
    :type azure_sas_credential: ~azure.core.credentials.AzureSasCredential
    """

    def __init__(self, azure_sas_credential: AzureSasCredential) -> None:
        self._credential = azure_sas_credential
        self.token_type = b"servicebus.windows.net:sastoken"

    async def get_token(
        self, *scopes: str, **kwargs: Any  # pylint:disable=unused-argument
    ) -> AccessToken:
        """
        This method is automatically called when token is about to expire.
        """
        signature, expiry = parse_sas_credential(self._credential)
        return AccessToken(signature, expiry)


class ClientBaseAsync(ClientBase):
    def __init__(
        self,
        fully_qualified_namespace: str,
        eventhub_name: str,
        credential: Union[
            "AsyncTokenCredential", AzureSasCredential, AzureNamedKeyCredential
        ],
        **kwargs: Any
    ) -> None:
        self._internal_kwargs = get_dict_with_loop_if_needed(kwargs.get("loop", None))
        if isinstance(credential, AzureSasCredential):
            self._credential = EventhubAzureSasTokenCredentialAsync(credential)  # type: ignore
        elif isinstance(credential, AzureNamedKeyCredential):
            self._credential = EventhubAzureNamedKeyTokenCredentialAsync(credential)  # type: ignore
        else:
            self._credential = credential  # type: ignore
        super(ClientBaseAsync, self).__init__(
            fully_qualified_namespace=fully_qualified_namespace,
            eventhub_name=eventhub_name,
            credential=self._credential,
            **kwargs
        )

    def __enter__(self):
        raise TypeError(
            "Asynchronous client must be opened with async context manager."
        )

    @staticmethod
    def _from_connection_string(conn_str: str, **kwargs) -> Dict[str, Any]:
        host, policy, key, entity, token, token_expiry = _parse_conn_str(
            conn_str, **kwargs
        )
        kwargs["fully_qualified_namespace"] = host
        kwargs["eventhub_name"] = entity
        if token and token_expiry:
            kwargs["credential"] = EventHubSASTokenCredential(token, token_expiry)
        elif policy and key:
            kwargs["credential"] = EventHubSharedKeyCredential(policy, key)
        return kwargs

    async def _create_auth_async(self) -> JWTTokenAuthAsync:
        """
        Create an ~uamqp.authentication.SASTokenAuthAsync instance to authenticate
        the session.

        """
        try:
            # ignore mypy's warning because token_type is Optional
            token_type = self._credential.token_type  # type: ignore
        except AttributeError:
            token_type = b"jwt"
        if token_type == b"servicebus.windows.net:sastoken":
            return JWTTokenAuthAsync(
                self._auth_uri,
                self._auth_uri,
                functools.partial(self._credential.get_token, self._auth_uri),
            )
        return JWTTokenAuthAsync(
            self._auth_uri,
            self._auth_uri,
            functools.partial(self._credential.get_token, JWT_TOKEN_SCOPE),
            token_type=token_type,
            timeout=self._config.auth_timeout,
            http_proxy=self._config.http_proxy,
            transport_type=self._config.transport_type,
            custom_endpoint_hostname=self._config.custom_endpoint_hostname,
            port=self._config.connection_port,
            verify=self._config.connection_verify,
        )

    async def _close_connection_async(self) -> None:
        pass

    async def _backoff_async(
        self,
        retried_times: int,
        last_exception: Exception,
        timeout_time: Optional[float] = None,
        entity_name: Optional[str] = None,
    ) -> None:
        entity_name = entity_name or self._container_id
        backoff = _get_backoff_time(
            self._config.retry_mode,
            self._config.backoff_factor,
            self._config.backoff_max,
            retried_times,
        )
        if backoff <= self._config.backoff_max and (
            timeout_time is None or time.time() + backoff <= timeout_time
        ):  # pylint:disable=no-else-return
            await asyncio.sleep(backoff, **self._internal_kwargs)
            _LOGGER.info(
                "%r has an exception (%r). Retrying...",
                format(entity_name),
                last_exception,
            )
        else:
            _LOGGER.info(
                "%r operation has timed out. Last exception before timeout is (%r)",
                entity_name,
                last_exception,
            )
            raise last_exception

    async def _management_request_async(self, mgmt_msg: Message, op_type: bytes) -> Any:
        retried_times = 0
        last_exception = None
        while retried_times <= self._config.max_retries:
            mgmt_auth = await self._create_auth_async()
            hostname = self._address.hostname
            custom_endpoint_address = "{}:{}".format(self._config.custom_endpoint_hostname, self._config.connection_port)
            if self._config.transport_type.name == 'AmqpOverWebsocket':
                hostname += '/$servicebus/websocket/'
                if custom_endpoint_address:
                    custom_endpoint_address += '/$servicebus/websocket/'
            mgmt_client = AMQPClientAsync(
                hostname,
                auth=mgmt_auth,
                debug=self._config.network_tracing,
                transport_type=self._config.transport_type,
                http_proxy=self._config.http_proxy,
                custom_endpoint_address=custom_endpoint_address,
                connection_verify=self._config.connection_verify
            )
            try:
                await mgmt_client.open_async()
                while not (await mgmt_client.client_ready_async()):
                    await asyncio.sleep(0.05)
                mgmt_msg.application_properties["security_token"] = await mgmt_auth.get_token()
                response = await mgmt_client.mgmt_request_async(
                    mgmt_msg,
                    operation=READ_OPERATION.decode(),
                    operation_type=op_type.decode(),
                    status_code_field=MGMT_STATUS_CODE,
                    description_fields=MGMT_STATUS_DESC,
                )
                status_code = int(response.application_properties[MGMT_STATUS_CODE])
                description = response.application_properties.get(
                    MGMT_STATUS_DESC
                )  # type: Optional[Union[str, bytes]]
                if description and isinstance(description, six.binary_type):
                    description = description.decode("utf-8")
                if status_code < 400:
                    return response
                if status_code in [401]:
                    raise errors.AuthenticationException(
                        errors.ErrorCondition.UnauthorizedAccess,
                        description="Management authentication failed. Status code: {}, Description: {!r}".format(
                            status_code,
                            description
                        )
                    )
                if status_code in [404]:
                    raise errors.AMQPConnectionError(
                        errors.ErrorCondition.NotFound,
                        description="Management connection failed. Status code: {}, Description: {!r}".format(
                            status_code,
                            description
                        )
                    )
                raise errors.AMQPConnectionError(
                    errors.ErrorCondition.UnknownError,
                    description="Management operation failed. Status code: {}, Description: {!r}".format(
                        status_code,
                        description
                    )
                )
            except asyncio.CancelledError:  # pylint: disable=try-except-raise
                raise
            except Exception as exception:  # pylint:disable=broad-except
                last_exception = await _handle_exception(exception, self)
                await self._backoff_async(
                    retried_times=retried_times, last_exception=last_exception
                )
                retried_times += 1
                if retried_times > self._config.max_retries:
                    _LOGGER.info(
                        "%r returns an exception %r", self._container_id, last_exception
                    )
                    raise last_exception
            finally:
                await mgmt_client.close_async()

    async def _get_eventhub_properties_async(self) -> Dict[str, Any]:
        mgmt_msg = Message(application_properties={"name": self.eventhub_name})
        response = await self._management_request_async(
            mgmt_msg, op_type=MGMT_OPERATION
        )
        output = {}
        eh_info = response.value  # type: Dict[bytes, Any]
        if eh_info:
            output["eventhub_name"] = eh_info[b"name"].decode("utf-8")
            output["created_at"] = utc_from_timestamp(
                float(eh_info[b"created_at"]) / 1000
            )
            output["partition_ids"] = [
                p.decode("utf-8") for p in eh_info[b"partition_ids"]
            ]
        return output

    async def _get_partition_ids_async(self) -> List[str]:
        return (await self._get_eventhub_properties_async())["partition_ids"]

    async def _get_partition_properties_async(
        self, partition_id: str
    ) -> Dict[str, Any]:
        mgmt_msg = Message(
            application_properties={
                "name": self.eventhub_name,
                "partition": partition_id,
            }
        )
        response = await self._management_request_async(
            mgmt_msg, op_type=MGMT_PARTITION_OPERATION
        )
        partition_info = response.value  # type: Dict[bytes, Union[bytes, int]]
        output = {}  # type: Dict[str, Any]
        if partition_info:
            output["eventhub_name"] = cast(bytes, partition_info[b"name"]).decode(
                "utf-8"
            )
            output["id"] = cast(bytes, partition_info[b"partition"]).decode("utf-8")
            output["beginning_sequence_number"] = cast(
                int, partition_info[b"begin_sequence_number"]
            )
            output["last_enqueued_sequence_number"] = cast(
                int, partition_info[b"last_enqueued_sequence_number"]
            )
            output["last_enqueued_offset"] = cast(
                bytes, partition_info[b"last_enqueued_offset"]
            ).decode("utf-8")
            output["is_empty"] = partition_info[b"is_partition_empty"]
            output["last_enqueued_time_utc"] = utc_from_timestamp(
                float(cast(int, partition_info[b"last_enqueued_time_utc"]) / 1000)
            )
        return output

    async def _close_async(self) -> None:
        pass


if TYPE_CHECKING:

    class AbstractConsumerProducer(Protocol):
        @property
        def _name(self):
            # type: () -> str
            """Name of the consumer or producer"""

        @_name.setter
        def _name(self, value):
            pass

        @property
        def _client(self):
            # type: () -> ClientBaseAsync
            """The instance of EventHubComsumerClient or EventHubProducerClient"""

        @_client.setter
        def _client(self, value):
            pass

        @property
        def _handler(self):
            # type: () -> AMQPClientAsync
            """The instance of SendClientAsync or ReceiveClientAsync"""

        @property
        def _internal_kwargs(self):
            # type: () -> dict
            """The dict with an event loop that users may pass in to wrap sync calls to async API.
            It's furthur passed to uamqp APIs
            """

        @_internal_kwargs.setter
        def _internal_kwargs(self, value):
            pass

        @property
        def running(self):
            # type: () -> bool
            """Whether the consumer or producer is running"""

        @running.setter
        def running(self, value):
            pass

        def _create_handler(self, auth: JWTTokenAuthAsync) -> None:
            pass

    _MIXIN_BASE = AbstractConsumerProducer
else:
    _MIXIN_BASE = object


class ConsumerProducerMixin(_MIXIN_BASE):
    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()

    def _check_closed(self) -> None:
        if self.closed:
            raise ClientClosedError(
                "{} has been closed. Please create a new one to handle event data.".format(
                    self._name
                )
            )

    async def _open(self) -> None:
        """
        Open the EventHubConsumer using the supplied connection.

        """
        # pylint: disable=protected-access,line-too-long
        if not self.running:
            if self._handler:
                await self._handler.close_async()
            auth = await self._client._create_auth_async()
            self._create_handler(auth)
            await self._handler.open_async()
            while not await self._handler.client_ready_async():
                await asyncio.sleep(0.05, **self._internal_kwargs)
            self._max_message_size_on_link = (
                self._handler._link.remote_max_message_size
                or constants.MAX_FRAME_SIZE_BYTES
            )
            self.running = True

    async def _close_handler_async(self) -> None:
        if self._handler:
            # close the link (shared connection) or connection (not shared)
            await self._handler.close_async()
        self.running = False

    async def _close_connection_async(self) -> None:
        await self._close_handler_async()
        await self._client._conn_manager_async.reset_connection_if_broken()  # pylint:disable=protected-access

    async def _handle_exception(self, exception: Exception) -> Exception:
        if not self.running and isinstance(exception, TimeoutError):
            exception = errors.AuthenticationException(
                errors.ErrorCondition.InternalError,
                description="Authorization timeout."
            )
        return await _handle_exception(exception, self)

    async def _do_retryable_operation(
        self,
        operation: Callable[..., Any],
        timeout: Optional[float] = None,
        **kwargs: Any
    ) -> Optional[Any]:
        # pylint:disable=protected-access,line-too-long
        timeout_time = (time.time() + timeout) if timeout else None
        retried_times = 0
        last_exception = kwargs.pop("last_exception", None)
        operation_need_param = kwargs.pop("operation_need_param", True)
        max_retries = self._client._config.max_retries

        while retried_times <= max_retries:
            try:
                if operation_need_param:
                    return await operation(
                        timeout_time=timeout_time,
                        last_exception=last_exception,
                        **kwargs
                    )
                return await operation()
            except asyncio.CancelledError:  # pylint: disable=try-except-raise
                raise
            except Exception as exception:  # pylint:disable=broad-except
                last_exception = await self._handle_exception(exception)
                await self._client._backoff_async(
                    retried_times=retried_times,
                    last_exception=last_exception,
                    timeout_time=timeout_time,
                    entity_name=self._name,
                )
                retried_times += 1
                if retried_times > max_retries:
                    _LOGGER.info(
                        "%r operation has exhausted retry. Last exception: %r.",
                        self._name,
                        last_exception,
                    )
                    raise last_exception
        return None

    async def close(self) -> None:
        """
        Close down the handler. If the handler has already closed,
        this will be a no op.
        """
        await self._close_handler_async()
        self.closed = True
