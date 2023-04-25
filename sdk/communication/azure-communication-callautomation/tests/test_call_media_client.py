# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import unittest

from azure.communication.callautomation import (
    CallMediaClient,
    _communication_identifier_serializer
)
from azure.communication.callautomation._models import (
    FileSource,
    PhoneNumberIdentifier,
    DtmfTone,
    CallMediaRecognizeDtmfOptions
)
from azure.communication.callautomation._generated.models import (
    PlayRequest,
    PlaySource,
    PlaySourceType,
    PlayOptions,
    RecognizeRequest,
    RecognizeOptions,
    DtmfOptions
)
from unittest.mock import Mock

class TestCallMediaClient(unittest.TestCase):
    def setUp(self):
        self.call_connection_id = "10000000-0000-0000-0000-000000000000"
        self.uri = "https://file_source_url.com/audio_file.wav"
        self.phone_number = "+12345678900"
        self.target_user = PhoneNumberIdentifier(self.phone_number)
        self.call_media_operations = Mock()

        self.call_media_client = CallMediaClient(call_connection_id=self.call_connection_id, call_media_operations=self.call_media_operations)

    def test_play(self):
        mock_play = Mock()
        self.call_media_operations.play = mock_play
        play_source = FileSource(uri=self.uri)

        self.call_media_client.play(play_source=play_source, play_to=[self.target_user])

        expected_play_request = PlayRequest(
            play_source_info=PlaySource(
                source_type=PlaySourceType.FILE,
                file_source=FileSource(uri=self.uri),
                play_source_id=None
            ),
            play_to=[_communication_identifier_serializer.serialize_identifier(self.target_user)],
            play_options=PlayOptions(loop=False)            
        )
        mock_play.assert_called_once()
        actual_play_request = mock_play.call_args[0][1]

        self.assertEqual(expected_play_request.play_source_info.source_type, actual_play_request.play_source_info.source_type)
        self.assertEqual(expected_play_request.play_source_info.file_source.uri, actual_play_request.play_source_info.file_source.uri)
        self.assertEqual(expected_play_request.play_source_info.play_source_id, actual_play_request.play_source_info.play_source_id)
        self.assertEqual(expected_play_request.play_to[0]['raw_id'], actual_play_request.play_to[0]['raw_id'])
        self.assertEqual(expected_play_request.play_options, actual_play_request.play_options)


    def test_play_to_all(self):
        mock_play = Mock()
        self.call_media_operations.play = mock_play
        play_source = FileSource(uri=self.uri)

        self.call_media_client.play_to_all(play_source=play_source)

        expected_play_request = PlayRequest(
            play_source_info=PlaySource(
                source_type=PlaySourceType.FILE,
                file_source=FileSource(uri=self.uri),
                play_source_id=None
            ),
            play_to=[],
            play_options=PlayOptions(loop=False)            
        )
        mock_play.assert_called_once()
        actual_play_request = mock_play.call_args[0][1]

        self.assertEqual(expected_play_request.play_source_info.source_type, actual_play_request.play_source_info.source_type)
        self.assertEqual(expected_play_request.play_source_info.file_source.uri, actual_play_request.play_source_info.file_source.uri)
        self.assertEqual(expected_play_request.play_source_info.play_source_id, actual_play_request.play_source_info.play_source_id)
        self.assertEqual(expected_play_request.play_to, actual_play_request.play_to)
        self.assertEqual(expected_play_request.play_options, actual_play_request.play_options)
    
    def test_recognize(self):
        mock_recognize = Mock()
        self.call_media_operations.recognize = mock_recognize
        play_source = FileSource(uri=self.uri)

        recognize_options = CallMediaRecognizeDtmfOptions(
                target_participant=self.target_user,
                max_tones_to_collect=3)
        recognize_options.inter_tone_timeout = 10
        recognize_options.stop_dtmf_tones = [DtmfTone.FOUR]
        recognize_options.interrupt_prompt = True
        recognize_options.initial_silence_timeout = 5
        recognize_options.play_prompt = play_source

        self.call_media_client.start_recognizing(recognize_options=recognize_options)

        mock_recognize.assert_called_once()

        actual_recognize_request = mock_recognize.call_args[0][1]

        expected_recognize_request = RecognizeRequest(
            recognize_input_type=recognize_options.input_type,
            play_prompt=self.call_media_client._create_play_source_internal(play_source),
            interrupt_call_media_operation=recognize_options.interrupt_call_media_operation,
            operation_context=recognize_options.operation_context,
            recognize_options=RecognizeOptions(
                target_participant=_communication_identifier_serializer.serialize_identifier(
                    recognize_options.target_participant),
                interrupt_prompt=recognize_options.interrupt_prompt,
                initial_silence_timeout_in_seconds=recognize_options.initial_silence_timeout,
                dtmf_options=DtmfOptions(
                    inter_tone_timeout_in_seconds=recognize_options.inter_tone_timeout,
                    max_tones_to_collect=recognize_options.max_tones_to_collect,
                    stop_tones=recognize_options.stop_dtmf_tones
                )
            )
        )

        self.assertEqual(expected_recognize_request.recognize_input_type, actual_recognize_request.recognize_input_type)
        self.assertEqual(expected_recognize_request.play_prompt.source_type, actual_recognize_request.play_prompt.source_type)
        self.assertEqual(expected_recognize_request.play_prompt.file_source.uri, actual_recognize_request.play_prompt.file_source.uri)
        self.assertEqual(expected_recognize_request.interrupt_call_media_operation, actual_recognize_request.interrupt_call_media_operation)
        self.assertEqual(expected_recognize_request.operation_context, actual_recognize_request.operation_context)
        self.assertEqual(expected_recognize_request.recognize_options.target_participant, actual_recognize_request.recognize_options.target_participant)
        self.assertEqual(expected_recognize_request.recognize_options.interrupt_prompt, actual_recognize_request.recognize_options.interrupt_prompt)
        self.assertEqual(expected_recognize_request.recognize_options.initial_silence_timeout_in_seconds, actual_recognize_request.recognize_options.initial_silence_timeout_in_seconds)
        self.assertEqual(expected_recognize_request.recognize_options.dtmf_options.inter_tone_timeout_in_seconds, actual_recognize_request.recognize_options.dtmf_options.inter_tone_timeout_in_seconds)
        self.assertEqual(expected_recognize_request.recognize_options.dtmf_options.max_tones_to_collect, actual_recognize_request.recognize_options.dtmf_options.max_tones_to_collect)
        self.assertEqual(expected_recognize_request.recognize_options.dtmf_options.stop_tones, actual_recognize_request.recognize_options.dtmf_options.stop_tones)


    def test_cancel(self):
        mock_cancel_all = Mock()
        self.call_media_operations.cancel_all_media_operations = mock_cancel_all

        self.call_media_client.cancel_all_media_operations()

        mock_cancel_all.assert_called_once()
        actual_call_connection_id = mock_cancel_all.call_args[0][0]
        self.assertEqual(self.call_connection_id, actual_call_connection_id)
