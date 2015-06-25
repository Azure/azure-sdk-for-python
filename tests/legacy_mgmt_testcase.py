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
from .common_recordingtestcase import (
    RecordingTestCase,
    TestMode,
)
from . import legacy_mgmt_settings_fake as fake_settings
from .util import (
    set_service_options,
)


class LegacyMgmtTestCase(RecordingTestCase):

    def setUp(self):
        super(LegacyMgmtTestCase, self).setUp()

        self.fake_settings = fake_settings
        if TestMode.is_playback(self.test_mode):
            self.settings = self.fake_settings
        else:
            from . import legacy_mgmt_settings_real as real_settings
            self.settings = real_settings

    def _scrub(self, val):
        val = super(LegacyMgmtTestCase, self)._scrub(val)
        real_to_fake_dict = {
            self.settings.SUBSCRIPTION_ID: self.fake_settings.SUBSCRIPTION_ID,
            self.settings.STORAGE_ACCOUNT_NAME: self.fake_settings.STORAGE_ACCOUNT_NAME,
            self.settings.STORAGE_ACCOUNT_KEY: self.fake_settings.STORAGE_ACCOUNT_KEY,
            self.settings.SERVICEBUS_NAME: self.fake_settings.SERVICEBUS_NAME,
            self.settings.LINUX_OS_VHD: self.fake_settings.LINUX_OS_VHD,
            self.settings.LINUX_VM_REMOTE_SOURCE_IMAGE_LINK: self.fake_settings.LINUX_VM_REMOTE_SOURCE_IMAGE_LINK,
            self.settings.LINUX_VM_IMAGE_NAME: self.fake_settings.LINUX_VM_IMAGE_NAME,
        }
        val = self._scrub_using_dict(val, real_to_fake_dict)
        return val

    def create_service_management(self, service_class):
        conn_type = self.settings.CONNECTION_TYPE
        if conn_type == 'requests_with_token' or conn_type == 'requests_with_cert':
            import requests
            session = requests.Session()
            if conn_type == 'requests_with_token':
                auth = 'Bearer {}'.format(self.settings.get_token())
                session.headers['authorization'] = auth
            else:
                # Note this works only with RunLiveNoRecord
                session.cert = self.settings.PEM_PATH
            service = service_class(
                self.settings.SUBSCRIPTION_ID,
                request_session=session,
            )
        elif conn_type == 'winhttp':
            # Note this works only with RunLiveNoRecord
            service = service_class(
                self.settings.SUBSCRIPTION_ID,
                self.settings.PFX_LOCATION,
            )
        elif conn_type == 'httplib':
            # Note this works only with RunLiveNoRecord
            service = service_class(
                self.settings.SUBSCRIPTION_ID,
                self.settings.PEM_PATH,
            )
        else:
            raise ValueError('Insupported value for "connectiontype" in settings:"{}"'.format(conn_type))
        set_service_options(service, self.settings)
        return service
