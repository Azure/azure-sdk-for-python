# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

import json
import unittest
from azure.communication.callautomation.streaming.models import (TranscriptionMetadata,TranscriptionData,WordData,TextFormat,ResultStatus)
from azure.communication.callautomation.streaming.streaming_data_parser import StreamingDataParser

class TestStreamDataParser(unittest.TestCase):
    def setUp(self):
        self.transcriptionMetaDataJson = '{"kind":"TranscriptionMetadata","transcriptionMetadata":{"subscriptionId":"0000a000-9999-5555-ae00-cd00e0bc0000","locale":"en-US","callConnectionId":"6d09449c-6677-4f91-8cb7-012c338e6ec1","correlationId":"6d09449c-6677-4f91-8cb7-012c338e6ec1"}}'
        self.transcriptionDataJson = '{"kind":"TranscriptionData","transcriptionData":{"text":"Is everything fine.","format":"display","confidence":0.8138430714607239,"offset":868464674,"duration":11600000,"words":[{"text":"is","offset":868464674,"duration":2400000},{"text":"everything","offset":870864674,"duration":5200000},{"text":"fine","offset":876064674,"duration":4000000}],"participantRawID":"4:+910000000000","resultStatus":"Final"}}'

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
        self.assertEqual(transcriptionMetadata.subscriptionId, "0000a000-9999-5555-ae00-cd00e0bc0000")
        self.assertEqual(transcriptionMetadata.locale, "en-US")
        self.assertEqual(transcriptionMetadata.correlationId, "6d09449c-6677-4f91-8cb7-012c338e6ec1")
        self.assertEqual(transcriptionMetadata.callConnectionId, "6d09449c-6677-4f91-8cb7-012c338e6ec1")

    def validate_transcription_data(self, transcriptionData):
        self.assertEqual(transcriptionData.text, "Is everything fine.")
        self.assertEqual(transcriptionData.format, "display")
        self.assertEqual(transcriptionData.resultStatus, "Final")
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


