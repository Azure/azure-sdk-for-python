#-------------------------------------------------------------------------
# Copyright (c) Microsoft.  All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#--------------------------------------------------------------------------
from contextlib import contextmanager
import copy
import inspect
import json
import os
import os.path
import random
import unittest

import requests
import vcr

from azure.common import SubscriptionCloudCredentials

should_log = os.getenv('SDK_TESTS_LOG', '0')
if should_log.lower() == 'true' or should_log == '1':
    import logging
    logger = logging.getLogger('azure.common.filters')
    logger.setLevel(logging.DEBUG)
    logger.addHandler(logging.StreamHandler())


class TestMode(object):
    none = 'None' # this will be for unit test, no need for any recordings
    playback = 'Playback'
    record = 'Record'
    run_live_no_record = 'RunLiveNoRecord'

    @staticmethod
    def is_playback(mode):
        return mode.lower() == TestMode.playback.lower()

    @staticmethod
    def need_recordingfile(mode):
        mode_lower = mode.lower()
        return mode_lower == TestMode.playback.lower() or mode_lower == TestMode.record.lower()

    @staticmethod
    def need_real_credentials(mode):
        mode_lower = mode.lower()
        return mode_lower == TestMode.run_live_no_record.lower() or mode_lower == TestMode.record.lower()

class HttpStatusCode(object):
    OK = 200
    Created = 201
    Accepted = 202
    NoContent = 204
    NotFound = 404

class RecordingTestCase(unittest.TestCase):

    def __init__(self, *args, **kwargs):
        super(RecordingTestCase, self).__init__(*args, **kwargs)
        try:
            with open(os.path.join('tests', 'testsettings_local.json')) as testsettings_local_file:
                test_settings = json.load(testsettings_local_file)
            self.test_mode = test_settings['mode']
        except:
            pass
        
        if getattr(self, 'test_mode', None) is None:
            self.test_mode = TestMode.playback

    def setUp(self):
        super(RecordingTestCase, self).setUp()

        # example of qualified test name:
        # test_mgmt_network.test_public_ip_addresses
        _, filename = os.path.split(inspect.getsourcefile(type(self)))
        name, _ = os.path.splitext(filename)
        self.qualified_test_name = '{0}.{1}'.format(
            name,
            self._testMethodName,
        )

    def is_playback(self):
        return TestMode.is_playback(self.test_mode)

    def get_token_based_credential(self):

        with open(get_test_file_path(os.path.join('credentials_mock.json'))) as credential_file:
            self.credential_mock = json.load(credential_file)

        if TestMode.is_playback(self.test_mode):
            credential = self.credential_mock
        else:
            with open(get_test_file_path(os.path.join('credentials_real.json'))) as credential_file:
                credential = json.load(credential_file)

        session = requests.Session()
        if TestMode.need_real_credentials(self.test_mode):
            credential['token'] = credential['authorization_header'].split()[1]
        else:
            credential['token'] = 'faked_token'

        self.subscription_id = credential['subscriptionid']
        azure_cred = SubscriptionCloudCredentials(credential['subscriptionid'], 
                                                  credential['token'])
        return azure_cred

    def recording(self):
        if TestMode.need_recordingfile(self.test_mode):
            cassette_name = '{0}.yaml'.format(self.qualified_test_name)

            my_vcr = vcr.VCR(
                before_record_request = self._scrub_sensitive_request_info,
                before_record_response = self._scrub_sensitive_response_info,
                record_mode = 'none' if TestMode.is_playback(self.test_mode) else 'all'
            )

            return my_vcr.use_cassette(
                get_test_file_path(os.path.join('recordings', cassette_name)),
                filter_headers=['authorization'],
            )
        else:
            return self._nop_context_manager()

    def get_resource_name(self, name):
        if self.test_mode == TestMode.run_live_no_record:
            # Running against a live server, not recording. Waiting for
            # resources to be deleted from a previous run is very slow.
            # Randomize the name a little so that we don't conflict with
            # resources from a previous run which may still be deleting.
            return name + str(random.Random().randint(100, 999))
        else:
            # Recording or playing back, so use a fixed name
            return name

    def _scrub_sensitive_request_info(self, request):
        if not TestMode.is_playback(self.test_mode):
            request.uri = self._scrub(request.uri)
            if request.body is not None:
                request.body = self._scrub(request.body)
        return request

    def _scrub_sensitive_response_info(self, response):
        if not TestMode.is_playback(self.test_mode):
            # We need to make a copy because vcr doesn't make one for us.
            # Without this, changing the contents of the dicts would change
            # the contents returned to the caller - not just the contents
            # getting saved to disk. That would be a problem with headers
            # such as 'location', often used in the request uri of a
            # subsequent service call.
            response = copy.deepcopy(response)
            headers = response.get('headers')
            if headers:
                for name, val in headers.items():
                    for i in range(len(val)):
                        val[i] = self._scrub(val[i])
        return response

    def _scrub(self, val):
        return val.replace(self.subscription_id, self.credential_mock['subscriptionid'])

    @contextmanager
    def _nop_context_manager(self):
        yield


def get_test_file_path(relative_path):
    base_path = os.path.dirname(__file__)
    absolute_path = os.path.join(base_path, relative_path)
    return absolute_path
