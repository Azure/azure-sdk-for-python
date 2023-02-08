# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
from typing import Any, List, Optional, Union

from ._generated.models import (
CallLocator,
StartCallRecordingRequest as StartCallRecordingRequestRest,
RecordingContentType, RecordingChannelType, RecordingFormatType,
CommunicationIdentifierModel,
RecordingStorageType
)

class ServerCallLocator(object):
    def __init__(
        self,
        *,
        locatorid: str,
        **kwargs: Any
    ) -> None:

        super().__init__(**kwargs)
        self.id = locatorid
        self.kind = "serverCallLocator"

    def _to_generated(self):

        return CallLocator( kind=self.kind,
        server_call_id=self.id
        )

class GroupCallLocator(object):
    def __init__(
        self,
        *,
        locatorid: str,
        **kwargs: Any
    ) -> None:

        super().__init__(**kwargs)
        self.id = locatorid
        self.kind = "groupCallLocator"

    def _to_generated(self):

        return CallLocator( kind=self.kind,
        group_call_id=self.id
        )

class StartCallRecordingRequest(object):
    def __init__(
        self,
        *,
        call_locator: ServerCallLocator|GroupCallLocator,
        recording_state_callback_uri: Optional[str] = None,
        recording_content_type: Optional[Union[str, "RecordingContentType"]] = None,
        recording_channel_type: Optional[Union[str, "RecordingChannelType"]] = None,
        recording_format_type: Optional[Union[str, "RecordingFormatType"]] = None,
        audio_channel_participant_ordering: Optional[List["CommunicationIdentifierModel"]] = None,
        recording_storage_type: Optional[Union[str, "RecordingStorageType"]] = None,
        **kwargs: Any
    ) -> None:
        """
        :keyword call_locator: The call locator. Required.
        :paramtype call_locator: ~azure.communication.callautomation.models.CallLocator
        :keyword recording_state_callback_uri: The uri to send notifications to.
        :paramtype recording_state_callback_uri: str
        :keyword recording_content_type: The content type of call recording. Known values are: "audio"
         and "audioVideo".
        :paramtype recording_content_type: str or
         ~azure.communication.callautomation.models.RecordingContentType
        :keyword recording_channel_type: The channel type of call recording. Known values are: "mixed"
         and "unmixed".
        :paramtype recording_channel_type: str or
         ~azure.communication.callautomation.models.RecordingChannelType
        :keyword recording_format_type: The format type of call recording. Known values are: "wav",
         "mp3", and "mp4".
        :paramtype recording_format_type: str or
         ~azure.communication.callautomation.models.RecordingFormatType
        :keyword audio_channel_participant_ordering: The sequential order in which audio channels are
         assigned to participants in the unmixed recording.
         When 'recordingChannelType' is set to 'unmixed' and `audioChannelParticipantOrdering is not
         specified,
         the audio channel to participant mapping will be automatically assigned based on the order in
         which participant
         first audio was detected.  Channel to participant mapping details can be found in the metadata
         of the recording.
        :paramtype audio_channel_participant_ordering:
         list[~azure.communication.callautomation.models.CommunicationIdentifierModel]
        :keyword recording_storage_type: Recording storage mode. ``External`` enables bring your own
         storage. Known values are: "acs" and "azureBlob".
        :paramtype recording_storage_type: str or
         ~azure.communication.callautomation.models.RecordingStorageType
        """
        super().__init__(**kwargs)
        self.call_locator = call_locator
        self.recording_state_callback_uri = recording_state_callback_uri
        self.recording_content_type = recording_content_type
        self.recording_channel_type = recording_channel_type
        self.recording_format_type = recording_format_type
        self.audio_channel_participant_ordering = audio_channel_participant_ordering
        self.recording_storage_type = recording_storage_type


    def _to_generated(self):

        return StartCallRecordingRequestRest( call_locator=self.call_locator._to_generated(),
        recording_state_callback_uri=self.recording_state_callback_uri,
        recording_content_type=self.recording_content_type,
        recording_channel_type=self.recording_channel_type,
        recording_format_type=self.recording_format_type,
        audio_channel_participant_ordering=self.audio_channel_participant_ordering,
        recording_storage_type=self.recording_storage_type
        )


class RecordingStateResponse(object):
    """RecordingStateResponse.

    :ivar recording_id:
    :vartype recording_id: str
    :ivar recording_state: Known values are: "active" and "inactive".
    :vartype recording_state: str or ~azure.communication.callautomation.models.RecordingState
    """

    # pylint:disable=protected-access

    def __init__(
        self,
        **kwargs # type: Any
    ):
        # type: (...) -> None
        self.recording_id = kwargs['recording_id']
        self.recording_state = kwargs['recording_state']

    @classmethod
    def _from_generated(cls, recording_state_response):

        return cls(
            recording_id=recording_state_response.recording_id,
            recording_state=recording_state_response.recording_state
        )
