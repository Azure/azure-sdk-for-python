# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
from __future__ import annotations

import logging
import asyncio
import time
import functools
from typing import TYPE_CHECKING, Any, Dict, List, Callable, Optional, Union, cast

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
from .._utils import utc_from_timestamp, parse_sas_credential
from ..exceptions import ClientClosedError
from .._constants import (
    JWT_TOKEN_SCOPE,
    MGMT_OPERATION,
    MGMT_PARTITION_OPERATION,
    MGMT_STATUS_CODE,
    MGMT_STATUS_DESC,
    READ_OPERATION,
)
from ._async_utils import get_dict_with_loop_if_needed
from ._connection_manager_async import get_connection_manager

try:
    from ._transport._uamqp_transport_async import UamqpTransportAsync
except ImportError:
    UamqpTransportAsync = None  # type: ignore
from ._transport._pyamqp_transport_async import PyamqpTransportAsync

if TYPE_CHECKING:
    from .._pyamqp.message import Message
    from .._pyamqp.aio import AMQPClientAsync
    from .._pyamqp.aio._authentication_async import JWTTokenAuthAsync

    try:
        from uamqp import (
            Message as uamqp_Message,
            AMQPClientAsync as uamqp_AMQPClientAsync,
        )
        from uamqp.authentication import JWTTokenAsync as uamqp_JWTTokenAsync
    except ImportError:
        uamqp_Message = None
        uamqp_AMQPClientAsync = None
        uamqp_JWTTokenAsync = None
    from azure.core.credentials_async import AsyncTokenCredential

    try:
        from typing_extensions import TypeAlias, Protocol
    except ImportError:
        Protocol = object  # type: ignore

    CredentialTypes: TypeAlias = Union[
        "EventHubSharedKeyCredential",
        AsyncTokenCredential,
        AzureSasCredential,
        AzureNamedKeyCredential,
    ]

    class AbstractConsumerProducer(Protocol):
        @property
        def _name(self) -> str:
            """Name of the consumer or producer"""

        @_name.setter
        def _name(self, value):
            pass

        @property
        def _client(self) -> ClientBaseAsync:
            """The instance of EventHubComsumerClient or EventHubProducerClient"""

        @_client.setter
        def _client(self, value):
            pass

        @property
        def _handler(self) -> Union["uamqp_AMQPClientAsync", AMQPClientAsync]:
            """The instance of SendClientAsync or ReceiveClientAsync"""

        @property
        def _internal_kwargs(self) -> Dict[Any, Any]:
            """The dict with an event loop that users may pass in to wrap sync calls to async API.
            It's furthur passed to uamqp APIs
            """

        @_internal_kwargs.setter
        def _internal_kwargs(self, value):
            pass

        @property
        def running(self) -> bool:
            """Whether the consumer or producer is running"""

        @running.setter
        def running(self, value: bool) -> None:
            pass

        def _create_handler(self, auth: Union["uamqp_JWTTokenAsync", JWTTokenAuthAsync]) -> None:
            pass

    _MIXIN_BASE = AbstractConsumerProducer
else:
    _MIXIN_BASE = object


_LOGGER = logging.getLogger(__name__)


class EventHubSharedKeyCredential:
    """The shared access key credential used for authentication.

    :param str policy: The name of the shared access policy.
    :param str key: The shared access key.
    """

    def __init__(self, policy: str, key: str):
        self.policy = policy
        self.key = key
        self.token_type = b"servicebus.windows.net:sastoken"

    async def get_token(self, *scopes: str, **kwargs: Any) -> AccessToken:  # pylint:disable=unused-argument
        if not scopes:
            raise ValueError("No token scope provided.")
        return _generate_sas_token(scopes[0], self.policy, self.key)


class EventHubSASTokenCredential:
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

    async def get_token(self, *scopes: str, **kwargs: Any) -> AccessToken:  # pylint:disable=unused-argument
        """
        This method is automatically called when token is about to expire.

        :param str scopes: The list of scopes for which the token has access.
        :return: The token object
        :rtype: ~azure.core.credentials.AccessToken
        """
        return AccessToken(self.token, self.expiry)


class EventhubAzureNamedKeyTokenCredentialAsync:  # pylint: disable=name-too-long
    """The named key credential used for authentication.

    :param credential: The AzureNamedKeyCredential that should be used.
    :type credential: ~azure.core.credentials.AzureNamedKeyCredential
    """

    def __init__(self, azure_named_key_credential: AzureNamedKeyCredential) -> None:
        self._credential: AzureNamedKeyCredential = azure_named_key_credential
        self.token_type: bytes = b"servicebus.windows.net:sastoken"

    async def get_token(self, *scopes, **kwargs) -> AccessToken:  # pylint:disable=unused-argument
        if not scopes:
            raise ValueError("No token scope provided.")
        name, key = self._credential.named_key
        return _generate_sas_token(scopes[0], name, key)


class EventhubAzureSasTokenCredentialAsync:
    """The shared access token credential used for authentication
    when AzureSasCredential is provided.

    :param azure_sas_credential: The credential to be used for authentication.
    :type azure_sas_credential: ~azure.core.credentials.AzureSasCredential
    """

    def __init__(self, azure_sas_credential: AzureSasCredential) -> None:
        self._credential = azure_sas_credential
        self.token_type = b"servicebus.windows.net:sastoken"

    async def get_token(self, *scopes: str, **kwargs: Any) -> AccessToken:  # pylint:disable=unused-argument
        """
        This method is automatically called when token is about to expire.

        :param str scopes: The list of scopes for which the token has access.
        :return: The access token.
        :rtype: ~azure.core.credentials.AccessToken
        """
        signature, expiry = parse_sas_credential(self._credential)
        return AccessToken(signature, cast(int, expiry))


class ClientBaseAsync(ClientBase):
    def __init__(
        self, fully_qualified_namespace: str, eventhub_name: str, credential: "CredentialTypes", **kwargs: Any
    ) -> None:
        self._internal_kwargs = get_dict_with_loop_if_needed(kwargs.get("loop", None))
        uamqp_transport = kwargs.get("uamqp_transport", False)
        if uamqp_transport and UamqpTransportAsync is None:
            raise ValueError("To use the uAMQP transport, please install `uamqp>=1.6.0,<2.0.0`.")
        self._amqp_transport = UamqpTransportAsync if uamqp_transport else PyamqpTransportAsync
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
            amqp_transport=self._amqp_transport,
            **kwargs,
        )
        kwargs["custom_endpoint_address"] = self._config.custom_endpoint_address
        self._conn_manager_async = get_connection_manager(amqp_transport=self._amqp_transport, **kwargs)

    def __enter__(self) -> None:
        raise TypeError("Asynchronous client must be opened with async context manager.")

    @staticmethod
    def _from_connection_string(conn_str: str, **kwargs) -> Dict[str, Any]:
        host, policy, key, entity, token, token_expiry, emulator = _parse_conn_str(conn_str, **kwargs)
        kwargs["fully_qualified_namespace"] = host
        kwargs["eventhub_name"] = entity
        # Check if emulator is in use, unset tls if it is
        if emulator:
            kwargs["use_tls"] = False
        if token and token_expiry:
            kwargs["credential"] = EventHubSASTokenCredential(token, token_expiry)
        elif policy and key:
            kwargs["credential"] = EventHubSharedKeyCredential(policy, key)
        return kwargs

    async def _create_auth_async(
        self, *, auth_uri: Optional[str] = None
    ) -> Union["uamqp_JWTTokenAsync", JWTTokenAuthAsync]:
        """
        Create an ~uamqp.authentication.SASTokenAuthAsync instance to authenticate
        the session.

        :keyword auth_uri: The URI to authenticate with.
        :paramtype auth_uri: str or None

        :return: A JWTTokenAuthAsync instance to authenticate the session.
        :rtype: ~uamqp.authentication.JWTTokenAsync or JWTTokenAuthAsync
        """
        # if auth_uri is not provided, use the default hub one
        entity_auth_uri = auth_uri if auth_uri else self._eventhub_auth_uri

        try:
            # ignore mypy's warning because token_type is Optional
            token_type = self._credential.token_type  # type: ignore
        except AttributeError:
            token_type = b"jwt"
        if token_type == b"servicebus.windows.net:sastoken":
            return await self._amqp_transport.create_token_auth_async(
                entity_auth_uri,
                functools.partial(self._credential.get_token, entity_auth_uri),
                token_type=token_type,
                config=self._config,
                update_token=True,
            )
        return await self._amqp_transport.create_token_auth_async(
            entity_auth_uri,
            functools.partial(self._credential.get_token, JWT_TOKEN_SCOPE),
            token_type=token_type,
            config=self._config,
            update_token=False,
        )

    async def _close_connection_async(self) -> None:
        await self._conn_manager_async.reset_connection_if_broken()

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
        ):
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

    async def _management_request_async(self, mgmt_msg: Union[Message, uamqp_Message], op_type: bytes) -> Any:
        retried_times = 0
        last_exception = None
        while retried_times <= self._config.max_retries:
            mgmt_auth = await self._create_auth_async()
            mgmt_client = self._amqp_transport.create_mgmt_client(
                self._address, mgmt_auth=mgmt_auth, config=self._config
            )
            try:
                conn = await self._conn_manager_async.get_connection(endpoint=self._address.hostname, auth=mgmt_auth)
                await mgmt_client.open_async(connection=conn)
                while not await mgmt_client.client_ready_async():
                    await asyncio.sleep(0.05)
                cast(Dict[Union[str, bytes], Any], mgmt_msg.application_properties)["security_token"] = (
                    await self._amqp_transport.get_updated_token_async(mgmt_auth)
                )
                status_code, description, response = await self._amqp_transport.mgmt_client_request_async(
                    mgmt_client,
                    mgmt_msg,
                    operation=READ_OPERATION,
                    operation_type=op_type,
                    status_code_field=MGMT_STATUS_CODE,
                    description_fields=MGMT_STATUS_DESC,
                )
                status_code = int(status_code)
                if description and isinstance(description, bytes):
                    description = description.decode("utf-8")
                if status_code < 400:
                    return response
                raise self._amqp_transport.get_error(status_code, description)
            except asyncio.CancelledError:  # pylint: disable=try-except-raise
                raise
            except Exception as exception:  # pylint:disable=broad-except
                # If optional dependency is not installed, do not retry.
                if isinstance(exception, ImportError):
                    raise exception
                # is_consumer=True passed in here, ALTHOUGH this method is shared by the producer and consumer.
                # is_consumer will only be checked if FileNotFoundError is raised by self.mgmt_client.open() due to
                # invalid/non-existent connection_verify filepath. The producer will encounter the FileNotFoundError
                # when opening the SendClient, so is_consumer=True will not be passed to amqp_transport.handle_exception
                # there. This is for uamqp exception parity, which raises FileNotFoundError in the consumer and
                # EventHubError in the producer. TODO: Remove `is_consumer` kwarg when resolving issue #27128.
                last_exception = await self._amqp_transport._handle_exception_async(  # pylint: disable=protected-access
                    exception, self, is_consumer=True
                )
                await self._backoff_async(retried_times=retried_times, last_exception=last_exception)
                retried_times += 1
                if retried_times > self._config.max_retries:
                    _LOGGER.info("%r returns an exception %r", self._container_id, last_exception)
                    raise last_exception from None
            finally:
                await mgmt_client.close_async()

    async def _get_eventhub_properties_async(self) -> Dict[str, Any]:
        mgmt_msg = self._amqp_transport.build_message(application_properties={"name": self.eventhub_name})
        response = await self._management_request_async(mgmt_msg, op_type=MGMT_OPERATION)
        output = {}
        eh_info: Dict[bytes, Any] = response.value
        if eh_info:
            output["eventhub_name"] = eh_info[b"name"].decode("utf-8")
            output["created_at"] = utc_from_timestamp(float(eh_info[b"created_at"]) / 1000)
            output["partition_ids"] = [p.decode("utf-8") for p in eh_info[b"partition_ids"]]
        return output

    async def _get_partition_ids_async(self) -> List[str]:
        return (await self._get_eventhub_properties_async())["partition_ids"]

    async def _get_partition_properties_async(self, partition_id: str) -> Dict[str, Any]:
        mgmt_msg = self._amqp_transport.build_message(
            application_properties={
                "name": self.eventhub_name,
                "partition": partition_id,
            }
        )
        response = await self._management_request_async(mgmt_msg, op_type=MGMT_PARTITION_OPERATION)
        partition_info: Dict[bytes, Union[bytes, int]] = response.value
        output: Dict[str, Any] = {}
        if partition_info:
            output["eventhub_name"] = cast(bytes, partition_info[b"name"]).decode("utf-8")
            output["id"] = cast(bytes, partition_info[b"partition"]).decode("utf-8")
            output["beginning_sequence_number"] = cast(int, partition_info[b"begin_sequence_number"])
            output["last_enqueued_sequence_number"] = cast(int, partition_info[b"last_enqueued_sequence_number"])
            output["last_enqueued_offset"] = cast(bytes, partition_info[b"last_enqueued_offset"]).decode("utf-8")
            output["is_empty"] = partition_info[b"is_partition_empty"]
            output["last_enqueued_time_utc"] = utc_from_timestamp(
                float(cast(int, partition_info[b"last_enqueued_time_utc"]) / 1000)
            )
        return output

    async def _close_async(self) -> None:
        await self._conn_manager_async.close_connection()


class ConsumerProducerMixin(_MIXIN_BASE):
    async def __aenter__(self) -> ConsumerProducerMixin:
        return self

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        await self.close()

    def _check_closed(self) -> None:
        if self.closed:
            raise ClientClosedError(
                "{} has been closed. Please create a new one to handle event data.".format(self._name)
            )

    async def _open(self) -> None:
        """
        Open the EventHubConsumer using the supplied connection.

        """
        # pylint: disable=protected-access
        if not self.running:
            if self._handler:
                await self._handler.close_async()
            auth = await self._client._create_auth_async(auth_uri=self._client._auth_uri)
            self._create_handler(auth)
            conn = await self._client._conn_manager_async.get_connection(
                endpoint=self._client._address.hostname, auth=auth
            )
            await self._handler.open_async(connection=conn)
            while not await self._handler.client_ready_async():
                await asyncio.sleep(0.05, **self._internal_kwargs)
            # pylint: disable=protected-access
            self._max_message_size_on_link = (
                self._client._amqp_transport.get_remote_max_message_size(self._handler)
                or self._client._amqp_transport.MAX_MESSAGE_LENGTH_BYTES
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

    async def _handle_exception(self, exception: Exception, *, is_consumer: bool = False) -> Exception:
        # pylint: disable=protected-access
        exception = self._client._amqp_transport.check_timeout_exception(self, exception)
        return await self._client._amqp_transport._handle_exception_async(exception, self, is_consumer=is_consumer)

    async def _do_retryable_operation(
        self, operation: Callable[..., Any], timeout: Optional[float] = None, **kwargs: Any
    ) -> Optional[Any]:
        # pylint:disable=protected-access
        timeout_time = (time.time() + timeout) if timeout else None
        retried_times = 0
        last_exception = kwargs.pop("last_exception", None)
        operation_need_param = kwargs.pop("operation_need_param", True)
        max_retries = self._client._config.max_retries

        while retried_times <= max_retries:
            try:
                if operation_need_param:
                    return await operation(timeout_time=timeout_time, last_exception=last_exception, **kwargs)
                return await operation()
            except asyncio.CancelledError:  # pylint: disable=try-except-raise
                raise
            except Exception as exception:  # pylint:disable=broad-except
                # If optional dependency is not installed, do not retry.
                if isinstance(exception, ImportError):
                    raise exception
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
                    raise last_exception from None
        return None

    async def close(self) -> None:
        """
        Close down the handler. If the handler has already closed,
        this will be a no op.
        """
        await self._close_handler_async()
        self.closed = True
