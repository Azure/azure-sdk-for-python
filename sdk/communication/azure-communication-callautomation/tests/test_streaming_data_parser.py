# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

import json
import unittest
from azure.communication.callautomation._models import (
    TranscriptionMetadata,
    TranscriptionData,
    AudioMetadata,
    AudioData)
from azure.communication.callautomation._streaming_data_parser import StreamingDataParser

class TestStreamDataParser(unittest.TestCase):
    def setUp(self):
        self.transcriptionMetaDataJson = '{"kind":"TranscriptionMetadata","transcriptionMetadata":{"subscriptionId":"0000a000-9999-5555-ae00-cd00e0bc0000","locale":"en-US","callConnectionId":"6d09449c-6677-4f91-8cb7-012c338e6ec1","correlationId":"6d09449c-6677-4f91-8cb7-012c338e6ec1"}}'
        self.transcriptionDataJson = '{"kind":"TranscriptionData","transcriptionData":{"text":"Is everything fine.","format":"display","confidence":0.8138430714607239,"offset":868464674,"duration":11600000,"words":[{"text":"is","offset":868464674,"duration":2400000},{"text":"everything","offset":870864674,"duration":5200000},{"text":"fine","offset":876064674,"duration":4000000}],"participantRawID":"4:+910000000000","resultStatus":"Final"}}'
        self.audioMetadataJson = '{"kind":"AudioMetadata","audioMetadata":{"subscriptionId":"4af370df-3868-461f-8242-91f077a6f8a6","encoding":"PCM","sampleRate":16000,"channels":1,"length":640}}'
        self.audioDataJson = '{"kind":"AudioData","audioData":{"timestamp":"2024-05-30T06:25:02.948Z","data":"test","silent":false}}'
    def test_parse_binary_to_transcription_metadata(self):
        transcriptionMetaDataBinary = self.transcriptionMetaDataJson.encode('utf-8')
        parsedData = StreamingDataParser.parse(transcriptionMetaDataBinary)
        self.assertTrue(isinstance(parsedData, TranscriptionMetadata))
        self.validate_transcription_metadata(parsedData)

    def test_parse_json_to_transcription_metadata(self):
        parsedData = StreamingDataParser.parse(self.transcriptionMetaDataJson)
        self.assertTrue(isinstance(parsedData, TranscriptionMetadata))
        self.validate_transcription_metadata(parsedData)

    def test_parse_binary_to_transcription_data(self):
        transcriptionDataBinary = self.transcriptionDataJson.encode('utf-8')
        parsedData = StreamingDataParser.parse(transcriptionDataBinary)
        self.assertTrue(isinstance(parsedData, TranscriptionData))
        self.validate_transcription_data(parsedData)

    def test_parse_json_to_transcription_data(self):
        parsedData = StreamingDataParser.parse(self.transcriptionDataJson)
        self.assertTrue(isinstance(parsedData, TranscriptionData))
        self.validate_transcription_data(parsedData)

    def validate_transcription_metadata(self, transcriptionMetadata):
        self.assertEqual(transcriptionMetadata.subscription_id, "0000a000-9999-5555-ae00-cd00e0bc0000")
        self.assertEqual(transcriptionMetadata.locale, "en-US")
        self.assertEqual(transcriptionMetadata.correlation_id, "6d09449c-6677-4f91-8cb7-012c338e6ec1")
        self.assertEqual(transcriptionMetadata.call_connection_id, "6d09449c-6677-4f91-8cb7-012c338e6ec1")

    def validate_transcription_data(self, transcriptionData):
        self.assertEqual(transcriptionData.text, "Is everything fine.")
        self.assertEqual(transcriptionData.format, "display")
        self.assertEqual(transcriptionData.result_state, "Final")
        self.assertAlmostEqual(transcriptionData.confidence, 0.8138430714607239)
        self.assertEqual(transcriptionData.offset, 868464674)
        self.assertEqual(transcriptionData.duration, 11600000)
        self.assertEqual(len(transcriptionData.words), 3)
        self.assertEqual(transcriptionData.words[0].text, "is")
        self.assertEqual(transcriptionData.words[0].offset, 868464674)
        self.assertEqual(transcriptionData.words[0].duration, 2400000)
        self.assertEqual(transcriptionData.words[1].text, "everything")
        self.assertEqual(transcriptionData.words[1].offset, 870864674)
        self.assertEqual(transcriptionData.words[1].duration, 5200000)
        self.assertEqual(transcriptionData.words[2].text, "fine")
        self.assertEqual(transcriptionData.words[2].offset, 876064674)
        self.assertEqual(transcriptionData.words[2].duration, 4000000)
        self.assertEqual(transcriptionData.participant.raw_id, "4:+910000000000")

    def test_parse_json_to_audio_metadata(self):
        parsedData = StreamingDataParser.parse(self.audioMetadataJson)
        self.assertTrue(isinstance(parsedData, AudioMetadata))
        self.validate_audio_metadata(parsedData)

    def test_parse_binary_to_audio_metadata(self):
        audioMetadataBinary = self.audioMetadataJson.encode('utf-8')
        parsedData = StreamingDataParser.parse(audioMetadataBinary)
        self.assertTrue(isinstance(parsedData, AudioMetadata))
        self.validate_audio_metadata(parsedData)

    def test_parse_json_to_audio_data(self):
        parsedData = StreamingDataParser.parse(self.audioDataJson)
        self.assertTrue(isinstance(parsedData, AudioData))
        self.validate_audio_data(parsedData)

    def test_parse_binary_to_audio_data(self):
        audioDataBinary = self.audioDataJson.encode('utf-8')
        parsedData = StreamingDataParser.parse(audioDataBinary)
        self.assertTrue(isinstance(parsedData, AudioData))
        self.validate_audio_data(parsedData)
        
    def validate_audio_metadata(self, audioMetadata):
        self.assertEqual(audioMetadata.subscription_id,'4af370df-3868-461f-8242-91f077a6f8a6')
        self.assertEqual(audioMetadata.encoding,'PCM')
        self.assertEqual(audioMetadata.sample_rate,16000)
        self.assertEqual(audioMetadata.channels,1)
        self.assertEqual(audioMetadata.length,640)
    
    def validate_audio_data(self, audioData):
        self.assertEqual(audioData.data,"test")
        self.assertEqual(audioData.is_silent,False)
        