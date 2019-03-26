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
from requests import Session
from testutils.common_recordingtestcase import (
    RecordingTestCase,
    TestMode,
)
import tests.legacy_mgmt_settings_fake as fake_settings


class LegacyMgmtTestCase(RecordingTestCase):

    def setUp(self):
        self.working_folder = os.path.dirname(__file__)

        super(LegacyMgmtTestCase, self).setUp()

        self.fake_settings = fake_settings
        if TestMode.is_playback(self.test_mode):
            self.settings = self.fake_settings
        else:
            import tests.legacy_mgmt_settings_real as real_settings
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
            if conn_type == 'requests_with_token':
                import requests
                session = requests.Session()
                credentials = self.settings.get_credentials()
                auth = 'Bearer {}'.format(credentials.token['access_token'])
                session.headers['authorization'] = auth
                service = service_class(
                    self.settings.SUBSCRIPTION_ID,
                    request_session=session,
                )
            else:
                # Note this works only with RunLiveNoRecord
                service = service_class(
                    self.settings.SUBSCRIPTION_ID,
                    self.settings.PEM_PATH,
                )
        elif conn_type == 'winhttp':
            # Note this works only with RunLiveNoRecord
            service = service_class(
                self.settings.SUBSCRIPTION_ID,
                self.settings.PFX_LOCATION,
            )
        else:
            raise ValueError('Insupported value for "connectiontype" in settings:"{}"'.format(conn_type))
        self._set_service_options(service, self.settings)
        return service

    def _create_storage_service(self, service_class, settings, account_name=None, account_key=None):
        account_name = account_name or settings.STORAGE_ACCOUNT_NAME
        account_key = account_key or settings.STORAGE_ACCOUNT_KEY
        session = Session()
        service = service_class(
            account_name,
            account_key,
            request_session=session,
        )
        self._set_service_options(service, settings)
        return service

    def _set_service_options(self, service, settings):
        if settings.USE_PROXY:
            service.set_proxy(
                settings.PROXY_HOST,
                settings.PROXY_PORT,
                settings.PROXY_USER,
                settings.PROXY_PASSWORD,
            )
