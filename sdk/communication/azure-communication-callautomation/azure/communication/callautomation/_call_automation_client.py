# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

from typing import Any  # pylint: disable=unused-import
from urllib.parse import urlparse
from azure.core.credentials import TokenCredential

from ._version import SDK_MONIKER
from ._api_versions import DEFAULT_VERSION
from ._call_connection import CallConnection
from ._call_recording import CallRecording
from ._generated._client import AzureCommunicationCallAutomationService
from ._shared.utils import get_authentication_policy, parse_connection_str
from ._generated.models import (CreateCallRequest, AnswerCallRequest)
from ._communication_identifier_serializer import *
from ._models import CallInvite


class CallAutomationClient(object):
    def __init__(
            self,
            endpoint,  # type: str
            credential,  # type: TokenCredential
            **kwargs  # type: Any
    ):
        # type: (...) -> None
        if not credential:
            raise ValueError("credential can not be None")

        try:
            if not endpoint.lower().startswith('http'):
                endpoint = "https://" + endpoint
        except AttributeError:
            raise ValueError("Host URL must be a string")

        parsed_url = urlparse(endpoint.rstrip('/'))
        if not parsed_url.netloc:
            raise ValueError("Invalid URL: {}".format(endpoint))

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
        conn_str,  # type: str
        **kwargs  # type: Any
    ):  # type: (...) -> CallAutomationClient
        endpoint, access_key = parse_connection_str(conn_str)

        return cls(endpoint, access_key, **kwargs)

    def get_call_connection(
        self,
        call_connection_id,  # type: str
        **kwargs  # type: Any
    ):  # type: (...) -> CallConnection

        if not call_connection_id:
            raise ValueError("call_connection_id can not be None")

        return CallConnection(
            call_connection_id,
            self._call_connection_client,
            self._call_media,
            **kwargs
        )

    def get_call_recording(
        self,
        **kwargs  # type: Any
    ):  # type: (...) -> CallRecording

        return CallRecording(
            self._call_recording_client,
            **kwargs
        )

    def create_call(
        self,
        call_invite: CallInvite,
        callback_url: str,
        **kwargs
    ):
        """
        Create a call connection request from a source identity to a target identity.

        :param call_invite: Required. Call invitee's information.
        :type call_invite: CallInvite
        :param callback_url: Required. The call back url for receiving events.
        :type callback_url: str
        :param source_caller_id_number: The source caller Id, a phone number, that's shown to the PSTN participant being invited. Required only when calling a PSTN callee.
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

        """

        if not call_invite:
            raise ValueError('call_invite cannot be None.')
        if not callback_url:
            raise ValueError('callback_url cannot be None.')

        create_call_request = CreateCallRequest(
            targets=[serialize_identifier(call_invite.target)],
            callback_uri=callback_url,
            source_caller_id_number=serialize_identifier(
                call_invite.sourceCallIdNumber),
            source_display_name=call_invite.sourceDisplayName,
            source_identity=self.source_identity,
            operation_context=kwargs.pop("operation_context", None),
            media_streaming_configuration=kwargs.pop(
                "media_streaming_configuration", None),
            azure_cognitive_services_endpoint_url=kwargs.pop(
                "azure_cognitive_services_endpoint_url", None),
        )
        repeatability_request_id = kwargs.pop("repeatability_request_id", None)
        repeatability_first_sent = kwargs.pop("repeatability_first_sent", None)

        self._client.create_call(create_call_request=create_call_request, repeatability_first_sent=repeatability_first_sent,
                                 repeatability_request_id=repeatability_request_id,
                                 **kwargs)

    def create_group_call(
        self,
        targets: list[CommunicationIdentifier],
        callback_url: str,
        **kwargs
    ):
        """
        Create a call connection request from a source identity to a list of target identities.

        :param targets: Required. A list of targets.
        :type targets: list[CommunicationIdentifier]
        :param callback_url: Required. The call back url for receiving events.
        :type callback_url: str
        :param source_caller_id_number: The source caller Id, a phone number, that's shown to the PSTN participant being invited. Required only when calling a PSTN callee.
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

        """

        if not targets:
            raise ValueError('targets cannot be None.')
        if not callback_url:
            raise ValueError('callback_url cannot be None.')

        create_call_request = CreateCallRequest(
            targets=[serialize_identifier(identifier)
                     for identifier in targets],
            callback_uri=callback_url,
            source_caller_id_number=serialize_identifier(
                kwargs.pop("source_caller_id_number", None)),
            source_display_name=kwargs.pop("source_display_name", None),
            source_identity=self.source_identity,
            operation_context=kwargs.pop("operation_context", None),
            media_streaming_configuration=kwargs.pop(
                "media_streaming_configuration", None),
            azure_cognitive_services_endpoint_url=kwargs.pop(
                "azure_cognitive_services_endpoint_url", None),
        )

        repeatability_request_id = kwargs.pop("repeatability_request_id", None)
        repeatability_first_sent = kwargs.pop("repeatability_first_sent", None)

        self._client.create_call(create_call_request=create_call_request, repeatability_first_sent=repeatability_first_sent,
                                 repeatability_request_id=repeatability_request_id,
                                 **kwargs)

    def answer_call(
        self,
        incoming_call_context: str,
        callback_url: str,
        **kwargs
    ):
        """
        Create a call connection request from a source identity to a list of target identities.

        :param incoming_call_context: Required. The incoming call context.
        :type incoming_call_context: str
        :param callback_url: Required. The call back url for receiving events.
        :type callback_url: str

        """

        if not incoming_call_context:
            raise ValueError('incoming_call_context cannot be None.')
        if not callback_url:
            raise ValueError('callback_url cannot be None.')

        answer_call_request = AnswerCallRequest(
            incoming_call_context=incoming_call_context,
            callback_uri=callback_url,
            media_streaming_configuration=kwargs.pop(
                "media_streaming_configuration", None),
            azure_cognitive_services_endpoint_url=kwargs.pop(
                "azure_cognitive_services_endpoint_url", None),
            answered_by_identifier=self.source_identity
        )

        repeatability_request_id = kwargs.pop("repeatability_request_id", None)
        repeatability_first_sent = kwargs.pop("repeatability_first_sent", None)

        self._client.answer_call(answer_call_request == answer_call_request, repeatability_first_sent=repeatability_first_sent,
                                 repeatability_request_id=repeatability_request_id,
                                 **kwargs)
