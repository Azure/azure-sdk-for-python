# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

from typing import TYPE_CHECKING, Any, Dict, List, Optional  # pylint: disable=unused-import

from azure.core.tracing.decorator import distributed_trace
from azure.core import PipelineClient
from azure.core.exceptions import (ClientAuthenticationError, HttpResponseError,
                                    ResourceExistsError, ResourceNotFoundError, map_error)
from azure.core.pipeline import PipelineResponse
from azure.core.pipeline.transport import HttpRequest, HttpResponse
from azure.core.pipeline.policies import HeadersPolicy


from ._generated import models as _models

try:
    from urllib.parse import urlparse
except ImportError:
    from urlparse import urlparse  # type: ignore

from ._communication_identifier_serializer import serialize_identifier
from ._communication_call_locator_serializer import serialize_call_locator
from ._generated._azure_communication_calling_server_service import \
    AzureCommunicationCallingServerService
from ._generated.models import (
    CreateCallRequest,
    PhoneNumberIdentifierModel,
    PlayAudioResult,
    AddParticipantResult
    )
from ._shared.models import CommunicationIdentifier
from ._models import CallLocator
from ._call_connection import CallConnection
from ._converters import (
    JoinCallRequestConverter,
    PlayAudioWithCallLocatorRequestConverter,
    PlayAudioToParticipantWithCallLocatorRequestConverter,
    AddParticipantWithCallLocatorRequestConverter,
    RemoveParticipantWithCallLocatorRequestConverter,
    CancelMediaOperationWithCallLocatorRequestConverter,
    CancelParticipantMediaOperationWithCallLocatorRequestConverter
    )
from ._shared.utils import get_authentication_policy, get_header_policy, parse_connection_str
from ._version import SDK_MONIKER

if TYPE_CHECKING:
    from azure.core.credentials import TokenCredential
    from ._models import CreateCallOptions, JoinCallOptions, PlayAudioOptions

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
        self._callingserver_service_client = AzureCommunicationCallingServerService(
            self._endpoint,
            headers_policy=get_header_policy(endpoint, credential),
            authentication_policy=get_authentication_policy(endpoint, credential),
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
        call_connection_id  # type: str
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

    @distributed_trace()
    def create_call_connection(
        self,
        source,  # type: CommunicationIdentifier
        targets,  # type: List[CommunicationIdentifier]
        options,  # type: CreateCallOptions
        **kwargs  # type: Any
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
            alternate_caller_id=(None
                if options.alternate_Caller_Id is None
                else PhoneNumberIdentifierModel(value=options.alternate_Caller_Id.properties['value'])),
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
        call_locator,  # type: CallLocator
        source,  # type: CommunicationIdentifier
        call_options,  # type: JoinCallOptions
        **kwargs  # type: Any
    ):  # type: (...) -> CallConnection
        """Join the call using call_locator.

        :param CallLocator call_locator:
           The callLocator.
        :param CommunicationIdentifier targets:
           The source identity.
        :param JoinCallOptions options:
           The call Options.
        :returns: CallConnection for a successful join request.
        :rtype: ~azure.communication.callingserver.CallConnection
        """
        if not call_locator:
            raise ValueError("call_locator can not be None")
        if not source:
            raise ValueError("source can not be None")
        if not call_options:
            raise ValueError("call_options can not be None")

        join_call_request = JoinCallRequestConverter.convert(
            serialize_call_locator(call_locator),
            serialize_identifier(source),
            call_options
            )

        join_call_response = self._server_call_client.join_call(
            call_request=join_call_request,
            **kwargs
        )

        return CallConnection(
            join_call_response.call_connection_id,
            self._call_connection_client
            )

    @distributed_trace()
    def play_audio(
        self,
        call_locator,  # type: CallLocator
        audio_file_uri,  # type: str
        play_audio_options,  # type: PlayAudioOptions
        **kwargs  # type: Any
    ):  # type: (...) -> PlayAudioResult

        if not call_locator:
            raise ValueError("call_locator can not be None")
        if not audio_file_uri:
            raise ValueError("audio_file_uri can not be None")
        if not play_audio_options:
            raise ValueError("options can not be None")

        play_audio_request = PlayAudioWithCallLocatorRequestConverter.convert(
            serialize_call_locator(call_locator),
            audio_file_uri,
            play_audio_options
            )

        return self._server_call_client.play_audio(
            play_audio_request=play_audio_request,
            **kwargs
        )

    @distributed_trace()
    def play_audio_to_participant(
        self,
        call_locator,  # type: CallLocator
        participant,  # type: CommunicationIdentifier
        audio_file_uri,  # type: str
        play_audio_options,  # type: PlayAudioOptions
        **kwargs  # type: Any
    ):  # type: (...) -> PlayAudioResult

        if not call_locator:
            raise ValueError("call_locator can not be None")
        if not participant:
            raise ValueError("participant can not be None")
        if not audio_file_uri:
            raise ValueError("audio_file_uri can not be None")
        if not play_audio_options:
            raise ValueError("play_audio_options can not be None")

        play_audio_to_participant_request = PlayAudioToParticipantWithCallLocatorRequestConverter.convert(
            serialize_call_locator(call_locator),
            serialize_identifier(participant),
            audio_file_uri,
            play_audio_options
            )

        return self._server_call_client.participant_play_audio(
            play_audio_to_participant_request=play_audio_to_participant_request,
            **kwargs
        )

    @distributed_trace()
    def add_participant(
        self,
        call_locator,  # type: CallLocator
        participant,  # type: CommunicationIdentifier
        callback_uri,  # type: str
        alternate_caller_id,  # type: Optional[str]
        operation_context,  # type: Optional[str]
        **kwargs  # type: Any
    ):  # type: (...) -> AddParticipantResult

        if not call_locator:
            raise ValueError("call_locator can not be None")
        if not participant:
            raise ValueError("participant can not be None")

        alternate_caller_id = (None
            if alternate_caller_id is None
            else PhoneNumberIdentifierModel(value=alternate_caller_id))

        add_participant_with_call_locator_request = AddParticipantWithCallLocatorRequestConverter.convert(
            serialize_call_locator(call_locator),
            serialize_identifier(participant),
            alternate_caller_id=alternate_caller_id,
            operation_context=operation_context,
            callback_uri=callback_uri
            )

        return self._server_call_client.add_participant(
            add_participant_with_call_locator_request=add_participant_with_call_locator_request,
            **kwargs
        )

    @distributed_trace()
    def remove_participant(
        self,
        call_locator,  # type: CallLocator
        participant,  # type: CommunicationIdentifier
        **kwargs  # type: Any
    ): # type: (...) -> None

        remove_participant_with_call_locator_request = RemoveParticipantWithCallLocatorRequestConverter.convert(
            serialize_call_locator(call_locator),
            serialize_identifier(participant)
            )

        return self._server_call_client.remove_participant(
            remove_participant_with_call_locator_request=remove_participant_with_call_locator_request,
            **kwargs
        )

    @distributed_trace()
    def cancel_media_operation(
        self,
        call_locator,  # type: CallLocator
        media_operation_id,  # type: str
        **kwargs  # type: Any
    ): # type: (...) -> None

        if not call_locator:
            raise ValueError("call_locator can not be None")
        if not media_operation_id:
            raise ValueError("media_operation_id can not be None")

        cancel_media_operation_request = CancelMediaOperationWithCallLocatorRequestConverter.convert(
            serialize_call_locator(call_locator),
            media_operation_id=media_operation_id
            )

        return self._server_call_client.cancel_media_operation(
            cancel_media_operation_request=cancel_media_operation_request,
            **kwargs
        )

    @distributed_trace()
    def cancel_participant_media_operation(
        self,
        call_locator,  # type: CallLocator
        participant,  # type: CommunicationIdentifier
        media_operation_id,  # type: str
        **kwargs  # type: Any
    ): # type: (...) -> None

        if not call_locator:
            raise ValueError("call_locator can not be None")
        if not participant:
            raise ValueError("participant can not be None")
        if not media_operation_id:
            raise ValueError("media_operation_id can not be None")

        cancel_participant_media_operation_request = CancelParticipantMediaOperationWithCallLocatorRequestConverter.convert(
            serialize_call_locator(call_locator),
            serialize_identifier(participant),
            media_operation_id=media_operation_id
            )

        return self._server_call_client.cancel_participant_media_operation(
            cancel_participant_media_operation_request=cancel_participant_media_operation_request,
            **kwargs
            )

    @distributed_trace()
    def delete_recording(
        self,
        content_delete_url, # type: str
        **kwargs # type: Any

    ): # type: (...) -> HttpResponse
        if not content_delete_url:
            raise ValueError("content_delete_url can not be None")

        url = content_delete_url
        uri_to_sign_with = self.get_url_to_sign_request_with(url)

        query_parameters = {}
        # Construct headers
        header_parameters = {}  # type: Dict[str, Any]
        header_parameters['UriToSignWith'] = self._callingserver_service_client._serialize.header(
            "uri_to_sign_with", uri_to_sign_with, 'str')

        error_map = {
            409: ResourceExistsError,
            400: lambda response: HttpResponseError(response=response,
                                                    model=self._callingserver_service_client._deserialize(_models.CommunicationErrorResponse,
                                                                            response)),
            401: lambda response: ClientAuthenticationError(response=response,
                                                            model=self._callingserver_service_client._deserialize(_models.CommunicationErrorResponse,
                                                                                    response)),
            403: lambda response: HttpResponseError(response=response,
                                                    model=self._callingserver_service_client._deserialize(_models.CommunicationErrorResponse,
                                                                            response)),
            404: lambda response: ResourceNotFoundError(response=response,
                                                        model=self._callingserver_service_client._deserialize(_models.CommunicationErrorResponse,
                                                                                response)),
            500: lambda response: HttpResponseError(response=response,
                                                    model=self._callingserver_service_client._deserialize(_models.CommunicationErrorResponse,
                                                                            response)),
        }
        error_map.update(kwargs.pop('error_map', {}))

        request = self._callingserver_service_client._client.delete(url, query_parameters, header_parameters)
        pipeline_response = self._callingserver_service_client._client._pipeline.run(request, **kwargs) # pylint: disable=protected-access
        response = pipeline_response.http_response
        if response.status_code not in [200]:
            map_error(status_code=response.status_code,
                      response=response, error_map=error_map)
            raise HttpResponseError(response=response)

        return response


    def get_url_to_sign_request_with(
        self,
        content_url # type: str
    ):
        path = urlparse(content_url).path
        return self._endpoint + path