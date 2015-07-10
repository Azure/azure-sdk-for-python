# coding: utf-8

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
import os.path
from testutils.common_recordingtestcase import (
    RecordingTestCase,
    TestMode,
)
import tests.servicebus_settings_fake as fake_settings


class ServiceBusTestCase(RecordingTestCase):

    def setUp(self):
        self.working_folder = os.path.dirname(__file__)

        super(ServiceBusTestCase, self).setUp()

        self.fake_settings = fake_settings
        if TestMode.is_playback(self.test_mode):
            self.settings = self.fake_settings
        else:
            import tests.servicebus_settings_real as real_settings
            self.settings = real_settings

    def _set_service_options(self, service, settings):
        if settings.USE_PROXY:
            service.set_proxy(
                settings.PROXY_HOST,
                settings.PROXY_PORT,
                settings.PROXY_USER,
                settings.PROXY_PASSWORD,
            )

    def _scrub(self, val):
        val = super(ServiceBusTestCase, self)._scrub(val)
        real_to_fake_dict = {
            self.settings.SERVICEBUS_NAME: self.fake_settings.SERVICEBUS_NAME,
            self.settings.EVENTHUB_NAME: self.fake_settings.EVENTHUB_NAME,
        }
        val = self._scrub_using_dict(val, real_to_fake_dict)
        return val
