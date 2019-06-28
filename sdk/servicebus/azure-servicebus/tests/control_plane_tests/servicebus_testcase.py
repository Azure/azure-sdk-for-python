# coding: utf-8

#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------

import os.path
from testutils.common_recordingtestcase import (
    RecordingTestCase,
    TestMode,
)
from . import servicebus_settings_fake as fake_settings


class ServiceBusTestCase(RecordingTestCase):

    def setUp(self):
        self.working_folder = os.path.dirname(__file__)

        super(ServiceBusTestCase, self).setUp()

        self.fake_settings = fake_settings
        if TestMode.is_playback(self.test_mode):
            self.settings = self.fake_settings
        else:
            import tests.servicebus_settings_real as real_settings  # pylint: disable=import-error,no-name-in-module
            self.settings = real_settings

    def _set_service_options(self, service, settings):  # pylint: disable=no-self-use
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
