# coding: utf-8
# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

import unittest
from azure.communication.rooms._shared.policy import HMACCredentialsPolicy
from devtools_testutils import AzureTestCase

class HMACTest(AzureTestCase):
    def setUp(self):
        super(HMACTest, self).setUp()

    def test_correct_hmac(self):
        auth_policy = HMACCredentialsPolicy("contoso.communicationservices.azure.com", "pw==")

        sha_val = auth_policy._compute_hmac("banana")
        assert sha_val == "88EC05aAS9iXnaimtNO78JLjiPtfWryQB/5QYEzEsu8="

    def test_correct_utf16_hmac(self):
        auth_policy = HMACCredentialsPolicy("contoso.communicationservices.azure.com", "pw==")

        sha_val = auth_policy._compute_hmac(u"😀")

        assert sha_val == "1rudJKjn2Zi+3hRrBG29wIF6pD6YyAeQR1ZcFtXoKAU=" 