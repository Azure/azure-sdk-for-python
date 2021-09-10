# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

from typing import TYPE_CHECKING, Any, List

from azure.core.tracing.decorator import distributed_trace

from ._call_connection import CallConnection
from ._communication_identifier_serializer import (deserialize_identifier,
                                                   serialize_identifier)
from ._generated._azure_communication_calling_server_service import \
    AzureCommunicationCallingServerService
from ._generated.models import CreateCallRequest, PhoneNumberIdentifierModel
from ._models import CreateCallOptions, JoinCallOptions
from ._server_call import ServerCall
from ._shared.models import CommunicationIdentifier

if TYPE_CHECKING:
    from azure.core.credentials import TokenCredential

from ._shared.utils import (get_authentication_policy, get_current_utc_time,
                            parse_connection_str)
from ._version import SDK_MONIKER
from ._content_downloader import ContentDownloader
from ._generated import models as _models
from msrest import Deserializer, Serializer
from azure.core import PipelineClient
from azure.core.pipeline.transport import HttpResponse
from ._generated._configuration import AzureCommunicationCallingServerServiceConfiguration


class CallingServerClient(object):
    """A client to interact with the AzureCommunicationService Calling Server.

    This client provides calling operations.

    :param str endpoint:
        The endpoint url for Azure Communication Service resource.
    :param TokenCredential credential:
        The TokenCredential we use to authenticate against the service.

    .. admonition:: Example:

        .. literalinclude:: ../samples/identity_samples.py
            :language: python
            :dedent: 8
    """

    def __init__(
        self,
        endpoint,  # type: str
        credential,  # type: TokenCredential
        **kwargs  # type: Any
    ):  # type: (...) -> None
        try:
            if not endpoint.lower().startswith('http'):
                endpoint = "https://" + endpoint
        except AttributeError:
            raise ValueError("Account URL must be a string.")

        if not credential:
            raise ValueError(
                "You need to provide account shared key to authenticate.")

        self._endpoint = endpoint
        self._authentication_policy = get_authentication_policy(
            endpoint, credential)
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
        **kwargs  # type: Any
    ):  # type: (...) -> CallingServerClient
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
    ):  # type: (...) -> CallConnection
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
    ):  # type: (...) -> ServerCall
        """Initializes a server call.

        :param str server_call_id:
           The server call id.
        :returns: Instance of ServerCall.
        :rtype: ~azure.communication..callingserver.ServerCall
        """
        if not server_call_id:
            raise ValueError("call_connection_id can not be None")

        return ServerCall(server_call_id, self._server_call_client)

    @distributed_trace()
    def create_call_connection(
        self,
        source,  # type: CommunicationIdentifier
        targets,  # type: List[CommunicationIdentifier]
        options,  # type: CreateCallOptions
        **kwargs: Any
    ):  # type: (...) -> CallConnection
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
            alternate_caller_id=None if options.alternate_Caller_Id == None else PhoneNumberIdentifierModel(
                value=options.alternate_Caller_Id.properties['value']),
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
        server_call_id,  # type: str
        source,  # type: CommunicationIdentifier
        options,  # type: JoinCallOptions
        **kwargs  # type: Any
    ):  # type: (...) -> CallConnection
        """Join the call using server call id.

        :param str server_call_id:
           The server call id.
        :param CommunicationIdentifier targets:
           The source identity.
        :param JoinCallOptions options:
           The call Options.
        :returns: CallConnection for a successful join request.
        :rtype: ~azure.communication.callingserver.CallConnection
        """
        if not server_call_id:
            raise ValueError("server_call_id can not be None")

        if not source:
            raise ValueError("source can not be None")

        if not options:
            raise ValueError("options can not be None")

        join_call_response = self._server_call_client.join_call(
            server_call_id=server_call_id,
            source=source,
            call_options=options,
            **kwargs
        )

        return CallConnection(join_call_response.call_connection_id, self._call_connection_client)

    @distributed_trace()
    def start_download(
        self,
        content_url,  # type: str
        **kwargs  # type: Any
    ):  # type: (...) -> HttpResponse
        """Start download using content url.

        :param str content_url:
            The content url.
        :returns: HttpResponse for a successful download request.
        :rtype: ~HttpResponse
        """
        if not content_url:
            raise ValueError("content_url can not be None")
        client_models = {k: v for k,
                         v in _models.__dict__.items() if isinstance(v, type)}

        self._serialize = Serializer(client_models)
        self._serialize.client_side_validation = False
        self._deserialize = Deserializer(client_models)
        self._config = AzureCommunicationCallingServerServiceConfiguration(
            self._endpoint, authentication_policy=self._authentication_policy)

        base_url = '{endpoint}'
        self._client = PipelineClient(
            base_url=base_url, config=self._config, **kwargs)
        downloader = ContentDownloader(
            self._client, self._serialize, self._deserialize, self._config)
        content_url_result = downloader.start_download(
            content_url=content_url,
        )

        return content_url_result
