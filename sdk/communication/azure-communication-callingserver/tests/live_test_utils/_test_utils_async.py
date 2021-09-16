# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

from azure.communication.callingserver import PlayAudioResult, CallConnection, PhoneNumberIdentifier, CreateCallOptions, MediaType, EventSubscriptionType, CancelAllMediaOperationsResult
from azure.communication.callingserver import aio

from azure.communication.callingserver.aio import CallConnection as CallConnectionAsync

class CallingServerLiveTestUtils:

    def validate_callconnection_Async(call_connection_async: CallConnectionAsync):
        assert call_connection_async is not None
        assert call_connection_async.call_connection_id is not None
        assert len(call_connection_async.call_connection_id) != 0

    def validate_play_audio_result_Async(play_audio_result: PlayAudioResult):
        assert play_audio_result is not None
        assert play_audio_result.operation_id is not None
        assert len(play_audio_result.operation_id) != 0
        assert play_audio_result.status is not None
        assert play_audio_result.status == OperationStatus.CONST_RUNNING

    def validate_cancel_all_media_operations_Async(cancel_all_media_operations_result: CancelAllMediaOperationsResult):
        assert cancel_all_media_operations_result is not None
        assert cancel_all_media_operations_result.operation_id is not None
        assert len(cancel_all_media_operations_result.operation_id) != 0
        assert cancel_all_media_operations_result.status is not None
        assert cancel_all_media_operations_result.status == OperationStatus.CONST_COMPLETED

class OperationStatus:
    # Static value notStarted for OperationStatus.
    CONST_NOT_STARTED = "notStarted"

    # Static value running for OperationStatus.
    CONST_RUNNING = "running"

    # Static value completed for OperationStatus.
    CONST_COMPLETED = "completed"

    # Static value failed for OperationStatus.
    CONST_FAILED = "failed"

    # // Random Gen Guid
    # protected const string FROM_USER_IDENTIFIER = "e3560385-776f-41d1-bf04-07ef738f2f23";

    # // Random Gen Guid
    # protected const string TO_USER_IDENTIFIER = "e3560385-776f-41d1-bf04-07ef738f2fc1";

    # // From ACS Resource "immutableResourceId".
    # protected const string RESOURCE_IDENTIFIER = "016a7064-0581-40b9-be73-6dde64d69d72";

    # // Random Gen Guid
    # protected const string GROUP_IDENTIFIER = "f8c9bb0a-25ec-408d-b335-266dcc0c0c9a";

    # protected string GetResourceId()
    #     {
    #         if (Mode == RecordedTestMode.Live)
    #         {
    #             return TestEnvironment.ResourceIdentifier;
    #         }
    #         return RESOURCE_IDENTIFIER;
    #     }


    #  if self.is_playback():
    #         self.phone_number = "+14255550123"
    #         self.recording_processors.extend([
    #         BodyReplacerProcessor(keys=["to", "from", "messageId", "repeatabilityRequestId", "repeatabilityFirstSent"])])
    #     else:
    #         self.phone_number = os.getenv("AZURE_PHONE_NUMBER")
    #         self.recording_processors.extend([
    #             BodyReplacerProcessor(keys=["to", "from", "messageId", "repeatabilityRequestId", "repeatabilityFirstSent"]),
    #             ResponseReplacerProcessor(keys=[self._resource_name])])