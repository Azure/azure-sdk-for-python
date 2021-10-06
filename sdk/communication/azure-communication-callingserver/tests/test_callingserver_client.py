# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import unittest
import utils._test_mock_utils as _mock_utils
import utils._test_constants as _test_constants

from typing import List
from parameterized import parameterized
from azure.communication.callingserver import (
    CreateCallOptions,
    JoinCallOptions,
    CommunicationIdentifier,
    CallLocator,
    PlayAudioOptions,
    ServerCallLocator
    )

from utils._unit_test_utils import CallingServerUnitTestUtils

class TestCallingServerClient(unittest.TestCase):

    @parameterized.expand(CallingServerUnitTestUtils.data_source_test_create_connection())
    def test_create_connection_succeed(
        self,
        test_name, # type: str
        source_user, # type: CommunicationIdentifier
        target_users, # type: List[CommunicationIdentifier]
        options, # type: CreateCallOptions
        use_managed_identity = False # type: bool
        ):

        calling_server_client = _mock_utils.create_mock_calling_server_client(
            status_code=201,
            payload=_test_constants.CreateOrJoinCallPayload,
            use_managed_identity = use_managed_identity
            )

        call_connection = calling_server_client.create_call_connection(source_user,
            target_users, options)
        assert call_connection.call_connection_id == _test_constants.CALL_ID

    @parameterized.expand(CallingServerUnitTestUtils.data_source_test_create_connection())
    def test_create_connection_failed(
        self,
        test_name, # type: str
        source_user, # type: CommunicationIdentifier
        target_users, # type: List[CommunicationIdentifier]
        options, # type: CreateCallOptions
        use_managed_identity = False # type: bool
        ):

        calling_server_client = _mock_utils.create_mock_calling_server_client(
            status_code=404,
            payload=_test_constants.ErrorPayload,
            use_managed_identity = use_managed_identity
            )

        raised = False
        try:
            calling_server_client.create_call_connection(source_user, target_users, options)
        except:
            raised = True
        assert raised == True

    @parameterized.expand(CallingServerUnitTestUtils.data_source_test_join_call())
    def test_join_call_succeed(
        self,
        test_name, # type: str
        call_locator, # type: CallLocator
        source_user, # type: CommunicationIdentifier
        options, # type: JoinCallOptions
        use_managed_identity = False # type: bool
        ):

        calling_server_client = _mock_utils.create_mock_calling_server_client(
            status_code=202,
            payload=_test_constants.CreateOrJoinCallPayload,
            use_managed_identity = use_managed_identity
            )

        call_connection = calling_server_client.join_call(
            call_locator,
            source_user,
            options
            )

        assert call_connection.call_connection_id == _test_constants.CALL_ID

    @parameterized.expand(CallingServerUnitTestUtils.data_source_test_join_call())
    def test_join_call_failed(
        self,
        test_name, # type: str
        call_locator, # type: CallLocator
        source_user, # type: CommunicationIdentifier
        options, # type: JoinCallOptions
        use_managed_identity = False # type: bool
        ):

        calling_server_client = _mock_utils.create_mock_calling_server_client(
            status_code=404,
            payload=_test_constants.ErrorPayload,
            use_managed_identity = use_managed_identity
            )

        raised = False
        try:
            calling_server_client.join_call(
                call_locator,
                source_user,
                options
                )
        except:
            raised = True
        assert raised == True

    @parameterized.expand(CallingServerUnitTestUtils.data_source_test_play_audio())
    def test_play_audio_succeed(
        self,
        test_name, # type: str
    call_locator, # type: CallLocator
        audio_file_uri, # type: str
        options, # type: PlayAudioOptions
        use_managed_identity = False # type: bool
        ):

        calling_server_client = _mock_utils.create_mock_calling_server_client(
            status_code=202,
            payload=_test_constants.PlayAudioResponsePayload,
            use_managed_identity=use_managed_identity
            )

        result = calling_server_client.play_audio(
            call_locator,
            audio_file_uri,
            options
            )

        CallingServerUnitTestUtils.verify_play_audio_result(result)

    @parameterized.expand(CallingServerUnitTestUtils.data_source_test_play_audio())
    def test_play_audio_failed(
        self,
        test_name, # type: str
        call_locator, # type: CallLocator
        audio_file_uri, # type: str
        options, # type: PlayAudioOptions
        use_managed_identity = False # type: bool
        ):

        calling_server_client = _mock_utils.create_mock_calling_server_client(
            status_code=404,
            payload=_test_constants.ErrorPayload,
            use_managed_identity = use_managed_identity
            )

        raised = False
        try:
            calling_server_client.play_audio(
                call_locator,
                audio_file_uri,
                options
                )
        except:
            raised = True
        assert raised == True

    @parameterized.expand(CallingServerUnitTestUtils.data_source_test_play_audio_to_participant())
    def test_play_audio_to_participant_succeed(
        self,
        test_name, # type: str
        call_locator, # type: CallLocator
        participant, # type: CommunicationIdentifier
        audio_file_uri, # type: str
        play_audio_options, # type: PlayAudioOptions
        use_managed_identity = False # type: bool
        ):

        calling_server_client = _mock_utils.create_mock_calling_server_client(
            status_code=202,
            payload=_test_constants.PlayAudioResponsePayload,
            use_managed_identity=use_managed_identity
            )

        result = calling_server_client.play_audio_to_participant(
            call_locator,
            participant,
            audio_file_uri,
            play_audio_options
            )
        CallingServerUnitTestUtils.verify_play_audio_result(result)

    @parameterized.expand(CallingServerUnitTestUtils.data_source_test_play_audio_to_participant())
    def test_play_audio_to_participant_failed(
        self,
        test_name, # type: str
        call_locator, # type: CallLocator
        participant, # type: CommunicationIdentifier
        audio_file_uri, # type: str
        play_audio_options, # type: PlayAudioOptions
        use_managed_identity = False # type: bool
        ):

        calling_server_client = _mock_utils.create_mock_calling_server_client(
            status_code=404,
            payload=_test_constants.ErrorPayload,
            use_managed_identity = use_managed_identity
            )

        raised = False
        try:
            calling_server_client.play_audio_to_participant(
                call_locator,
                participant,
                audio_file_uri,
                play_audio_options
                )
        except:
            raised = True
        assert raised == True

    @parameterized.expand(CallingServerUnitTestUtils.data_source_test_add_participant())
    def test_add_participant_succeed(
        self,
        test_name, # type: str
        call_locator, # type: CallLocator
        participant, # type: CommunicationIdentifier
        callback_uri, # type: str
        alternate_caller_id, # type: str
        operation_context, # type: str
        use_managed_identity = False # type: bool
        ):

        calling_server_client = _mock_utils.create_mock_calling_server_client(
            status_code=202,
            payload=_test_constants.AddParticipantResultPayload,
            use_managed_identity=use_managed_identity
            )

        result = calling_server_client.add_participant(
            call_locator,
            participant,
            callback_uri,
            alternate_caller_id = alternate_caller_id,
            operation_context = operation_context
            )

        CallingServerUnitTestUtils.verify_add_participant_result(result)

    @parameterized.expand(CallingServerUnitTestUtils.data_source_test_add_participant())
    def test_add_participant_failed(
        self,
        test_name, # type: str
        call_locator, # type: CallLocator
        participant, # type: CommunicationIdentifier
        callback_uri, # type: str
        alternate_caller_id, # type: str
        operation_context, # type: str
        use_managed_identity = False # type: bool
        ):

        calling_server_client = _mock_utils.create_mock_calling_server_client(
            status_code=404,
            payload=_test_constants.ErrorPayload,
            use_managed_identity = use_managed_identity
            )

        raised = False
        try:
            calling_server_client.add_participant(
                call_locator,
                participant,
                callback_uri,
                alternate_caller_id = alternate_caller_id,
                operation_context = operation_context
                )
        except:
            raised = True
        assert raised == True

    @parameterized.expand(CallingServerUnitTestUtils.data_source_test_remove_participant())
    def test_remove_participant_succeed(
        self,
        test_name, # type: str
        call_locator, # type: CallLocator
        participant, # type: CommunicationIdentifier
        use_managed_identity = False # type: bool
        ):

        calling_server_client = _mock_utils.create_mock_calling_server_client(
            status_code=202,
            payload=None,
            use_managed_identity=use_managed_identity
            )

        calling_server_client.remove_participant(
            call_locator,
            participant
            )

    @parameterized.expand(CallingServerUnitTestUtils.data_source_test_remove_participant())
    def test_remove_participant_failed(
        self,
        test_name, # type: str
        call_locator, # type: CallLocator
        participant, # type: CommunicationIdentifier
        use_managed_identity = False # type: bool
        ):

        calling_server_client = _mock_utils.create_mock_calling_server_client(
            status_code=404,
            payload=_test_constants.ErrorPayload,
            use_managed_identity = use_managed_identity
            )

        raised = False
        try:
            calling_server_client.remove_participant(
                call_locator,
                participant
                )
        except:
            raised = True
        assert raised == True

    @parameterized.expand(CallingServerUnitTestUtils.data_source_test_cancel_media_operation())
    def test_cancel_media_operation_succeed(
        self,
        test_name, # type: str
        call_locator, # type: CallLocator
        media_operation_id, # type: str
        use_managed_identity = False # type: bool
        ):

        calling_server_client = _mock_utils.create_mock_calling_server_client(
            status_code=200,
            payload=None,
            use_managed_identity=use_managed_identity
            )

        calling_server_client.cancel_media_operation(
            call_locator,
            media_operation_id
            )

    @parameterized.expand(CallingServerUnitTestUtils.data_source_test_cancel_media_operation())
    def test_cancel_media_operation_failed(
        self,
        test_name, # type: str
        call_locator, # type: CallLocator
        media_operation_id, # type: str
        use_managed_identity = False # type: bool
        ):

        calling_server_client = _mock_utils.create_mock_calling_server_client(
            status_code=404,
            payload=_test_constants.ErrorPayload,
            use_managed_identity = use_managed_identity
            )

        raised = False
        try:
             calling_server_client.cancel_media_operation(
                call_locator,
                media_operation_id = media_operation_id
                )
        except:
            raised = True
        assert raised == True

    @parameterized.expand(CallingServerUnitTestUtils.data_source_test_cancel_participant_media_operation())
    def test_cancel_participant_media_operation(
        self,
        test_name, # type: str
        call_locator, # type: CallLocator
        participant, # type: CommunicationIdentifier
        media_operation_id, # type: str
        use_managed_identity = False # type: bool
        ):

        calling_server_client = _mock_utils.create_mock_calling_server_client(
            status_code=200,
            payload=None,
            use_managed_identity=use_managed_identity
            )

        calling_server_client.cancel_participant_media_operation(
            call_locator,
            participant,
            media_operation_id
            )

    @parameterized.expand(CallingServerUnitTestUtils.data_source_test_cancel_participant_media_operation())
    def test_cancel_media_operation_failed(
        self,
        test_name, # type: str
        call_locator, # type: CallLocator
        participant, # type: CommunicationIdentifier
        media_operation_id, # type: str
        use_managed_identity = False # type: bool
        ):

        calling_server_client = _mock_utils.create_mock_calling_server_client(
            status_code=404,
            payload=_test_constants.ErrorPayload,
            use_managed_identity = use_managed_identity
            )

        raised = False
        try:
            calling_server_client.cancel_participant_media_operation(
                call_locator,
                participant,
                media_operation_id
                )
        except:
            raised = True
        assert raised == True

    def test_start_recording_relative_uri_fails(self):
        server_call_id = "aHR0cHM6Ly9jb252LXVzd2UtMDguY29udi5za3lwZS5jb20vY29udi8tby1FWjVpMHJrS3RFTDBNd0FST1J3P2k9ODgmZT02Mzc1Nzc0MTY4MDc4MjQyOTM"
        with self.assertRaises(ValueError):
            _mock_utils.create_calling_server_client().start_recording(ServerCallLocator(server_call_id), "/not/absolute/uri")