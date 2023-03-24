# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

from typing import Any, List  # pylint: disable=unused-import
from urllib.parse import urlparse
from azure.core.credentials import TokenCredential

from ._version import SDK_MONIKER
from ._api_versions import DEFAULT_VERSION
from ._call_connection_client import CallConnectionClient
from ._call_recording_client import CallRecordingClient
from ._generated._client import AzureCommunicationCallAutomationService
from ._shared.models import CommunicationIdentifier
from ._communication_identifier_serializer import serialize_phone_identifier, serialize_identifier
from ._shared.utils import get_authentication_policy, parse_connection_str
from ._generated.models import (
    CreateCallRequest, AnswerCallRequest, RedirectCallRequest, RejectCallRequest, CustomContext)
from ._models import (CallInvite, CallConnectionProperties)


class CallResult(object):
    def __init__(
        self,
        *,
        call_connection: CallConnectionClient,
        call_connection_properties: CallConnectionProperties,
        **kwargs: Any
    ) -> None:
        """
        :keyword call_connection: Call connection. Required.
        :type call_connection: CallConnectionClient
        :keyword call_connection_properties: Properties of the call connection
        :type call_connection_properties: CallConnectionProperties
        """
        super().__init__(**kwargs)
        self.call_connection = call_connection
        self.call_connection_properties = call_connection_properties


class CreateCallResult(CallResult):
    pass


class AnswerCallResult(CallResult):
    pass


class CallAutomationClient(object):
    """A client to interact with the AzureCommunicationService CallAutomation service.

    Call Automation provides developers the ability to build server-based,
    intelligent call workflows, and call recording for voice and PSTN channels.

    :param str endpoint:
     The endpoint of the Azure Communication resource.
    :param ~azure.core.credentials.TokenCredential credential:
     The credentials with which to authenticate

    :keyword api_version: Azure Communication Call Automation API version.
     Default value is "2023-01-15-preview".
     Note that overriding this default value may result in unsupported behavior.
    :paramtype api_version: str
    """

    def __init__(
            self,
            endpoint: str,
            credential: TokenCredential,
            **kwargs
    ) -> None:
        if not credential:
            raise ValueError("credential can not be None")

        try:
            if not endpoint.lower().startswith('http'):
                endpoint = "https://" + endpoint
        except AttributeError:
            raise ValueError("Host URL must be a string")

        parsed_url = urlparse(endpoint.rstrip('/'))
        if not parsed_url.netloc:
            raise ValueError(f"Invalid URL: {format(endpoint)}")

        self._endpoint = endpoint
        self._api_version = kwargs.pop("api_version", DEFAULT_VERSION)
        self._credential = credential

        self._client = AzureCommunicationCallAutomationService(
            self._endpoint,
            api_version=self._api_version,
            authentication_policy=get_authentication_policy(
                endpoint, credential),
            sdk_moniker=SDK_MONIKER,
            **kwargs)

        self._call_connection_client = self._client.call_connection
        self._call_media = self._client.call_media
        self._call_recording_client = self._client.call_recording
        self.source_identity = kwargs.pop("source_identity", None)

    @classmethod
    def from_connection_string(
        cls,
        conn_str: str,
        **kwargs
    ) -> 'CallAutomationClient':
        """Create CallAutomation from a Connection String.

        :param str conn_str:
         A connection string to an Azure Communication Service resource.

        :return: Instance of CallAutomationClient.
        :rtype: CallAutomationClient
        """
        endpoint, access_key = parse_connection_str(conn_str)

        return cls(endpoint, access_key, **kwargs)

    def get_call_connection(
        self,
        call_connection_id: str,
        **kwargs
    ) -> CallConnectionClient:
        """Get CallConnectionClient object.
        Only use when you already know CallConnectionId for an ongoing call.

        :param str call_connection_id:
         CallConnectionId of ongoing call.

        :return: Instance of CallConnectionClient.
        :rtype: ~azure.communication.callautomation.CallConnectionClient
        """
        if not call_connection_id:
            raise ValueError("call_connection_id can not be None")

        return CallConnectionClient(
            call_connection_id,
            self._call_connection_client,
            self._call_media,
            **kwargs
        )

    def get_call_recording(
        self,
        **kwargs
    ) -> CallRecordingClient:
        """Get CallRecordingClient object.
        For any recording related action, use this to perform actions.

        :return: Instance of CallRecordingClient.
        :rtype: ~azure.communication.callautomation.CallRecordingClient
        """
        return CallRecordingClient(
            self._call_recording_client,
            **kwargs
        )

    def create_call(
        self,
        target: CallInvite,
        callback_uri: str,
        **kwargs
    ) -> CreateCallResult:
        """
        Create a call connection request from a source identity to a target identity.

        :param target: Required. Call invitee's information.
        :type target: CallInvite
        :param callback_uri: Required. The call back uri for receiving events.
        :type callback_uri: str
        :param source_caller_id_number: The source caller Id, a phone number,
         that's shown to the PSTN participant being invited.
         Required only when calling a PSTN callee.
        :type source_caller_id_number: PhoneNumberIdentifier
        :param source_display_name: Display name of the call if dialing out to a pstn number.
        :type source_display_name: str
        :param source_identity: The identifier of the source of the call.
        :type source_identity: CommunicationIdentifier
        :param operation_context: A customer set value used to track the answering of a call.
        :type operation_context: str
        :param media_streaming_configuration: Media Streaming Configuration.
        :type media_streaming_configuration: MediaStreamingConfiguration
        :param azure_cognitive_services_endpoint_url: The identifier of the Cognitive Service resource
     assigned to this call.
        :type azure_cognitive_services_endpoint_url: str
        :return: Instance of CreateCallResult.
        :rtype: CreateCallResult
        """

        if not target:
            raise ValueError('target cannot be None.')
        if not callback_uri:
            raise ValueError('callback_uri cannot be None.')

        media_streaming_config = kwargs.pop(
            "media_streaming_configuration", None)
        user_custom_context = CustomContext(
            voip_headers=target.voipHeaders, sip_headers=target.sipHeaders) if target.sipHeaders or target.voipHeaders else None
        create_call_request = CreateCallRequest(
            targets=[serialize_identifier(target.target)],
            callback_uri=callback_uri,
            source_caller_id_number=serialize_phone_identifier(
                target.sourceCallIdNumber) if target.sourceCallIdNumber else None,
            source_display_name=target.sourceDisplayName,
            source_identity=serialize_identifier(
                self.source_identity) if self.source_identity else None,
            operation_context=kwargs.pop("operation_context", None),
            media_streaming_configuration=media_streaming_config.to_generated(
            ) if media_streaming_config else None,
            azure_cognitive_services_endpoint_url=kwargs.pop(
                "azure_cognitive_services_endpoint_url", None),
            custom_context=user_custom_context
        )
        repeatability_request_id = kwargs.pop("repeatability_request_id", None)
        repeatability_first_sent = kwargs.pop("repeatability_first_sent", None)

        result = self._client.create_call(
            create_call_request=create_call_request,
            repeatability_first_sent=repeatability_first_sent,
            repeatability_request_id=repeatability_request_id,
            **kwargs)

        return CreateCallResult(
            call_connection=self.get_call_connection(
                result.call_connection_id),
            call_connection_properties=CallConnectionProperties._from_generated(  # pylint:disable=protected-access
                result))

    def create_group_call(
        self,
        targets: List[CommunicationIdentifier],
        callback_uri: str,
        **kwargs
    ) -> CreateCallResult:
        """
        Create a call connection request from a source identity to a list of target identities.

        :param targets: Required. A list of targets.
        :type targets: list[CommunicationIdentifier]
        :param callback_uri: Required. The call back uri for receiving events.
        :type callback_uri: str
        :param source_caller_id_number: The source caller Id, a phone number,
         that's shown to the PSTN participant being invited.
         Required only when calling a PSTN callee.
        :type source_caller_id_number: PhoneNumberIdentifier
        :param source_display_name: Display name of the call if dialing out to a pstn number.
        :type source_display_name: str
        :param source_identity: The identifier of the source of the call.
        :type source_identity: CommunicationIdentifier
        :param operation_context: A customer set value used to track the answering of a call.
        :type operation_context: str
        :param media_streaming_configuration: Media Streaming Configuration.
        :type media_streaming_configuration: MediaStreamingConfiguration
        :param azure_cognitive_services_endpoint_url: The identifier of the Cognitive Service resource
     assigned to this call.
        :type azure_cognitive_services_endpoint_url: str
        :param sip_headers: Sip Headers for PSTN Call
        :type sip_headers: Dict[str, str]
        :param voip_headers: Voip Headers for Voip Call
        :type voip_headers: Dict[str, str]
        :return: Instance of CreateCallResult.
        :rtype: CreateCallResult
        """

        if not targets:
            raise ValueError('targets cannot be None.')
        if not callback_uri:
            raise ValueError('callback_uri cannot be None.')

        caller_id_number = kwargs.pop("source_caller_id_number", None)
        media_streaming_config = kwargs.pop(
            "media_streaming_configuration", None)
        sip_headers = kwargs.pop("sip_headers", None)
        voip_headers = kwargs.pop("voip_headers", None)
        user_custom_context = CustomContext(
            voip_headers=voip_headers, sip_headers=sip_headers) if sip_headers or voip_headers else None

        create_call_request = CreateCallRequest(
            targets=[serialize_identifier(identifier)
                     for identifier in targets],
            callback_uri=callback_uri,
            source_caller_id_number=serialize_phone_identifier(
                caller_id_number) if caller_id_number else None,
            source_display_name=kwargs.pop("source_display_name", None),
            source_identity=serialize_identifier(
                self.source_identity) if self.source_identity else None,
            operation_context=kwargs.pop("operation_context", None),
            media_streaming_configuration=media_streaming_config.to_generated(
            ) if media_streaming_config else None,
            azure_cognitive_services_endpoint_url=kwargs.pop(
                "azure_cognitive_services_endpoint_url", None),
            custom_context=user_custom_context,
        )

        repeatability_request_id = kwargs.pop("repeatability_request_id", None)
        repeatability_first_sent = kwargs.pop("repeatability_first_sent", None)

        result = self._client.create_call(
            create_call_request=create_call_request,
            repeatability_first_sent=repeatability_first_sent,
            repeatability_request_id=repeatability_request_id,
            **kwargs)

        return CreateCallResult(
            call_connection=self.get_call_connection(
                result.call_connection_id),
            call_connection_properties=CallConnectionProperties._from_generated(  # pylint:disable=protected-access
                result))

    def answer_call(
        self,
        incoming_call_context: str,
        callback_uri: str,
        **kwargs
    ) -> AnswerCallResult:
        """
        Create a call connection request from a source identity to a list of target identities.

        :param incoming_call_context: Required. The incoming call context.
        :type incoming_call_context: str
        :param callback_uri: Required. The call back uri for receiving events.
        :type callback_uri: str
        :param media_streaming_configuration: Media Streaming Configuration.
        :type media_streaming_configuration: MediaStreamingConfiguration
        :param azure_cognitive_services_endpoint_url: The endpoint uri of
        the Azure Cognitive Services resource attached.
        :type azure_cognitive_services_endpoint_url: str
        :param repeatability_request_id: If specified, the client directs that the request is
         repeatable; that is, that the client can make the request multiple times
         with the same Repeatability-Request-Id and get back an appropriate response
         without the server executing the request multiple times. The value of the
         Repeatability-Request-Id is an opaque string representing a client-generated
         unique identifier for the request. It is a version 4 (random)
         UUID. Default value is None.
        :type repeatability_request_id: str
        :param repeatability_first_sent: If Repeatability-Request-ID header is specified,
          then Repeatability-First-Sent header must also be specified. The value should be
          the date and time at which the request was first created, expressed using the
          IMF-fixdate form of HTTP-date.
          Example: Sun, 06 Nov 1994 08:49:37 GMT. Default value is None.
        :type repeatability_first_sent: str
        :return: Instance of AnswerCallResult.
        :rtype: AnswerCallResult
        """

        if not incoming_call_context:
            raise ValueError('incoming_call_context cannot be None.')
        if not callback_uri:
            raise ValueError('callback_uri cannot be None.')

        media_streaming_config = kwargs.pop(
            "media_streaming_configuration", None)

        answer_call_request = AnswerCallRequest(
            incoming_call_context=incoming_call_context,
            callback_uri=callback_uri,
            media_streaming_configuration=media_streaming_config.to_generated(
            ) if media_streaming_config else None,
            azure_cognitive_services_endpoint_url=kwargs.pop(
                "azure_cognitive_services_endpoint_url", None),
            answered_by_identifier=serialize_identifier(
                self.source_identity) if self.source_identity else None
        )

        repeatability_request_id = kwargs.pop("repeatability_request_id", None)
        repeatability_first_sent = kwargs.pop("repeatability_first_sent", None)

        result = self._client.answer_call(
            answer_call_request=answer_call_request,
            repeatability_first_sent=repeatability_first_sent,
            repeatability_request_id=repeatability_request_id,
            **kwargs)

        return AnswerCallResult(
            call_connection=self.get_call_connection(
                result.call_connection_id),
            call_connection_properties=CallConnectionProperties._from_generated(  # pylint:disable=protected-access
                result))

    def redirect_call(
        self,
        incoming_call_context: str,
        target: CallInvite,
        **kwargs
    ) -> None:
        """
        Redirect a call to a specific target.

        :param incoming_call_context: Required. The incoming call context.
        :type incoming_call_context: str
        :param target: The target identity to redirect the call to. Required.
        :type target: CallInvite
        :return: None
        :rtype: None
        """

        if not incoming_call_context:
            raise ValueError('incoming_call_context cannot be None.')
        if not target:
            raise ValueError('target cannot be None.')
        
        user_custom_context = CustomContext(
            voip_headers=target.voipHeaders, sip_headers=target.sipHeaders) if target.sipHeaders or target.voipHeaders else None

        redirect_call_request = RedirectCallRequest(
            incoming_call_context=incoming_call_context,
            target=serialize_identifier(target.target),
            custom_context=user_custom_context
        )

        repeatability_request_id = kwargs.pop("repeatability_request_id", None)
        repeatability_first_sent = kwargs.pop("repeatability_first_sent", None)

        self._client.redirect_call(
            redirect_call_request=redirect_call_request,
            repeatability_first_sent=repeatability_first_sent,
            repeatability_request_id=repeatability_request_id,
            **kwargs)

    def reject_call(
        self,
        incoming_call_context: str,
        **kwargs
    ) -> None:
        """
        Reject the call.

        :param incoming_call_context: Required. The incoming call context.
        :type incoming_call_context: str
        :param call_reject_reason: The rejection reason.
         Known values are: "none", "busy", and "forbidden".
        :type call_reject_reason: str or CallRejectReason
        :return: None
        :rtype: None
        """

        if not incoming_call_context:
            raise ValueError('incoming_call_context cannot be None.')

        reject_call_request = RejectCallRequest(
            incoming_call_context=incoming_call_context,
            call_reject_reason=kwargs.pop("call_reject_reason", None)
        )

        repeatability_request_id = kwargs.pop("repeatability_request_id", None)
        repeatability_first_sent = kwargs.pop("repeatability_first_sent", None)

        self._client.reject_call(
            reject_call_request=reject_call_request,
            repeatability_first_sent=repeatability_first_sent,
            repeatability_request_id=repeatability_request_id,
            **kwargs)
