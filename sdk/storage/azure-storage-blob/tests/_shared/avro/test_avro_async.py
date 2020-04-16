
# coding: utf-8
# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

import inspect
import os
import pytest
import unittest
from azure.storage.blob._shared.avro.avro_io_async import AsyncDatumReader
from azure.storage.blob._shared.avro.datafile_async import AsyncDataFileReader

from .test_avro import SCHEMAS_TO_VALIDATE

CODECS_TO_VALIDATE = ['null']


class AsyncBufferedReaderWrapper:
    def __init__(self, reader):
        self._reader = reader

    async def seek(self, offset, whence=0):
        self._reader.seek(offset, whence)

    async def read(self, size=None):
        return self._reader.read(size)

    def close(self):
        self._reader.close()


class AvroReaderTestsAsync(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        test_file_path = inspect.getfile(cls)
        cls._samples_dir_root = os.path.join(os.path.dirname(test_file_path), 'samples')

    @pytest.mark.asyncio
    async def test_reader(self):
        correct = 0
        nitems = 10
        for iexample, (writer_schema, datum) in enumerate(SCHEMAS_TO_VALIDATE):
            for codec in CODECS_TO_VALIDATE:
                file_path = os.path.join(AvroReaderTestsAsync._samples_dir_root, 'test_' + codec + '_' + str(iexample) + '.avro')
                with open(file_path, 'rb') as reader:
                    datum_reader = AsyncDatumReader()
                    async_reader = AsyncBufferedReaderWrapper(reader)
                    async with await AsyncDataFileReader(async_reader, datum_reader).init() as dfr:
                        round_trip_data = []
                        async for x in dfr:
                            round_trip_data.append(x)
                        if ([datum] * nitems) == round_trip_data:
                            correct += 1
        self.assertEqual(
            correct,
            len(CODECS_TO_VALIDATE) * len(SCHEMAS_TO_VALIDATE))

    @pytest.mark.asyncio
    async def test_change_feed(self):
        file_path = os.path.join(AvroReaderTestsAsync._samples_dir_root, 'changeFeed.avro')
        with open(file_path, 'rb') as reader:
            datum_reader = AsyncDatumReader()
            async_reader = AsyncBufferedReaderWrapper(reader)
            async with await AsyncDataFileReader(async_reader, datum_reader).init() as dfr:
                data = []
                async for x in dfr:
                    data.append(x)
                self.assertEqual(1, len(data))
                expectedRecord = {
                    'data': {
                        'api': 'PutBlob',
                        'blobPropertiesUpdated': None,
                        'blobType': 'BlockBlob',
                        'clientRequestId': '75b6c460-fcd0-11e9-87e2-85def057dae9',
                        'contentLength': 12,
                        'contentType': 'text/plain',
                        'etag': '0x8D75EF45A3B8617',
                        'previousInfo': None,
                        'requestId': 'bb219c8e-401e-0028-1fdd-90f393000000',
                        'sequencer': '000000000000000000000000000017140000000000000fcc',
                        'snapshot': None,
                        'storageDiagnostics': {'bid': 'd3053fa1-a006-0042-00dd-902bbb000000',
                                               'seq': '(5908,134,4044,0)',
                                               'sid': '5aaf98bf-f1d8-dd76-2dd2-9b60c689538d'},
                        'url': ''},
                    'eventTime': '2019-11-01T17:53:07.5106080Z',
                    'eventType': 'BlobCreated',
                    'id': 'bb219c8e-401e-0028-1fdd-90f393069ae4',
                    'schemaVersion': 3,
                    'subject': '/blobServices/default/containers/test/blobs/sdf.txt',
                    'topic': '/subscriptions/ba45b233-e2ef-4169-8808-49eb0d8eba0d/resourceGroups/XClient/providers/Microsoft.Storage/storageAccounts/seanchangefeedstage'}
                self.assertEqual(expectedRecord, data[0])