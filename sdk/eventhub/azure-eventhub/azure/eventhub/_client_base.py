# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
from __future__ import annotations

import logging
import uuid
import time
import functools
import collections
from typing import Any, Dict, Tuple, List, Optional, TYPE_CHECKING, cast, Union
from datetime import timedelta
from urllib.parse import urlparse
from typing_extensions import TypeAlias

from azure.core.credentials import (
    AccessToken,
    AzureSasCredential,
    AzureNamedKeyCredential,
)
from azure.core.utils import parse_connection_string as core_parse_connection_string
from azure.core.pipeline.policies import RetryMode

try:
    from ._transport._uamqp_transport import UamqpTransport
except ImportError:
    UamqpTransport = None  # type: ignore
from ._transport._pyamqp_transport import PyamqpTransport
from .exceptions import ClientClosedError
from ._configuration import Configuration
from ._utils import utc_from_timestamp, parse_sas_credential
from ._pyamqp.utils import generate_sas_token
from ._connection_manager import get_connection_manager
from ._constants import (
    CONTAINER_PREFIX,
    JWT_TOKEN_SCOPE,
    READ_OPERATION,
    MGMT_STATUS_CODE,
    MGMT_STATUS_DESC,
    MGMT_OPERATION,
    MGMT_PARTITION_OPERATION,
)

if TYPE_CHECKING:
    from azure.core.credentials import TokenCredential

    CredentialTypes: TypeAlias = Union[
        AzureSasCredential,
        AzureNamedKeyCredential,
        "EventHubSharedKeyCredential",
        TokenCredential,
    ]
    from ._consumer_client import EventHubConsumerClient
    from ._producer_client import EventHubProducerClient
    from ._transport._base import AmqpTransport

    try:
        from uamqp import Message as uamqp_Message
        from uamqp.authentication import JWTTokenAuth as uamqp_JWTTokenAuth
        from uamqp import ReceiveClient as uamqp_AMQPRecieveClient
        from uamqp import SendClient as uamqp_AMQPSendClient
    except ImportError:
        pass
    from ._pyamqp.message import Message
    from ._pyamqp.authentication import JWTTokenAuth
    from ._pyamqp import ReceiveClient as pyamqp_AMQPRecieveClient
    from ._pyamqp import SendClient as pyamqp_AMQPSendClient

_LOGGER = logging.getLogger(__name__)
_Address = collections.namedtuple("_Address", "hostname path")


def _parse_conn_str(
    conn_str: str,  # pylint:disable=unused-argument
    *,
    eventhub_name: Optional[str] = None,
    check_case: bool = False,
    **kwargs: Any,
) -> Tuple[str, Optional[str], Optional[str], str, Optional[str], Optional[int], bool]:
    endpoint = None
    shared_access_key_name = None
    shared_access_key = None
    entity_path: Optional[str] = None
    shared_access_signature: Optional[str] = None
    shared_access_signature_expiry = None
    use_emulator: Optional[str] = None
    conn_settings = core_parse_connection_string(conn_str, case_sensitive_keys=check_case)
    if check_case:
        shared_access_key = conn_settings.get("SharedAccessKey")
        shared_access_key_name = conn_settings.get("SharedAccessKeyName")
        endpoint = conn_settings.get("Endpoint")
        entity_path = conn_settings.get("EntityPath")
        # non case sensitive check when parsing connection string for internal use
        for key, value in conn_settings.items():
            # only sas check is non case sensitive for both conn str properties and internal use
            if key.lower() == "sharedaccesssignature":
                shared_access_signature = value
        use_emulator = conn_settings.get("UseDevelopmentEmulator")

    if not check_case:
        endpoint = conn_settings.get("endpoint") or conn_settings.get("hostname")
        if endpoint:
            endpoint = endpoint.rstrip("/")
        shared_access_key_name = conn_settings.get("sharedaccesskeyname")
        shared_access_key = conn_settings.get("sharedaccesskey")
        entity_path = conn_settings.get("entitypath")
        shared_access_signature = conn_settings.get("sharedaccesssignature")
        use_emulator = conn_settings.get("usedevelopmentemulator")

    if shared_access_signature:
        try:
            # Expiry can be stored in the "se=<timestamp>" clause of the token. ('&'-separated key-value pairs)
            shared_access_signature_expiry = int(shared_access_signature.split("se=")[1].split("&")[0])  # type: ignore
        except (
            IndexError,
            TypeError,
            ValueError,
        ):  # Fallback since technically expiry is optional.
            # An arbitrary, absurdly large number, since you can't renew.
            shared_access_signature_expiry = int(time.time() * 2)

    entity = cast(str, eventhub_name or entity_path)

    # check that endpoint is valid
    if not endpoint:
        raise ValueError("Connection string is either blank or malformed.")

    parsed = urlparse(endpoint)
    if not parsed.netloc:
        raise ValueError("Invalid Endpoint on the Connection String.")
    host = cast(str, parsed.netloc.strip())

    emulator = use_emulator == "true"

    if any([shared_access_key, shared_access_key_name]) and not all([shared_access_key, shared_access_key_name]):
        raise ValueError(
            "Invalid connection string. Should be in the format: "
            "Endpoint=sb://<FQDN>/;SharedAccessKeyName=<KeyName>;SharedAccessKey=<KeyValue>"
        )
    # Only connection string parser should check that only one of sas and shared access
    # key exists. For backwards compatibility, client construction should not have this check.
    if check_case and shared_access_signature and shared_access_key:
        raise ValueError("Only one of the SharedAccessKey or SharedAccessSignature must be present.")
    if not shared_access_signature and not shared_access_key:
        raise ValueError("At least one of the SharedAccessKey or SharedAccessSignature must be present.")

    return (
        host,
        str(shared_access_key_name) if shared_access_key_name else None,
        str(shared_access_key) if shared_access_key else None,
        entity,
        str(shared_access_signature) if shared_access_signature else None,
        shared_access_signature_expiry,
        emulator,
    )


def _generate_sas_token(uri: str, policy: str, key: str, expiry: Optional[timedelta] = None) -> AccessToken:
    """Create a shared access signature token as a string literal.

    :param str uri: The resource URI.
    :param str policy: The name of the shared access policy.
    :param str key: The shared access key.
    :param datetime.timedelta or None expiry: The time period that the signature is valid for. Default is 1 hour.
    :return: An AccessToken.
    :rtype: ~azure.core.credentials.AccessToken
    """
    if not expiry:
        expiry = timedelta(hours=1)  # Default to 1 hour.

    abs_expiry = int(time.time()) + expiry.seconds

    token = generate_sas_token(uri, policy, key, abs_expiry)
    return AccessToken(token=token, expires_on=abs_expiry)


def _build_uri(address: str, entity: str) -> str:
    parsed = urlparse(address)
    if parsed.path:
        return address
    if not entity:
        raise ValueError("No EventHub specified")
    address += "/" + str(entity)
    return address


def _get_backoff_time(retry_mode, backoff_factor, backoff_max, retried_times):
    if retry_mode == RetryMode.Fixed:
        backoff_value = backoff_factor
    else:
        backoff_value = backoff_factor * (2**retried_times)
    return min(backoff_max, backoff_value)


class EventHubSharedKeyCredential:
    """The shared access key credential used for authentication.

    :param str policy: The name of the shared access policy.
    :param str key: The shared access key.
    """

    def __init__(self, policy: str, key: str) -> None:
        self.policy = policy
        self.key = key
        self.token_type = b"servicebus.windows.net:sastoken"

    def get_token(self, *scopes: str, **kwargs: Any) -> AccessToken:  # pylint:disable=unused-argument
        if not scopes:
            raise ValueError("No token scope provided.")
        return _generate_sas_token(scopes[0], self.policy, self.key)


class EventhubAzureNamedKeyTokenCredential:
    """The named key credential used for authentication.

    :param credential: The AzureNamedKeyCredential that should be used.
    :type credential: ~azure.core.credentials.AzureNamedKeyCredential
    """

    def __init__(self, azure_named_key_credential: AzureNamedKeyCredential) -> None:
        self._credential = azure_named_key_credential
        self.token_type = b"servicebus.windows.net:sastoken"

    def get_token(self, *scopes: str, **kwargs: Any) -> AccessToken:  # pylint:disable=unused-argument
        if not scopes:
            raise ValueError("No token scope provided.")
        name, key = self._credential.named_key
        return _generate_sas_token(scopes[0], name, key)


class EventHubSASTokenCredential:
    """The shared access token credential used for authentication.

    :param str token: The shared access token string
    :param int expiry: The epoch timestamp
    """

    def __init__(self, token: str, expiry: int) -> None:
        """
        :param str token: The shared access token string
        :param float expiry: The epoch timestamp
        """
        self.token = token
        self.expiry = expiry
        self.token_type = b"servicebus.windows.net:sastoken"

    def get_token(self, *scopes: str, **kwargs: Any) -> AccessToken:  # pylint:disable=unused-argument
        """
        This method is automatically called when token is about to expire.

        :param str scopes: The list of scopes for which the token has access.
        :return: The access token.
        :rtype: ~azure.core.credentials.AccessToken
        """
        return AccessToken(self.token, self.expiry)


class EventhubAzureSasTokenCredential:
    """The shared access token credential used for authentication
    when AzureSasCredential is provided.

    :param azure_sas_credential: The credential to be used for authentication.
    :type azure_sas_credential: ~azure.core.credentials.AzureSasCredential
    """

    def __init__(self, azure_sas_credential: AzureSasCredential) -> None:
        """The shared access token credential used for authentication
         when AzureSasCredential is provided.

        :param azure_sas_credential: The credential to be used for authentication.
        :type azure_sas_credential: ~azure.core.credentials.AzureSasCredential
        """
        self._credential = azure_sas_credential
        self.token_type = b"servicebus.windows.net:sastoken"

    def get_token(self, *scopes: str, **kwargs: Any) -> AccessToken:  # pylint:disable=unused-argument
        """
        This method is automatically called when token is about to expire.

        :param str scopes: The scopes for the token request.
        :return: The access token.
        :rtype: ~azure.core.credentials.AccessToken
        """
        signature, expiry = parse_sas_credential(self._credential)
        return AccessToken(signature, cast(int, expiry))


class ClientBase:  # pylint:disable=too-many-instance-attributes
    def __init__(
        self,
        fully_qualified_namespace: str,
        eventhub_name: str,
        credential: "CredentialTypes",
        **kwargs: Any,
    ) -> None:
        uamqp_transport = kwargs.pop("uamqp_transport", False)
        if uamqp_transport and UamqpTransport is None:
            raise ValueError("To use the uAMQP transport, please install `uamqp>=1.6.0,<2.0.0`.")
        self._amqp_transport = kwargs.pop("amqp_transport", UamqpTransport if uamqp_transport else PyamqpTransport)

        self.eventhub_name = eventhub_name
        if not eventhub_name:
            raise ValueError("The eventhub name can not be None or empty.")
        path = "/" + eventhub_name if eventhub_name else ""
        self._address = _Address(hostname=fully_qualified_namespace, path=path)
        self._container_id = CONTAINER_PREFIX + str(uuid.uuid4())[:8]
        if isinstance(credential, AzureSasCredential):
            self._credential = EventhubAzureSasTokenCredential(credential)
        elif isinstance(credential, AzureNamedKeyCredential):
            self._credential = EventhubAzureNamedKeyTokenCredential(credential)  # type: ignore
        else:
            self._credential = credential  # type: ignore
        self._auto_reconnect = kwargs.get("auto_reconnect", True)
        self._auth_uri: str
        self._eventhub_auth_uri = f"sb://{self._address.hostname}{self._address.path}"
        self._config = Configuration(
            amqp_transport=self._amqp_transport,
            hostname=self._address.hostname,
            **kwargs,
        )
        self._debug = self._config.network_tracing
        kwargs["custom_endpoint_address"] = self._config.custom_endpoint_address
        self._conn_manager = get_connection_manager(amqp_transport=self._amqp_transport, **kwargs)
        self._idle_timeout = kwargs.get("idle_timeout", None)

    @staticmethod
    def _from_connection_string(conn_str: str, **kwargs: Any) -> Dict[str, Any]:
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

    def _create_auth(self, *, auth_uri: Optional[str] = None) -> Union["uamqp_JWTTokenAuth", JWTTokenAuth]:
        """
        Create an ~uamqp.authentication.SASTokenAuth instance
         to authenticate the session.

        :keyword auth_uri: The URI to authenticate with.
        :paramtype auth_uri: str or None

        :return: The auth for the session.
        :rtype: JWTTokenAuth or uamqp_JWTTokenAuth
        """
        # if auth_uri is not provided, use the default hub one
        entity_auth_uri = auth_uri if auth_uri else self._eventhub_auth_uri

        try:
            # ignore mypy's warning because token_type is Optional
            token_type = self._credential.token_type  # type: ignore
        except AttributeError:
            token_type = b"jwt"
        if token_type == b"servicebus.windows.net:sastoken":
            return self._amqp_transport.create_token_auth(
                entity_auth_uri,
                functools.partial(self._credential.get_token, entity_auth_uri),
                token_type=token_type,
                config=self._config,
                update_token=True,
            )
        return self._amqp_transport.create_token_auth(
            entity_auth_uri,
            functools.partial(self._credential.get_token, JWT_TOKEN_SCOPE),
            token_type=token_type,
            config=self._config,
            update_token=False,
        )

    def _close_connection(self) -> None:
        self._conn_manager.reset_connection_if_broken()

    def _backoff(
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
            time.sleep(backoff)
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

    def _management_request(  # pylint:disable=inconsistent-return-statements
        self, mgmt_msg: Union[uamqp_Message, Message], op_type: bytes
    ) -> Any:
        retried_times = 0
        last_exception = None
        while retried_times <= self._config.max_retries:
            mgmt_auth = self._create_auth()
            mgmt_client = self._amqp_transport.create_mgmt_client(
                self._address, mgmt_auth=mgmt_auth, config=self._config
            )
            try:
                conn = self._conn_manager.get_connection(
                    endpoint=self._address.hostname, auth=mgmt_auth
                )
                mgmt_client.open(connection=conn)
                while not mgmt_client.client_ready():
                    time.sleep(0.05)

                cast(Dict[Union[str, bytes], Any], mgmt_msg.application_properties)["security_token"] = (
                    self._amqp_transport.get_updated_token(mgmt_auth)
                )
                status_code, description, response = self._amqp_transport.mgmt_client_request(
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
            except Exception as exception:  # pylint: disable=broad-except
                # If optional dependency is not installed, do not retry.
                if isinstance(exception, ImportError):
                    raise exception
                # is_consumer=True passed in here, ALTHOUGH this method is shared by the producer and consumer.
                # is_consumer will only be checked if FileNotFoundError is raised by self.mgmt_client.open() due to
                # invalid/non-existent connection_verify filepath. The producer will encounter the FileNotFoundError
                # when opening the SendClient, so is_consumer=True will not be passed to amqp_transport.handle_exception
                # there. This is for uamqp exception parity, which raises FileNotFoundError in the consumer and
                # EventHubError in the producer. TODO: Remove `is_consumer` kwarg when resolving issue #27128.
                last_exception = self._amqp_transport._handle_exception(  # pylint: disable=protected-access
                    exception, self, is_consumer=True
                )
                self._backoff(retried_times=retried_times, last_exception=last_exception)
                retried_times += 1
                if retried_times > self._config.max_retries:
                    _LOGGER.info("%r returns an exception %r", self._container_id, last_exception)
                    raise last_exception from None
            finally:
                mgmt_client.close()

    def _get_eventhub_properties(self) -> Dict[str, Any]:
        mgmt_msg = self._amqp_transport.build_message(application_properties={"name": self.eventhub_name})
        response = self._management_request(mgmt_msg, op_type=MGMT_OPERATION)
        output = {}
        eh_info: Dict[bytes, Any] = response.value
        if eh_info:
            output["eventhub_name"] = eh_info[b"name"].decode("utf-8")
            output["created_at"] = utc_from_timestamp(float(eh_info[b"created_at"]) / 1000)
            output["partition_ids"] = [p.decode("utf-8") for p in eh_info[b"partition_ids"]]
        return output

    def _get_partition_ids(self) -> List[str]:
        return self._get_eventhub_properties()["partition_ids"]

    def _get_partition_properties(self, partition_id: str) -> Dict[str, Any]:
        mgmt_msg = self._amqp_transport.build_message(
            application_properties={
                "name": self.eventhub_name,
                "partition": partition_id,
            }
        )
        response = self._management_request(mgmt_msg, op_type=MGMT_PARTITION_OPERATION)
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

    def _close(self) -> None:
        self._conn_manager.close_connection()


class ConsumerProducerMixin:

    def __init__(self) -> None:
        self._handler: Union[
            uamqp_AMQPRecieveClient, pyamqp_AMQPRecieveClient, uamqp_AMQPSendClient, pyamqp_AMQPSendClient
        ]
        self._client: Union[EventHubConsumerClient, EventHubProducerClient]
        self._amqp_transport: "AmqpTransport"
        self._max_message_size_on_link: Optional[int] = None

    def __enter__(self) -> ConsumerProducerMixin:
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        self.close()

    def _create_handler(self, auth):
        pass

    def _check_closed(self):
        if self.closed:
            raise ClientClosedError(f"{self._name} has been closed. Please create a new one to handle event data.")

    def _open(self) -> bool:
        """Open the EventHubConsumer/EventHubProducer using the supplied connection.

        :return: Whether the EventHubConsumer/EventHubProducer is ready to use.
        :rtype: bool
        """
        # pylint: disable=protected-access
        if not self.running:
            if self._handler:
                self._handler.close()
            auth = self._client._create_auth(auth_uri=self._client._auth_uri)
            self._create_handler(auth)
            conn = self._client._conn_manager.get_connection(  # pylint: disable=protected-access
                endpoint=self._client._address.hostname, auth=auth
            )
            self._handler.open(connection=conn)
            while not self._handler.client_ready():
                time.sleep(0.05)
            self._max_message_size_on_link = (
                self._amqp_transport.get_remote_max_message_size(self._handler)
                or self._amqp_transport.MAX_MESSAGE_LENGTH_BYTES
            )
            self.running: bool = True
            return True
        return False

    def _close_handler(self) -> None:
        if self._handler:
            self._handler.close()  # close the link (sharing connection) or connection (not sharing)
        self.running = False

    def _close_connection(self):
        self._close_handler()
        self._client._conn_manager.reset_connection_if_broken()  # pylint: disable=protected-access

    def _handle_exception(self, exception, *, is_consumer=False):
        exception = self._amqp_transport.check_timeout_exception(self, exception)
        return self._amqp_transport._handle_exception(  # pylint: disable=protected-access
            exception, self, is_consumer=is_consumer
        )

    def _do_retryable_operation(  # pylint:disable=inconsistent-return-statements
        self, operation, timeout=None, **kwargs
    ):
        # pylint:disable=protected-access
        timeout_time = (time.time() + timeout) if timeout else None
        retried_times = 0
        last_exception = kwargs.pop("last_exception", None)
        operation_need_param = kwargs.pop("operation_need_param", True)
        max_retries = self._client._config.max_retries  # pylint:disable=protected-access

        while retried_times <= max_retries:
            try:
                if operation_need_param:
                    return operation(
                        timeout_time=timeout_time,
                        last_exception=last_exception,
                        **kwargs,
                    )
                return operation()
            except Exception as exception:  # pylint:disable=broad-except
                # If optional dependency is not installed, do not retry.
                if isinstance(exception, ImportError):
                    raise exception
                last_exception = self._handle_exception(exception)
                self._client._backoff(
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

    def close(self) -> None:
        """
        Close down the handler. If the handler has already closed,
        this will be a no op.
        """
        self._close_handler()
        self.closed = True
