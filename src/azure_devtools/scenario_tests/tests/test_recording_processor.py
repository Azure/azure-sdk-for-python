# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import unittest
from azure_devtools.scenario_tests.recording_processors import RecordingProcessor


class TestRecordingProcessors(unittest.TestCase):
    def test_recording_processor_base_class(self):
        rp = RecordingProcessor()
        request_sample = {'url': 'https://www.bing,com', 'headers': {'beta': ['value_1', 'value_2']}}
        response_sample = {'body': 'something', 'headers': {'charlie': ['value_3']}}
        self.assertIs(request_sample, rp.process_request(request_sample))  # reference equality
        self.assertIs(response_sample, rp.process_response(response_sample))

        rp.replace_header(request_sample, 'beta', 'value_1', 'replaced_1')
        self.assertSequenceEqual(request_sample['headers']['beta'], ['replaced_1', 'value_2'])

        rp.replace_header(request_sample, 'Beta', 'replaced_1', 'replaced_2')  # case insensitive
        self.assertSequenceEqual(request_sample['headers']['beta'], ['replaced_2', 'value_2'])

        rp.replace_header(request_sample, 'alpha', 'replaced_1', 'replaced_2')  # ignore KeyError
        self.assertSequenceEqual(request_sample['headers']['beta'], ['replaced_2', 'value_2'])

        rp.replace_header_fn(request_sample, 'beta', lambda v: 'customized')
        self.assertSequenceEqual(request_sample['headers']['beta'], ['customized', 'customized'])
