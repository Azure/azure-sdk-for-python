# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
from __future__ import unicode_literals

import logging
import uuid
import time
import functools
import collections
from typing import Any, Dict, Tuple, List, Optional, TYPE_CHECKING, cast, Union
from datetime import timedelta
from urllib.parse import urlparse
import six

from azure.core.credentials import (
    AccessToken,
    AzureSasCredential,
    AzureNamedKeyCredential,
)
from azure.core.utils import parse_connection_string as core_parse_connection_string
from azure.core.pipeline.policies import RetryMode


from ._transport._uamqp_transport import UamqpTransport
from ._transport._pyamqp_transport import PyamqpTransport
from .exceptions import ClientClosedError
from ._configuration import Configuration
from ._utils import utc_from_timestamp, parse_sas_credential
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
from ._pyamqp import utils as pyamqp_utils, error as errors

if TYPE_CHECKING:
    from azure.core.credentials import TokenCredential
    try:
        from uamqp import Message as uamqp_Message
        from uamqp.authentication import JWTTokenAuth as uamqp_JWTTokenAuth
        from ._transport._uamqp_transport import (
            EventHubSharedKeyCredential as uamqp_EventHubSharedKeyCredential,
        )
    except ImportError:
        uamqp_Message = None
        uamqp_JWTTokenAuth = None
        uamqp_EventHubSharedKeyCredential = None
    from ._pyamqp.message import Message
    from ._pyamqp.authentication import JWTTokenAuth

    CredentialTypes = Union[
        AzureSasCredential,
        AzureNamedKeyCredential,
        uamqp_EventHubSharedKeyCredential,
        "EventHubSharedKeyCredential",
        TokenCredential,
    ]

_LOGGER = logging.getLogger(__name__)
_Address = collections.namedtuple("_Address", "hostname path")


def _parse_conn_str(conn_str, **kwargs):
    # type: (str, Any) -> Tuple[str, Optional[str], Optional[str], str, Optional[str], Optional[int]]
    endpoint = None
    shared_access_key_name = None
    shared_access_key = None
    entity_path = None  # type: Optional[str]
    shared_access_signature = None  # type: Optional[str]
    shared_access_signature_expiry = None
    eventhub_name = kwargs.pop("eventhub_name", None)  # type: Optional[str]
    check_case = kwargs.pop("check_case", False)  # type: bool
    conn_settings = core_parse_connection_string(
        conn_str, case_sensitive_keys=check_case
    )
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

    if not check_case:
        endpoint = conn_settings.get("endpoint") or conn_settings.get("hostname")
        if endpoint:
            endpoint = endpoint.rstrip("/")
        shared_access_key_name = conn_settings.get("sharedaccesskeyname")
        shared_access_key = conn_settings.get("sharedaccesskey")
        entity_path = conn_settings.get("entitypath")
        shared_access_signature = conn_settings.get("sharedaccesssignature")

    if shared_access_signature:
        try:
            # Expiry can be stored in the "se=<timestamp>" clause of the token. ('&'-separated key-value pairs)
            shared_access_signature_expiry = int(
                shared_access_signature.split("se=")[1].split("&")[0]  # type: ignore
            )
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

    if any([shared_access_key, shared_access_key_name]) and not all(
        [shared_access_key, shared_access_key_name]
    ):
        raise ValueError(
            "Invalid connection string. Should be in the format: "
            "Endpoint=sb://<FQDN>/;SharedAccessKeyName=<KeyName>;SharedAccessKey=<KeyValue>"
        )
    # Only connection string parser should check that only one of sas and shared access
    # key exists. For backwards compatibility, client construction should not have this check.
    if check_case and shared_access_signature and shared_access_key:
        raise ValueError(
            "Only one of the SharedAccessKey or SharedAccessSignature must be present."
        )
    if not shared_access_signature and not shared_access_key:
        raise ValueError(
            "At least one of the SharedAccessKey or SharedAccessSignature must be present."
        )

    return (
        host,
        str(shared_access_key_name) if shared_access_key_name else None,
        str(shared_access_key) if shared_access_key else None,
        entity,
        str(shared_access_signature) if shared_access_signature else None,
        shared_access_signature_expiry,
    )


def _generate_sas_token(uri, policy, key, expiry=None):
    # type: (str, str, str, Optional[timedelta]) -> AccessToken
    """Create a shared access signiture token as a string literal.
    :returns: SAS token as string literal.
    :rtype: str
    """
    if not expiry:
        expiry = timedelta(hours=1)  # Default to 1 hour.

    abs_expiry = int(time.time()) + expiry.seconds

    token = pyamqp_utils.generate_sas_token(uri, policy, key, abs_expiry).encode()
    return AccessToken(token=token, expires_on=abs_expiry)


def _build_uri(address, entity):
    # type: (str, Optional[str]) -> str
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


class EventHubSharedKeyCredential(object):
    """The shared access key credential used for authentication.

    :param str policy: The name of the shared access policy.
    :param str key: The shared access key.
    """

    def __init__(self, policy, key):
        # type: (str, str) -> None
        self.policy = policy
        self.key = key
        self.token_type = b"servicebus.windows.net:sastoken"

    def get_token(self, *scopes, **kwargs):  # pylint:disable=unused-argument
        # type: (str, Any) -> AccessToken
        if not scopes:
            raise ValueError("No token scope provided.")

        return _generate_sas_token(scopes[0], self.policy, self.key)


class EventhubAzureNamedKeyTokenCredential(object):
    """The named key credential used for authentication.

    :param credential: The AzureNamedKeyCredential that should be used.
    :type credential: ~azure.core.credentials.AzureNamedKeyCredential
    """

    def __init__(self, azure_named_key_credential):
        # type: (AzureNamedKeyCredential) -> None
        self._credential = azure_named_key_credential
        self.token_type = b"servicebus.windows.net:sastoken"

    def get_token(self, *scopes, **kwargs):  # pylint:disable=unused-argument
        # type: (str, Any) -> AccessToken
        if not scopes:
            raise ValueError("No token scope provided.")
        name, key = self._credential.named_key
        return _generate_sas_token(scopes[0], name, key)


class EventHubSASTokenCredential(object):
    """The shared access token credential used for authentication.

    :param str token: The shared access token string
    :param int expiry: The epoch timestamp
    """

    def __init__(self, token, expiry):
        # type: (str, int) -> None
        """
        :param str token: The shared access token string
        :param float expiry: The epoch timestamp
        """
        self.token = token
        self.expiry = expiry
        self.token_type = b"servicebus.windows.net:sastoken"

    def get_token(self, *scopes, **kwargs):  # pylint:disable=unused-argument
        # type: (str, Any) -> AccessToken
        """
        This method is automatically called when token is about to expire.
        """
        return AccessToken(self.token, self.expiry)


class EventhubAzureSasTokenCredential(object):
    """The shared access token credential used for authentication
    when AzureSasCredential is provided.

    :param azure_sas_credential: The credential to be used for authentication.
    :type azure_sas_credential: ~azure.core.credentials.AzureSasCredential
    """

    def __init__(self, azure_sas_credential):
        # type: (AzureSasCredential) -> None
        """The shared access token credential used for authentication
         when AzureSasCredential is provided.

        :param azure_sas_credential: The credential to be used for authentication.
        :type azure_sas_credential: ~azure.core.credentials.AzureSasCredential
        """
        self._credential = azure_sas_credential
        self.token_type = b"servicebus.windows.net:sastoken"

    def get_token(self, *scopes, **kwargs):  # pylint:disable=unused-argument
        # type: (str, Any) -> AccessToken
        """
        This method is automatically called when token is about to expire.
        """
        signature, expiry = parse_sas_credential(self._credential)
        return AccessToken(signature, expiry)


class ClientBase(object):  # pylint:disable=too-many-instance-attributes
    def __init__(
        self,
        fully_qualified_namespace: str,
        eventhub_name: str,
        credential: CredentialTypes,
        **kwargs: Any,
    ) -> None:
        self._uamqp_transport = kwargs.pop("uamqp_transport", False)
        if not self._uamqp_transport:
            self._amqp_transport = PyamqpTransport()
        else:
            self._amqp_transport = UamqpTransport()

        self.eventhub_name = eventhub_name
        if not eventhub_name:
            raise ValueError("The eventhub name can not be None or empty.")
        path = "/" + eventhub_name if eventhub_name else ""
        self._address = _Address(hostname=fully_qualified_namespace, path=path)
        self._container_id = CONTAINER_PREFIX + str(uuid.uuid4())[:8]
        if isinstance(credential, AzureSasCredential):
            self._credential = EventhubAzureSasTokenCredential(credential)
        elif isinstance(credential, AzureNamedKeyCredential):
            self._credential = EventhubAzureNamedKeyTokenCredential(credential)
            # TODO: see if pyamqp generated token works for uamqp
            # if self._uamqp_transport:
            #    self._credential = UamqpTransport.create_named_key_token_credential(credential)  # type: ignore
            # else:
            #    raise NotImplementedError('pyamqp named key token credential')
        else:
            self._credential = credential  # type: ignore
        self._keep_alive = kwargs.get("keep_alive", 30)
        self._auto_reconnect = kwargs.get("auto_reconnect", True)
        self._auth_uri = f"sb://{self._address.hostname}{self._address.path}"
        self._config = Configuration(
            uamqp_transport=self._uamqp_transport,
            hostname=self._address.hostname,
            **kwargs,
        )
        self._debug = self._config.network_tracing
        self._conn_manager = get_connection_manager(**kwargs)
        self._idle_timeout = kwargs.get("idle_timeout", None)

    @staticmethod
    def _from_connection_string(conn_str, **kwargs):
        # type: (str, Any) -> Dict[str, Any]
        host, policy, key, entity, token, token_expiry = _parse_conn_str(
            conn_str, **kwargs
        )
        kwargs["fully_qualified_namespace"] = host
        kwargs["eventhub_name"] = entity
        if token and token_expiry:
            kwargs["credential"] = EventHubSASTokenCredential(token, token_expiry)
        elif policy and key:
            # TODO: see if pyamqp generated token works for uamqp. pyamqp by default here, else uamqp
            kwargs["credential"] = EventHubSharedKeyCredential(policy, key)
            # kwargs["credential"] = UamqpTransport.create_shared_key_credential(policy, key)
        return kwargs

    def _create_auth(self) -> Union["uamqp_JWTTokenAuth", "JWTTokenAuth"]:
        """
        Create an ~uamqp.authentication.SASTokenAuth or pyamqp.JWTTokenAuth instance
         to authenticate the session.
        """
        try:
            # ignore mypy's warning because token_type is Optional
            token_type = self._credential.token_type  # type: ignore
        except AttributeError:
            token_type = b"jwt"
        if token_type == b"servicebus.windows.net:sastoken":
            return self._amqp_transport.create_token_auth(
                self._auth_uri,
                functools.partial(self._credential.get_token, self._auth_uri),
                token_type=token_type,
                config=self._config,
                update_token=True,  # TODO: discarded by pyamqp transport
            )
        return self._amqp_transport.create_token_auth(
            self._auth_uri,
            functools.partial(self._credential.get_token, JWT_TOKEN_SCOPE),
            token_type=token_type,
            config=self._config,
            update_token=False,
        )

    def _close_connection(self):
        # type: () -> None
        self._conn_manager.reset_connection_if_broken()

    def _backoff(
        self, retried_times, last_exception, timeout_time=None, entity_name=None
    ):
        # type: (int, Exception, Optional[int], Optional[str]) -> None
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

    def _management_request(
        self, mgmt_msg: Union["uamqp_Message", "Message"], op_type: bytes
    ) -> Any:
        # pylint:disable=assignment-from-none
        retried_times = 0
        last_exception = None
        while retried_times <= self._config.max_retries:
            mgmt_auth = self._create_auth()
            mgmt_client = self._amqp_transport.create_mgmt_client(
                self._address, mgmt_auth=mgmt_auth, config=self._config
            )
            try:
                mgmt_client.open()
                while not mgmt_client.client_ready():
                    time.sleep(0.05)
                # TODO: below might not be needed
                mgmt_msg.application_properties[
                    "security_token"
                ] = self._amqp_transport.get_updated_token(mgmt_auth)
                response = self._amqp_transport.mgmt_client_request(
                    mgmt_client,
                    mgmt_msg,
                    operation=READ_OPERATION,
                    operation_type=op_type,
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
                    raise self._amqp_transport.get_error(
                        self._amqp_transport.AUTH_EXCEPTION,
                        f"Management authentication failed. Status code: {status_code}, Description: {description!r}",
                        condition=errors.ErrorCondition.UnauthorizedAccess,
                    )
                if status_code in [
                    404
                ]:  # TODO: make sure the error surfaced is the same across pyamqp and uamqp
                    return self._amqp_transport.get_error(
                        self._amqp_transport.CONNECTION_ERROR,
                        f"Management connection failed. Status code: {status_code}, Description: {description!r}",
                        condition=errors.ErrorCondition.NotFound,
                    )
                return self._amqp_transport.get_error(
                    self._amqp_transport.AMQP_CONNECTION_ERROR,
                    f"Management request error. Status code: {status_code}, Description: {description!r}",
                    condition=errors.ErrorCondition.UnknownError,
                )
            except Exception as exception:  # pylint: disable=broad-except
                last_exception = self._amqp_transport._handle_exception(
                    exception, self
                )  # pylint: disable=protected-access
                self._backoff(
                    retried_times=retried_times, last_exception=last_exception
                )
                retried_times += 1
                if retried_times > self._config.max_retries:
                    _LOGGER.info(
                        "%r returns an exception %r", self._container_id, last_exception
                    )
                    raise last_exception
            finally:
                mgmt_client.close()

    def _add_span_request_attributes(self, span):
        span.add_attribute("component", "eventhubs")
        span.add_attribute("az.namespace", "Microsoft.EventHub")
        span.add_attribute("message_bus.destination", self._address.path)
        span.add_attribute("peer.address", self._address.hostname)

    def _get_eventhub_properties(self) -> Dict[str, Any]:
        mgmt_msg = self._amqp_transport.MESSAGE(
            application_properties={"name": self.eventhub_name}
        )
        response = self._management_request(mgmt_msg, op_type=MGMT_OPERATION)
        output = {}
        eh_info: Dict[bytes, Any] = response.value
        if eh_info:
            output["eventhub_name"] = eh_info[b"name"].decode("utf-8")
            output["created_at"] = utc_from_timestamp(
                float(eh_info[b"created_at"]) / 1000
            )
            output["partition_ids"] = [
                p.decode("utf-8") for p in eh_info[b"partition_ids"]
            ]
        return output

    def _get_partition_ids(self):
        # type:() -> List[str]
        return self._get_eventhub_properties()["partition_ids"]

    def _get_partition_properties(self, partition_id):
        # type:(str) -> Dict[str, Any]
        mgmt_msg = self._amqp_transport.MESSAGE(
            application_properties={
                "name": self.eventhub_name,
                "partition": partition_id,
            }
        )
        response = self._management_request(mgmt_msg, op_type=MGMT_PARTITION_OPERATION)
        partition_info = response.value  # type: Dict[bytes, Any]
        output = {}
        if partition_info:
            output["eventhub_name"] = partition_info[b"name"].decode("utf-8")
            output["id"] = partition_info[b"partition"].decode("utf-8")
            output["beginning_sequence_number"] = partition_info[
                b"begin_sequence_number"
            ]
            output["last_enqueued_sequence_number"] = partition_info[
                b"last_enqueued_sequence_number"
            ]
            output["last_enqueued_offset"] = partition_info[
                b"last_enqueued_offset"
            ].decode("utf-8")
            output["is_empty"] = partition_info[b"is_partition_empty"]
            output["last_enqueued_time_utc"] = utc_from_timestamp(
                float(partition_info[b"last_enqueued_time_utc"] / 1000)
            )
        return output

    def _close(self):
        # type:() -> None
        self._conn_manager.close_connection()


class ConsumerProducerMixin(object):
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def _create_handler(self, auth):
        pass

    def _check_closed(self):
        if self.closed:
            raise ClientClosedError(
                f"{self._name} has been closed. Please create a new one to handle event data."
            )

    def _open(self):
        """Open the EventHubConsumer/EventHubProducer using the supplied connection."""
        # pylint: disable=protected-access
        if not self.running:
            if self._handler:
                self._handler.close()
            auth = self._client._create_auth()
            self._create_handler(auth)
            self._handler.open()
            while not self._handler.client_ready():
                time.sleep(0.05)
            self._max_message_size_on_link = (
                self._amqp_transport.get_remote_max_message_size(self._handler)
                or self._amqp_transport.MAX_FRAME_SIZE_BYTES
            )
            self.running = True

    def _close_handler(self):
        if self._handler:
            self._handler.close()  # close the link (sharing connection) or connection (not sharing)
        self.running = False

    def _close_connection(self):
        self._close_handler()
        self._client._conn_manager.reset_connection_if_broken()  # pylint: disable=protected-access

    def _handle_exception(self, exception):
        if not self.running and isinstance(
            exception, self._amqp_transport.TIMEOUT_EXCEPTION
        ):
            exception = self._amqp_transport.get_error(
                self._amqp_transport.AUTH_EXCEPTION,
                "Authorization timeout.",
                condition=errors.ErrorCondition.InternalError,
            )
        return self._amqp_transport._handle_exception(
            exception, self
        )  # pylint: disable=protected-access

    def _do_retryable_operation(self, operation, timeout=None, **kwargs):
        # pylint:disable=protected-access
        timeout_time = (time.time() + timeout) if timeout else None
        retried_times = 0
        last_exception = kwargs.pop("last_exception", None)
        operation_need_param = kwargs.pop("operation_need_param", True)
        max_retries = (
            self._client._config.max_retries
        )  # pylint:disable=protected-access

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
                    raise last_exception

    def close(self):
        # type:() -> None
        """
        Close down the handler. If the handler has already closed,
        this will be a no op.
        """
        self._close_handler()
        self.closed = True
