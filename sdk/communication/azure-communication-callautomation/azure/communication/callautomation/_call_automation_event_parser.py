# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import json
from typing import Any, TYPE_CHECKING, Union
from azure.communication.callautomation._generated._serialization import Deserializer
from azure.communication.callautomation._generated import models as _models
from ._events_mapping import get_mapping

if TYPE_CHECKING:
    from ._events  import (
        AddParticipantSucceededEventData,
        AddParticipantFailedEventData,
        CallConnectedEventData,
        CallDisconnectedEventData,
        CallTransferAcceptedEventData,
        CallTransferFailedEventData,
        ParticipantsUpdatedEventData,
        RecordingStateChangedEventData,
        PlayCompletedEventData,
        PlayFailedEventData,
        PlayCanceledEventData,
        RecognizeCompletedEventData,
        RecognizeCanceledEventData,
        RecognizeFailedEventData,
        RemoveParticipantSucceededEventData,
        RemoveParticipantFailedEventData,
        ContinuousDtmfRecognitionToneReceivedEventData,
        ContinuousDtmfRecognitionToneFailedEventData,
        ContinuousDtmfRecognitionStoppedEventData,
        SendDtmfCompletedEventData,
        SendDtmfFailedEventData
    )

class CallAutomationEventParser(object):
    """CallAutomationEventParser helps deserialize CallAutomationEvent object sent by server.
    These Callback events are sent to callback url that was provided during either creating outbound call,
    or answering incoming call.
    """
    _client_models = {k: v for k, v in _models.__dict__.items() if isinstance(v, type)}
    _deserializer = Deserializer(_client_models)

    def __init__(
        self,
        **kwargs
    ):
        super().__init__(**kwargs)

    @classmethod
    def from_json(
        cls,
        event: Any
    ) -> Union['AddParticipantSucceededEventData',
               'AddParticipantFailedEventData',
               'CallConnectedEventData',
               'CallDisconnectedEventData',
               'CallTransferAcceptedEventData',
               'CallTransferFailedEventData',
               'ParticipantsUpdatedEventData',
               'RecordingStateChangedEventData',
               'PlayCompletedEventData',
               'PlayFailedEventData',
               'PlayCanceledEventData',
               'RecognizeCompletedEventData',
               'RecognizeCanceledEventData',
               'RecognizeFailedEventData',
               'RemoveParticipantSucceededEventData',
               'RemoveParticipantFailedEventData', 'ContinuousDtmfRecognitionToneReceivedEventData',
               'ContinuousDtmfRecognitionToneFailedEventData', 'ContinuousDtmfRecognitionStoppedEventData',
               'SendDtmfCompletedEventData',
               'SendDtmfFailedEventData']:
        """
        Returns the deserialized CallAutomationEvent object when a json payload is provided.

        :param event: The json string that should be converted into a CallAutomationEvent.
        :type event: any
        :return: Parsed CallAutomationEvent
        :rtype:
         AddParticipantSucceededEventData or
         AddParticipantFailedEventData or
         CallConnectedEventData or
         CallDisconnectedEventData or
         CallTransferAcceptedEventData or
         CallTransferFailedEventData or
         ParticipantsUpdatedEventData or
         RecordingStateChangedEventData or
         PlayCompletedEventData or
         PlayFailedEventData or
         PlayCanceledEventData or
         RecognizeCompletedEventData or
         RecognizeCanceledEventData or
         RecognizeFailedEventData or
         RemoveParticipantSucceededEventData or
         RemoveParticipantFailedEventData or ContinuousDtmfRecognitionToneReceivedEventData or
         ContinuousDtmfRecognitionToneFailedEventData or ContinuousDtmfRecognitionStoppedEventData or
         SendDtmfCompletedEventData or
         SendDtmfFailedEventData
        :raises ValueError: If the provided JSON is invalid.
        """
        parsed = json.loads(event)
        if isinstance(parsed, list):
            # If JSON object is an array, extract the first element
            parsed = parsed[0]

        event_type = ""
        if parsed['type']:
            event_type = parsed['type'].split(".")[-1]

        event_mapping = get_mapping()

        if event_type in event_mapping:
            event_data = parsed['data']
            event_class = event_mapping[event_type]

            # deserialize event into generated event
            generated_event = cls._deserializer(event_type, event_data)

            # create public event class with given AutoRest deserialized event
            return event_class._from_generated(generated_event) #pylint:disable=protected-access

        raise ValueError('Unknown event type:', event_type)
