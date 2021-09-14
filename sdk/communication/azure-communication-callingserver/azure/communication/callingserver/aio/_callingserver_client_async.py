# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

from typing import TYPE_CHECKING, Any, List

from azure.core.tracing.decorator_async import distributed_trace_async

from .._communication_identifier_serializer import serialize_identifier
from .._generated.aio._azure_communication_calling_server_service import \
    AzureCommunicationCallingServerService
from .._generated.models import CreateCallRequest, PhoneNumberIdentifierModel
from .._shared.models import CommunicationIdentifier
from ._call_connection_async import CallConnection
from ._server_call_async import ServerCall
from .._converters import JoinCallRequestConverter
from .._shared.utils import get_authentication_policy, parse_connection_str
from .._version import SDK_MONIKER

if TYPE_CHECKING:
    from azure.core.credentials_async import AsyncTokenCredential
    from .._models import CreateCallOptions, JoinCallOptions

class CallingServerClient(object):
    """A client to interact with the AzureCommunicationService Calling Server.

    This client provides calling operations.

    :param str endpoint:
        The endpoint url for Azure Communication Service resource.
    :param AsyncTokenCredential credential:
        The AsyncTokenCredential we use to authenticate against the service.

    .. admonition:: Example:

        .. literalinclude:: ../samples/identity_samples.py
            :language: python
            :dedent: 8
    """
    def __init__(
            self,
            endpoint, # type: str
            credential, # type: AsyncTokenCredential
            **kwargs # type: Any
        ): # type: (...) -> None
        try:
            if not endpoint.lower().startswith('http'):
                endpoint = "https://" + endpoint
        except AttributeError:
            raise ValueError("Account URL must be a string.")

        if not credential:
            raise ValueError(
                "You need to provide account shared key to authenticate.")

        self._endpoint = endpoint
        self._callingserver_service_client = AzureCommunicationCallingServerService(
            self._endpoint,
            authentication_policy=get_authentication_policy(endpoint, credential, decode_url=True, is_async=True),
            sdk_moniker=SDK_MONIKER,
            **kwargs)

        self._call_connection_client = self._callingserver_service_client.call_connections
        self._server_call_client = self._callingserver_service_client.server_calls

    @classmethod
    def from_connection_string(
            cls,
            conn_str,  # type: str
            **kwargs # type: Any
        ): # type: (...) -> CallingServerClient
        """Create CallingServerClient from a Connection String.

        :param str conn_str:
            A connection string to an Azure Communication Service resource.
        :returns: Instance of CallingServerClient.
        :rtype: ~azure.communication.callingserver.CallingServerClient

        .. admonition:: Example:

            .. literalinclude:: ../samples/callingserver_sample.py
                :start-after: [START auth_from_connection_string]
                :end-before: [END auth_from_connection_string]
                :language: python
                :dedent: 8
                :caption: Creating the CallingServerClient from a connection string.
        """
        endpoint, access_key = parse_connection_str(conn_str)

        return cls(endpoint, access_key, **kwargs)

    def get_call_connection(
            self,
            call_connection_id,  # type: str
        ): # type: (...) -> CallConnection
        """Initializes a new instance of CallConnection.

        :param str call_connection_id:
           The thread id for the ChatThreadClient instance.
        :returns: Instance of CallConnection.
        :rtype: ~azure.communication..callingserver.CallConnection
        """
        if not call_connection_id:
            raise ValueError("call_connection_id can not be None")

        return CallConnection(call_connection_id, self._call_connection_client)

    def initialize_server_call(
            self,
            server_call_id,  # type: str
        ): # type: (...) -> ServerCall
        """Initializes a server call.

        :param str server_call_id:
           The server call id.
        :returns: Instance of ServerCall.
        :rtype: ~azure.communication..callingserver.ServerCall
        """
        if not server_call_id:
            raise ValueError("call_connection_id can not be None")

        return ServerCall(server_call_id, self._server_call_client)

    @distributed_trace_async()
    async def create_call_connection(
        self,
        source,  # type: CommunicationIdentifier
        targets,  # type: List[CommunicationIdentifier]
        options,  # type: CreateCallOptions
        **kwargs: Any
    ): # type: (...) -> CallConnection
        """Create an outgoing call from source to target identities.

        :param CommunicationIdentifier source:
           The source identity.
        :param List[CommunicationIdentifier] targets:
           The target identities.
        :param CreateCallOptions options:
           The call options.
        :returns: CallConnection for a successful creating callConnection request.
        :rtype: ~azure.communication.callingserver.CallConnection
        """
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
            alternate_caller_id=(None
                if options.alternate_Caller_Id is None
                else PhoneNumberIdentifierModel(value=options.alternate_Caller_Id.properties['value'])),
            subject=options.subject,
            **kwargs
        )

        create_call_response = await self._call_connection_client.create_call(
            call_request=request,
            **kwargs
        )
        return CallConnection(create_call_response.call_connection_id, self._call_connection_client)  # pylint:disable=protected-access

    @distributed_trace_async()
    async def join_call(
        self,
        server_call_id,  # type: str
        source,  # type: CommunicationIdentifier
        call_options,  # type: JoinCallOptions
        **kwargs  # type: Any
    ): # type: (...) -> CallConnection
        """Join the call using server call id.

        :param str server_call_id:
           The server call id.
        :param CommunicationIdentifier source:
           The source identity.
        :param JoinCallOptions call_options:
           The call Options.
        :returns: CallConnection for a successful join request.
        :rtype: ~azure.communication.callingserver.CallConnection
        """
        if not server_call_id:
            raise ValueError("server_call_id can not be None")

        if not source:
            raise ValueError("source can not be None")

        if not call_options:
            raise ValueError("call_options can not be None")

        join_call_request = JoinCallRequestConverter._convert(serialize_identifier(source), call_options)

        join_call_response = await self._server_call_client.join_call(
            server_call_id=server_call_id,
            call_request=join_call_request,
            **kwargs
        )

        return CallConnection(join_call_response.call_connection_id, self._call_connection_client)

    async def close(self) -> None:
        """Close the :class:
        `~azure.communication.callingserver.aio.CallingServerClient` session.
        """
        await self._callingserver_service_client.close()

    async def __aenter__(self) -> "CallingServerClient":
        await self._callingserver_service_client.__aenter__()
        return self

    async def __aexit__(self, *args: "Any") -> None:
        await self._callingserver_service_client.__aexit__(*args)
