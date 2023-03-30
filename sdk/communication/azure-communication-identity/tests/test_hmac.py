# coding: utf-8
# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import unittest
from azure.communication.identity._shared.policy import HMACCredentialsPolicy
from devtools_testutils import AzureTestCase
from azure.communication.identity._shared.utils import get_current_utc_time
from azure.core.pipeline import PipelineRequest, PipelineContext
from azure.core.rest import HttpRequest

class HMACTest(AzureTestCase):
    def setUp(self):
        super(HMACTest, self).setUp()

    def test_correct_hmac(self):
        auth_policy = HMACCredentialsPolicy("https://contoso.communicationservices.azure.com", "pw==")

        sha_val = auth_policy._compute_hmac("banana")
        #[SuppressMessage("Microsoft.Security", "CS002:SecretInNextLine", Justification="unit test with fake keys")]
        assert sha_val == "88EC05aAS9iXnaimtNO78JLjiPtfWryQB/5QYEzEsu8="

    def test_correct_utf16_hmac(self):
        auth_policy = HMACCredentialsPolicy("https://contoso.communicationservices.azure.com", "pw==")

        sha_val = auth_policy._compute_hmac(u"😀")
        #[SuppressMessage("Microsoft.Security", "CS002:SecretInNextLine", Justification="unit test with fake keys")]
        assert sha_val == "1rudJKjn2Zi+3hRrBG29wIF6pD6YyAeQR1ZcFtXoKAU=" 

    def mocked_get_current_utc_time():
        return "Wed, 13 Apr 2022 18:09:12 GMT"

    @unittest.mock.patch('azure.communication.identity._shared.policy.get_current_utc_time', mocked_get_current_utc_time)
    def test_correct_signature(self):
        auth_policy = HMACCredentialsPolicy("https://contoso.communicationservices.azure.com", "pw==")

        test_request = HttpRequest(method = "GET", url = "https://contoso.communicationservices.azure.com/")
        request = PipelineRequest(test_request, PipelineContext(None))
        signature = auth_policy._sign_request(request).http_request.headers['Authorization']

        assert "HMAC-SHA256 SignedHeaders=x-ms-date;host;x-ms-content-sha256&Signature=88MDmJhUR3m5QhFxb8ztShsSwlGrg7g/6XPnWf7QEO4=" == signature

    @unittest.mock.patch('azure.communication.identity._shared.policy.get_current_utc_time', mocked_get_current_utc_time)
    def test_correct_signature_with_path(self):
        auth_policy = HMACCredentialsPolicy("https://contoso.communicationservices.azure.com", "pw==")

        test_request = HttpRequest(method = "GET", url = "https://contoso.communicationservices.azure.com/testPath")
        request = PipelineRequest(test_request, PipelineContext(None))
        signature = auth_policy._sign_request(request).http_request.headers['Authorization']

        assert "HMAC-SHA256 SignedHeaders=x-ms-date;host;x-ms-content-sha256&Signature=RoCrHjw7fb9fpHSbqvRUY2xa8RBS0YvI1cxI1x8AS38=" == signature

    @unittest.mock.patch('azure.communication.identity._shared.policy.get_current_utc_time', mocked_get_current_utc_time)
    def test_correct_signature_with_path_and_host(self):
        auth_policy = HMACCredentialsPolicy("https://contoso.communicationservices.azure.com", "pw==")

        test_request = HttpRequest(method = "GET", url = "https://contoso.communicationservices.azure.com/testPath?testQuery=yes")
        request = PipelineRequest(test_request, PipelineContext(None))
        signature = auth_policy._sign_request(request).http_request.headers['Authorization']

        assert "HMAC-SHA256 SignedHeaders=x-ms-date;host;x-ms-content-sha256&Signature=il99+rd6V5O136roX/zVePCNle78HmvC4B7tu9zRH3I=" == signature
