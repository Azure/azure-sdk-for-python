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
import unittest

from azure.servicemanagement import ServiceManagementService
from azuretest.util import (AzureTestCase,
                            credentials, 
                            getUniqueTestRunID,
                            getUniqueNameBasedOnCurrentTime,
                            )

MANAGEMENT_CERT_PUBLICKEY = 'MIIBCgKCAQEAsjULNM53WPLkht1rbrDob/e4hZTHzj/hlLoBt2X3cNRc6dOPsMucxbMdchbCqAFa5RIaJvF5NDKqZuUSwq6bttD71twzy9bQ03EySOcRBad1VyqAZQ8DL8nUGSnXIUh+tpz4fDGM5f3Ly9NX8zfGqG3sT635rrFlUp3meJC+secCCwTLOOcIs3KQmuB+pMB5Y9rPhoxcekFfpq1pKtis6pmxnVbiL49kr6UUL6RQRDwik4t1jttatXLZqHETTmXl0Y0wS5AcJUXVAn5AL2kybULoThop2v01/E0NkPtFPAqLVs/kKBahniNn9uwUo+LS9FA8rWGu0FY4CZEYDfhb+QIDAQAB'
MANAGEMENT_CERT_DATA = 'MIIC9jCCAeKgAwIBAgIQ00IFaqV9VqVJxI+wZka0szAJBgUrDgMCHQUAMBUxEzARBgNVBAMTClB5dGhvblRlc3QwHhcNMTIwODMwMDAyNTMzWhcNMzkxMjMxMjM1OTU5WjAVMRMwEQYDVQQDEwpQeXRob25UZXN0MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAsjULNM53WPLkht1rbrDob/e4hZTHzj/hlLoBt2X3cNRc6dOPsMucxbMdchbCqAFa5RIaJvF5NDKqZuUSwq6bttD71twzy9bQ03EySOcRBad1VyqAZQ8DL8nUGSnXIUh+tpz4fDGM5f3Ly9NX8zfGqG3sT635rrFlUp3meJC+secCCwTLOOcIs3KQmuB+pMB5Y9rPhoxcekFfpq1pKtis6pmxnVbiL49kr6UUL6RQRDwik4t1jttatXLZqHETTmXl0Y0wS5AcJUXVAn5AL2kybULoThop2v01/E0NkPtFPAqLVs/kKBahniNn9uwUo+LS9FA8rWGu0FY4CZEYDfhb+QIDAQABo0owSDBGBgNVHQEEPzA9gBBS6knRHo54LppngxVCCzZVoRcwFTETMBEGA1UEAxMKUHl0aG9uVGVzdIIQ00IFaqV9VqVJxI+wZka0szAJBgUrDgMCHQUAA4IBAQAnZbP3YV+08wI4YTg6MOVA+j1njd0kVp35FLehripmaMNE6lgk3Vu1MGGl0JnvMr3fNFGFzRske/jVtFxlHE5H/CoUzmyMQ+W06eV/e995AduwTKsS0ZgYn0VoocSXWst/nyhpKOcbJgAOohOYxgsGI1JEqQgjyeqzcCIhw/vlWiA3V8bSiPnrC9vwhH0eB025hBd2VbEGDz2nWCYkwtuOLMTvkmLi/oFw3GOfgagZKk8k/ZPffMCafz+yR3vb1nqAjncrVcJLI8amUfpxhjZYexo8MbxBA432M6w8sjXN+uLCl7ByWZ4xs4vonWgkmjeObtU37SIzolHT4dxIgaP2'

#------------------------------------------------------------------------------
class ManagementCertificateManagementServiceTest(AzureTestCase):

    def setUp(self):
        proxy_host = credentials.getProxyHost()
        proxy_port = credentials.getProxyPort()

        self.sms = ServiceManagementService(credentials.getSubscriptionId(), credentials.getManagementCertFile())
        if proxy_host:
            self.sms.set_proxy(proxy_host, proxy_port)

        self.management_certificate_name = getUniqueNameBasedOnCurrentTime('utmgmtcert')

    def tearDown(self):
        try:
            self.sms.delete_management_certificate(self.management_certificate_name)
        except: pass

    #--Helpers-----------------------------------------------------------------
    def _create_management_certificate(self, thumbprint):
        result = self.sms.add_management_certificate(MANAGEMENT_CERT_PUBLICKEY, thumbprint, MANAGEMENT_CERT_DATA)
        self.assertIsNone(result)

    def _management_certificate_exists(self, thumbprint):
        try:
            props = self.sms.get_management_certificate(thumbprint)
            return props is not None
        except:
            return False

    #--Test cases for management certificates ----------------------------
    def test_list_management_certificates(self):
        # Arrange
        self._create_management_certificate(self.management_certificate_name)

        # Act
        result = self.sms.list_management_certificates()

        # Assert
        self.assertIsNotNone(result)
        self.assertTrue(len(result) > 0)
        
        cert = None
        for temp in result:
            if temp.subscription_certificate_thumbprint == self.management_certificate_name:
                cert = temp
                break

        self.assertIsNotNone(cert)
        self.assertIsNotNone(cert.created)
        self.assertEqual(cert.subscription_certificate_public_key, MANAGEMENT_CERT_PUBLICKEY)
        self.assertEqual(cert.subscription_certificate_data, MANAGEMENT_CERT_DATA)
        self.assertEqual(cert.subscription_certificate_thumbprint, self.management_certificate_name)

    def test_get_management_certificate(self):
        # Arrange
        self._create_management_certificate(self.management_certificate_name)

        # Act
        result = self.sms.get_management_certificate(self.management_certificate_name)

        # Assert
        self.assertIsNotNone(result)
        self.assertIsNotNone(result.created)
        self.assertEqual(result.subscription_certificate_public_key, MANAGEMENT_CERT_PUBLICKEY)
        self.assertEqual(result.subscription_certificate_data, MANAGEMENT_CERT_DATA)
        self.assertEqual(result.subscription_certificate_thumbprint, self.management_certificate_name)

    def test_add_management_certificate(self):
        # Arrange
        public_key = MANAGEMENT_CERT_PUBLICKEY
        data = MANAGEMENT_CERT_DATA

        # Act
        result = self.sms.add_management_certificate(public_key, self.management_certificate_name, data)

        # Assert
        self.assertIsNone(result)
        self.assertTrue(self._management_certificate_exists(self.management_certificate_name))

    def test_delete_management_certificate(self):
        # Arrange
        self._create_management_certificate(self.management_certificate_name)

        # Act
        result = self.sms.delete_management_certificate(self.management_certificate_name)

        # Assert
        self.assertIsNone(result)
        self.assertFalse(self._management_certificate_exists(self.management_certificate_name))

#------------------------------------------------------------------------------
if __name__ == '__main__':
    unittest.main()
