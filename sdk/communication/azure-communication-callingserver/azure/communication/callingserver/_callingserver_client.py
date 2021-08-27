# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

from typing import Any, List

from azure.core.tracing.decorator import distributed_trace

from ._call_connection import CallConnection
from ._communication_identifier_serializer import (deserialize_identifier,
                                                   serialize_identifier)
from ._generated._azure_communication_calling_server_service import \
    AzureCommunicationCallingServerService
from ._generated.models import CreateCallRequest, PhoneNumberIdentifierModel, JoinCallRequest
from ._models import CreateCallOptions, JoinCallOptions
from ._server_call import ServerCall
from ._shared.models import CommunicationIdentifier
from ._shared.user_credential import CommunicationTokenCredential
from ._shared.utils import (get_authentication_policy, get_current_utc_time,
                            parse_connection_str)
from ._version import SDK_MONIKER
from ._converters import JoinCallRequestConverter

class CallingServerClient(object):
    def __init__(
        self,
        endpoint: str,
        credential: CommunicationTokenCredential,
        **kwargs: Any
    ):
        # type: (...) -> None
        
        try:
            if not endpoint.lower().startswith('http'):
                endpoint = "https://" + endpoint
        except AttributeError:
            raise ValueError("Account URL must be a string.")

        if not credential:
            raise ValueError(
                "invalid credential from connection string.")

        self._endpoint = endpoint
        self._authentication_policy = get_authentication_policy(endpoint, credential)

        self._callingserver_service_client = AzureCommunicationCallingServerService(
            self._endpoint,
            authentication_policy=self._authentication_policy,
            sdk_moniker=SDK_MONIKER,
            **kwargs)

        self._call_connection_client = self._callingserver_service_client.call_connections
        self._server_call_client = self._callingserver_service_client.server_calls

    @classmethod
    def from_connection_string(
        cls,
        conn_str,  # type: str
        **kwargs # type: Any
    ):
        # type: (...) -> CallingServerClient
        endpoint, access_key = parse_connection_str(conn_str)

        return cls(endpoint, access_key, **kwargs)

    def get_call_connection(
        self,
        call_connection_id: str,
    ):
        # type: (...) -> CallConnection

        if not call_connection_id:
            raise ValueError("call_connection_id can not be None")

        return CallConnection(call_connection_id, self._call_connection_client)

    def initialize_server_call(
        self,
        server_call_id: str,
    ):
        # type: (...) -> ServerCall

        if not server_call_id:
            raise ValueError("call_connection_id can not be None")

        return ServerCall(server_call_id, self._server_call_client)

    @distributed_trace()
    def create_call_connection(
        self,
        source: CommunicationIdentifier,
        targets: List[CommunicationIdentifier],
        options: CreateCallOptions,
        **kwargs: Any
    ):
        # type: (...) -> CallConnection

        if not source:
            raise ValueError("source can not be None")

        if not targets:
            raise ValueError("targets can not be None or empty")

        if not options:
            raise ValueError("options can not be None")

        request = CreateCallRequest(
            source=serialize_identifier(source),
            targets=[serialize_identifier(m) for m in targets],
            callback_uri=options.callback_uri,
            requested_media_types=options.requested_media_types,
            requested_call_events=options.requested_call_events,
            alternate_caller_id=None if options.alternate_Caller_Id == None else PhoneNumberIdentifierModel(value=options.alternate_Caller_Id.properties['value']),
            subject=options.subject,
            **kwargs
        )

        create_call_response = self._call_connection_client.create_call(
            call_request=request,
            **kwargs
        )

        return CallConnection(create_call_response.call_connection_id, self._call_connection_client)  # pylint:disable=protected-access

    @distributed_trace()
    def join_call(
        self,
        server_call_id: str,
        source: CommunicationIdentifier,
        options: JoinCallOptions,
        **kwargs  # type: Any
    ):
        # type: (...) -> CallConnection

        if not server_call_id:
            raise ValueError("server_call_id can not be None")

        if not source:
            raise ValueError("source can not be None")

        if not options:
            raise ValueError("options can not be None")

        join_call_request = JoinCallRequestConverter.convert(source, options)
        join_call_response = self._server_call_client.join_call(
            server_call_id,
            join_call_request,
            **kwargs
        )

        return CallConnection(join_call_response.call_connection_id, self._call_connection_client)

    def close(self):
        # type: () -> None
        self._callingserver_service_client.close()

    def __enter__(self):
        # type: () -> CallingServerClient
        self._callingserver_service_client.__enter__()  # pylint:disable=no-member
        return self

    def __exit__(self, *args):
        # type: (*Any) -> None
        self._callingserver_service_client.__exit__(*args)  # pylint:disable=no-member
