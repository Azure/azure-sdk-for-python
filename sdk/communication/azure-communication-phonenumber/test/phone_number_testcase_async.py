# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import os
from azure.communication.administration._shared.utils import parse_connection_str
from phone_number_testcase import PhoneNumberCommunicationTestCase
from _shared.asynctestcase import AsyncCommunicationTestCase

class AsyncPhoneNumberCommunicationTestCase(PhoneNumberCommunicationTestCase, AsyncCommunicationTestCase):
    def setUp(self):
        super(AsyncPhoneNumberCommunicationTestCase, self).setUp()
