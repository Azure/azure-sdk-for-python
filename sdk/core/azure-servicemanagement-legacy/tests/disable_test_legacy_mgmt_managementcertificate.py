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
from testutils.common_recordingtestcase import (
    TestMode,
    record,
)
from tests.legacy_mgmt_testcase import LegacyMgmtTestCase


MANAGEMENT_CERT_PUBLICKEY = 'MIIBCgKCAQEAsjULNM53WPLkht1rbrDob/e4hZTHzj/hlLoBt2X3cNRc6dOPsMucxbMdchbCqAFa5RIaJvF5NDKqZuUSwq6bttD71twzy9bQ03EySOcRBad1VyqAZQ8DL8nUGSnXIUh+tpz4fDGM5f3Ly9NX8zfGqG3sT635rrFlUp3meJC+secCCwTLOOcIs3KQmuB+pMB5Y9rPhoxcekFfpq1pKtis6pmxnVbiL49kr6UUL6RQRDwik4t1jttatXLZqHETTmXl0Y0wS5AcJUXVAn5AL2kybULoThop2v01/E0NkPtFPAqLVs/kKBahniNn9uwUo+LS9FA8rWGu0FY4CZEYDfhb+QIDAQAB'
MANAGEMENT_CERT_DATA = 'MIIC9jCCAeKgAwIBAgIQ00IFaqV9VqVJxI+wZka0szAJBgUrDgMCHQUAMBUxEzARBgNVBAMTClB5dGhvblRlc3QwHhcNMTIwODMwMDAyNTMzWhcNMzkxMjMxMjM1OTU5WjAVMRMwEQYDVQQDEwpQeXRob25UZXN0MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAsjULNM53WPLkht1rbrDob/e4hZTHzj/hlLoBt2X3cNRc6dOPsMucxbMdchbCqAFa5RIaJvF5NDKqZuUSwq6bttD71twzy9bQ03EySOcRBad1VyqAZQ8DL8nUGSnXIUh+tpz4fDGM5f3Ly9NX8zfGqG3sT635rrFlUp3meJC+secCCwTLOOcIs3KQmuB+pMB5Y9rPhoxcekFfpq1pKtis6pmxnVbiL49kr6UUL6RQRDwik4t1jttatXLZqHETTmXl0Y0wS5AcJUXVAn5AL2kybULoThop2v01/E0NkPtFPAqLVs/kKBahniNn9uwUo+LS9FA8rWGu0FY4CZEYDfhb+QIDAQABo0owSDBGBgNVHQEEPzA9gBBS6knRHo54LppngxVCCzZVoRcwFTETMBEGA1UEAxMKUHl0aG9uVGVzdIIQ00IFaqV9VqVJxI+wZka0szAJBgUrDgMCHQUAA4IBAQAnZbP3YV+08wI4YTg6MOVA+j1njd0kVp35FLehripmaMNE6lgk3Vu1MGGl0JnvMr3fNFGFzRske/jVtFxlHE5H/CoUzmyMQ+W06eV/e995AduwTKsS0ZgYn0VoocSXWst/nyhpKOcbJgAOohOYxgsGI1JEqQgjyeqzcCIhw/vlWiA3V8bSiPnrC9vwhH0eB025hBd2VbEGDz2nWCYkwtuOLMTvkmLi/oFw3GOfgagZKk8k/ZPffMCafz+yR3vb1nqAjncrVcJLI8amUfpxhjZYexo8MbxBA432M6w8sjXN+uLCl7ByWZ4xs4vonWgkmjeObtU37SIzolHT4dxIgaP2'
MANAGEMENT_CERT_THUMBRINT = 'BEA4B74BD6B915E9DD6A01FB1B8C3C1740F517F2'

#------------------------------------------------------------------------------


class LegacyMgmtManagementCertificateTest(LegacyMgmtTestCase):

    def setUp(self):
        super(LegacyMgmtManagementCertificateTest, self).setUp()

        self.sms = self.create_service_management(ServiceManagementService)

        self.certificate_thumbprints = []

    def tearDown(self):
        if not self.is_playback():
            for thumbprint in self.certificate_thumbprints:
                try:
                    self.sms.delete_management_certificate(thumbprint)
                except:
                    pass

        return super(LegacyMgmtManagementCertificateTest, self).tearDown()

    #--Helpers-----------------------------------------------------------------
    def _create_management_certificate(self, cert):
        self.certificate_thumbprints.append(cert.thumbprint)
        result = self.sms.add_management_certificate(cert.public_key,
                                                     cert.thumbprint,
                                                     cert.data)
        self.assertIsNone(result)

    def _management_certificate_exists(self, thumbprint):
        try:
            props = self.sms.get_management_certificate(thumbprint)
            return props is not None
        except:
            return False

    #--Test cases for management certificates ----------------------------
    @record
    def test_list_management_certificates(self):
        # Arrange
        local_cert = _local_certificate()
        self._create_management_certificate(local_cert)

        # Act
        result = self.sms.list_management_certificates()

        # Assert
        self.assertIsNotNone(result)
        self.assertTrue(len(result) > 0)

        cert = None
        for temp in result:
            if temp.subscription_certificate_thumbprint == \
                local_cert.thumbprint:
                cert = temp
                break

        self.assertIsNotNone(cert)
        self.assertIsNotNone(cert.created)
        self.assertEqual(cert.subscription_certificate_public_key,
                         local_cert.public_key)
        self.assertEqual(cert.subscription_certificate_data, local_cert.data)
        self.assertEqual(cert.subscription_certificate_thumbprint,
                         local_cert.thumbprint)

    @record
    def test_get_management_certificate(self):
        # Arrange
        local_cert = _local_certificate()
        self._create_management_certificate(local_cert)

        # Act
        result = self.sms.get_management_certificate(local_cert.thumbprint)

        # Assert
        self.assertIsNotNone(result)
        self.assertIsNotNone(result.created)
        self.assertEqual(result.subscription_certificate_public_key,
                         local_cert.public_key)
        self.assertEqual(result.subscription_certificate_data, local_cert.data)
        self.assertEqual(result.subscription_certificate_thumbprint,
                         local_cert.thumbprint)

    @record
    def test_add_management_certificate(self):
        # Arrange
        local_cert = _local_certificate()

        # Act
        self.certificate_thumbprints.append(local_cert.thumbprint)
        result = self.sms.add_management_certificate(local_cert.public_key,
                                                     local_cert.thumbprint,
                                                     local_cert.data)

        # Assert
        self.assertIsNone(result)
        self.assertTrue(
            self._management_certificate_exists(local_cert.thumbprint))

    @record
    def test_delete_management_certificate(self):
        # Arrange
        local_cert = _local_certificate()
        self._create_management_certificate(local_cert)

        # Act
        result = self.sms.delete_management_certificate(local_cert.thumbprint)

        # Assert
        self.assertIsNone(result)
        self.assertFalse(
            self._management_certificate_exists(local_cert.thumbprint))


class LocalCertificate(object):

    def __init__(self, thumbprint='', data='', public_key=''):
        self.thumbprint = thumbprint
        self.data = data
        self.public_key = public_key


def _local_certificate():
    # It would be nice to dynamically create this data, so that it is unique
    # But for now, we always create the same certificate
    return LocalCertificate(MANAGEMENT_CERT_THUMBRINT,
                            MANAGEMENT_CERT_DATA,
                            MANAGEMENT_CERT_PUBLICKEY)

#------------------------------------------------------------------------------
if __name__ == '__main__':
    unittest.main()
