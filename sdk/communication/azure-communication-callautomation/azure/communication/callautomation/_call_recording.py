# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

from typing import TYPE_CHECKING  # pylint: disable=unused-import
from ._models import RecordingStateResponse, StartCallRecordingRequest

if TYPE_CHECKING:
    from ._generated.operations import CallRecordingOperations

class CallRecording(object):
    def __init__(
            self,
            call_recording_client,  # type: CallRecordingOperations
        ):

        self._call_recording_client = call_recording_client

    def start_recording(
        self,
        start_call_recording_request:StartCallRecordingRequest,
        **kwargs
    ) -> RecordingStateResponse:
        """Start recording the call.

        :param start_call_recording_request: Required.
        :type content: StartCallRecordingRequest
        :keyword repeatability_request_id: If specified, the client directs that the request is
         repeatable; that is, that the client can make the request multiple times with the same
         Repeatability-Request-Id and get back an appropriate response without the server executing the
         request multiple times. The value of the Repeatability-Request-Id is an opaque string
         representing a client-generated unique identifier for the request. It is a version 4 (random)
         UUID. Default value is None.
        :paramtype repeatability_request_id: str
        :keyword repeatability_first_sent: If Repeatability-Request-ID header is specified, then
         Repeatability-First-Sent header must also be specified. The value should be the date and time
         at which the request was first created, expressed using the IMF-fixdate form of HTTP-date.
         Example: Sun, 06 Nov 1994 08:49:37 GMT. Default value is None.
        :paramtype repeatability_first_sent: str
        :keyword content_type: Body Parameter content-type. Content type parameter for binary body.
         Default value is "application/json".
        :paramtype content_type: str
        :return: RecordingStateResponse
        :rtype: ~azure.communication.callautomation.models.RecordingStateResponse #todo-itk create
         this model, test kwargs
        :raises ~azure.core.exceptions.HttpResponseError:
        """

        repeatability_request_id = kwargs.pop("repeatability_request_id", None)
        repeatability_first_sent = kwargs.pop("repeatability_first_sent", None)

        recording_state_response = self._call_recording_client.start_recording(
        start_call_recording = start_call_recording_request._to_generated(),
        repeatability_first_sent = repeatability_first_sent,
        repeatability_request_id = repeatability_request_id,
        **kwargs)

        return RecordingStateResponse._from_generated(recording_state_response)

    def stop_recording(
        self,
        recording_id,
        **kwargs
    ):
        """Stop recording the call.

        :param recording_id: The recording id. Required.
        :type recording_id: str
        :return: None
        :rtype: None
        :raises ~azure.core.exceptions.HttpResponseError:
        """
        self._call_recording_client.stop_recording(recording_id = recording_id, **kwargs)

    def pause_recording(
        self,
        recording_id,
        **kwargs
    ):
        """Pause recording the call.

        :param recording_id: The recording id. Required.
        :type recording_id: str
        :return: None
        :rtype: None
        :raises ~azure.core.exceptions.HttpResponseError:
        """
        self._call_recording_client.pause_recording(recording_id = recording_id, **kwargs)

    def resume_recording(
        self,
        recording_id,
        **kwargs
    ):
        """Resume recording the call.

        :param recording_id: The recording id. Required.
        :type recording_id: str
        :return: None
        :rtype: None
        :raises ~azure.core.exceptions.HttpResponseError:
        """
        self._call_recording_client.resume_recording(recording_id = recording_id, **kwargs)

    def get_recording_properties(
        self,
        recording_id,
        **kwargs
    ) -> RecordingStateResponse:
        """Get call recording properties.

        :param recording_id: The recording id. Required.
        :type recording_id: str
        :return: RecordingStateResponse
        :rtype: ~azure.communication.callautomation.models.RecordingStateResponse
        :raises ~azure.core.exceptions.HttpResponseError:
        """
        recording_state_response = self._call_recording_client.get_recording_properties(recording_id = recording_id, **kwargs)
        return RecordingStateResponse._from_generated(recording_state_response)
