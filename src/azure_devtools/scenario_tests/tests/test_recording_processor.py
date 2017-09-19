# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import json
try:
    import unittest.mock as mock
except ImportError:
    import mock
import unittest
import uuid

from azure_devtools.scenario_tests.recording_processors import (
    RecordingProcessor, SubscriptionRecordingProcessor, AccessTokenReplacer
)


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

    def test_access_token_processor(self):
        replaced_subscription_id = 'test_fake_token'
        rp = AccessTokenReplacer(replaced_subscription_id)

        TOKEN_STR = '{"token_type": "Bearer", "resource": "url", "access_token": "real_token"}'
        token_response_sample = {'body': {'string': TOKEN_STR}}

        self.assertEqual(json.loads(rp.process_response(token_response_sample)['body']['string'])['access_token'],
                         replaced_subscription_id)

        no_token_response_sample = {'body': {'string': '{"location": "westus"}'}}
        self.assertDictEqual(rp.process_response(no_token_response_sample), no_token_response_sample)

    @staticmethod
    def _mock_subscription_request_body(mock_sub_id):
        return json.dumps({
            "location": "westus",
            "properties": {
                "ipConfigurations": [
                    {
                        "properties": {
                            "subnet": {"id": "/Subscriptions/{}/resourceGroups/etc".format(mock_sub_id)},
                            "name": "azure-sample-ip-config"
                        }
                    },
                ]
            }
        }).encode()

    def test_subscription_recording_processor_for_request(self):
        replaced_subscription_id = str(uuid.uuid4())
        rp = SubscriptionRecordingProcessor(replaced_subscription_id)

        uri_templates = ['https://management.azure.com/subscriptions/{}/providers/Microsoft.ContainerRegistry/'
                         'checkNameAvailability?api-version=2017-03-01',
                         'https://graph.windows.net/{}/applications?api-version=1.6']

        for template in uri_templates:
            mock_sub_id = str(uuid.uuid4())
            mock_request = mock.Mock()
            mock_request.uri = template.format(mock_sub_id)
            mock_request.body = self._mock_subscription_request_body(mock_sub_id)

            rp.process_request(mock_request)
            self.assertEqual(mock_request.uri, template.format(replaced_subscription_id))
            self.assertEqual(mock_request.body,
                             self._mock_subscription_request_body(replaced_subscription_id))

    def test_subscription_recording_processor_for_response(self):
        replaced_subscription_id = str(uuid.uuid4())
        rp = SubscriptionRecordingProcessor(replaced_subscription_id)

        body_templates = ['https://management.azure.com/subscriptions/{}/providers/Microsoft.ContainerRegistry/'
                          'checkNameAvailability?api-version=2017-03-01',
                          'https://graph.Windows.net/{}/applications?api-version=1.6',
                          "{{'scope':'/subscriptions/{}', 'another_data':'/Microsoft.Something'}}"]

        location_header_template = 'https://graph.windows.net/{}/directoryObjects/' \
                                   'f604c53a-aa21-44d5-a41f-c1ef0b5304bd/Microsoft.DirectoryServices.Application'

        asyncoperation_header_template = 'https://management.azure.com/subscriptions/{}/resourceGroups/' \
                                         'clitest.rg000001/providers/Microsoft.Sql/servers/clitestserver000002/' \
                                         'databases/cliautomationdb01/azureAsyncOperation/' \
                                         '6ec6196b-fbaa-415f-8c1a-6cb634a96cb2?api-version=2014-04-01-Preview'

        for template in body_templates:
            mock_sub_id = str(uuid.uuid4())
            mock_response = dict({'body': {}})
            mock_response['body']['string'] = template.format(mock_sub_id)
            mock_response['headers'] = {'Location': [location_header_template.format(mock_sub_id)],
                                        'azure-asyncoperation': [asyncoperation_header_template.format(mock_sub_id)]}
            rp.process_response(mock_response)
            self.assertEqual(mock_response['body']['string'], template.format(replaced_subscription_id))

            self.assertSequenceEqual(mock_response['headers']['Location'],
                                     [location_header_template.format(replaced_subscription_id)])
            self.assertSequenceEqual(mock_response['headers']['azure-asyncoperation'],
                                     [asyncoperation_header_template.format(replaced_subscription_id)])
