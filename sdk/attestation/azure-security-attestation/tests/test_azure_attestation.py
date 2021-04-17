# coding: utf-8

#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------


# TEST SCENARIO COVERAGE
# ----------------------
# Methods Total   : 7
# Methods Covered : 7
# Examples Total  : 7
# Examples Tested : 7
# Coverage %      : 100
# ----------------------

from logging import fatal
from typing import ByteString
import unittest
from cryptography.hazmat.primitives import hashes
from devtools_testutils import AzureTestCase, PowerShellPreparer
import functools
import cryptography
import cryptography.x509
from cryptography.hazmat.primitives import serialization
import base64
import pytest
import azure.identity
from azure.security.attestation import AttestationClient, AttestationAdministrationClient, AttestationType, TokenValidationOptions, StoredAttestationPolicy, AttestationToken, SigningKey


AttestationPreparer = functools.partial(
            PowerShellPreparer, "attestation",
#            attestation_azure_authority_host='xxx',
#            attestation_resource_group='yyyy',
#            attestation_subscription_id='xxx',
#            attestation_environment='AzureCloud',
            attestation_policy_signing_key0='keyvalue',
            attestation_policy_signing_key1='keyvalue',
            attestation_policy_signing_key2='keyvalue',
            attestation_policy_signing_certificate0='more junk',
            attestation_policy_signing_certificate1='more junk',
            attestation_policy_signing_certificate2='more junk',
            attestation_serialized_policy_signing_key0="junk",
            attestation_serialized_policy_signing_key1="junk",
            attestation_serialized_policy_signing_key2="junk",
            attestation_serialized_isolated_signing_key='yyyy',
            attestation_isolated_signing_key='xxxx',
            attestation_isolated_signing_certificate='xxxx',
            attestation_service_management_url='https://management.core.windows.net/',
            attestation_location_short_name='wus', # Note: This must match the short name in the fake resources.
            attestation_client_id='xxxx',
            attestation_client_secret='secret',
            attestation_tenant_id='tenant',
            attestation_isolated_url='https://fakeresource.wus.attest.azure.net',
            attestation_aad_url='https://fakeresource.wus.attest.azure.net',
#            attestation_resource_manager_url='https://resourcemanager/zzz'
        )

_open_enclave_report = ("AQAAAAIAAADoEQAAAAAAAAMAAgAAAAAABQAKAJOacjP3nEyplAoNs5V_"
"Bgfl_L18zrEJejtqk6RDB0IzAAAAABERAwX_gAYAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA"
"AAAAAAAAAAAAAAAcAAAAAAAAABwAAAAAAAAApKh9LUZ5GYn6yR4o9mFFAVlPFtLCmkl3oQ4NNkhaFDg"
"AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAASupfmg7QSxH4iarf5qHTdiE6Kalahc5zN65vf"
"-zmYQwAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA"
"AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAABAAEAAAAAAAAAAAAAAAAAAAA"
"AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAKFQuRP5-c_ZhD2sxrn"
"V2kl8JzNu0xWRlg-zBVhM3qP8AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAADQQAACJx8e27"
"oQ0pijs3lXQ9HfKWP9NMqVHQFL9SOjC_KGDcbv-I2fCafTHJ__AmNqVXy7XTXnzmLp1HhUCy1_9AORS"
"ATqGZ1PtvBf4Q2NfNxqVkNrGJAjYuqMPStdg0MuM21nN-Qc9BWNycRMMsU7YfHSzmw7eGjBb_Ewfb3k"
"6N4ZYRhERAwX_gAYAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAABUAAAAAAA"
"AABwAAAAAAAAA_sKzghp0uMPKOhtcMdmQDpU-7zWWO7ODhuUipFVkXQAAAAAAAAAAAAAAAAAAAAAAAA"
"AAAAAAAAAAAAAAAAAAAjE9XddeWUD6WE393xoqCmgBWrI3tcBQLCBsJRJDFe_8AAAAAAAAAAAAAAAAA"
"AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA"
"AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAABAAUAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA"
"AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAH_mzVQFF8XbJCRGdNkA3SPx9ZUPgtx3874VyDYQnF"
"RIAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAEUP2-pxe7LoyevtN5BdE4KKikxKK6-hwG0x"
"CDmxmfLphcnrVskSbKmiKUfzkWUBehrF8gHCGNGIPX3QQDwmtZ4gAAABAgMEBQYHCAkKCwwNDg8QERI"
"TFBUWFxgZGhscHR4fBQDMDQAALS0tLS1CRUdJTiBDRVJUSUZJQ0FURS0tLS0tCk1JSUVnVENDQkNhZ0"
"F3SUJBZ0lVU3I5VmRiSnFWbzVyZzRadUpCRWo2SjNoak9jd0NnWUlLb1pJemowRUF3SXcKY1RFak1DR"
"UdBMVVFQXd3YVNXNTBaV3dnVTBkWUlGQkRTeUJRY205alpYTnpiM0lnUTBFeEdqQVlCZ05WQkFvTQpF"
"VWx1ZEdWc0lFTnZjbkJ2Y21GMGFXOXVNUlF3RWdZRFZRUUhEQXRUWVc1MFlTQkRiR0Z5WVRFTE1Ba0d"
"BMVVFCkNBd0NRMEV4Q3pBSkJnTlZCQVlUQWxWVE1CNFhEVEl4TURNeE9UQTBOVEl3T0ZvWERUSTRNRE"
"14T1RBME5USXcKT0Zvd2NERWlNQ0FHQTFVRUF3d1pTVzUwWld3Z1UwZFlJRkJEU3lCRFpYSjBhV1pwW"
"TJGMFpURWFNQmdHQTFVRQpDZ3dSU1c1MFpXd2dRMjl5Y0c5eVlYUnBiMjR4RkRBU0JnTlZCQWNNQzFO"
"aGJuUmhJRU5zWVhKaE1Rc3dDUVlEClZRUUlEQUpEUVRFTE1Ba0dBMVVFQmhNQ1ZWTXdXVEFUQmdjcWh"
"rak9QUUlCQmdncWhrak9QUU1CQndOQ0FBUlQKVGRNNVhTMGFiRTA2ZUdVTVU3S1JOQXJlRGRtTWJHK2"
"5KVHlucDZXankyeXJ6NmlEa3h1R1F3WGZ1b25uUVBuZApjdHgwbHIyR3I0WjF1YXNsQjM2Vm80SUNte"
"kNDQXBjd0h3WURWUjBqQkJnd0ZvQVUwT2lxMm5YWCtTNUpGNWc4CmV4UmwwTlh5V1Uwd1h3WURWUjBm"
"QkZnd1ZqQlVvRktnVUlaT2FIUjBjSE02THk5aGNHa3VkSEoxYzNSbFpITmwKY25acFkyVnpMbWx1ZEd"
"Wc0xtTnZiUzl6WjNndlkyVnlkR2xtYVdOaGRHbHZiaTkyTWk5d1kydGpjbXcvWTJFOQpjSEp2WTJWem"
"MyOXlNQjBHQTFVZERnUVdCQlRMejZNQ3VHcVZobFYrR2Q0ZGtacmx4YndCV2pBT0JnTlZIUThCCkFmO"
"EVCQU1DQnNBd0RBWURWUjBUQVFIL0JBSXdBRENDQWRRR0NTcUdTSWI0VFFFTkFRU0NBY1V3Z2dIQk1C"
"NEcKQ2lxR1NJYjRUUUVOQVFFRUVMOEhhRExXWWdVUFUzU3c3Tm1Ibkhrd2dnRmtCZ29xaGtpRytFMEJ"
"EUUVDTUlJQgpWREFRQmdzcWhraUcrRTBCRFFFQ0FRSUJFVEFRQmdzcWhraUcrRTBCRFFFQ0FnSUJFVE"
"FRQmdzcWhraUcrRTBCCkRRRUNBd0lCQWpBUUJnc3Foa2lHK0UwQkRRRUNCQUlCQkRBUUJnc3Foa2lHK"
"0UwQkRRRUNCUUlCQVRBUkJnc3EKaGtpRytFMEJEUUVDQmdJQ0FJQXdFQVlMS29aSWh2aE5BUTBCQWdj"
"Q0FRWXdFQVlMS29aSWh2aE5BUTBCQWdnQwpBUUF3RUFZTEtvWklodmhOQVEwQkFna0NBUUF3RUFZTEt"
"vWklodmhOQVEwQkFnb0NBUUF3RUFZTEtvWklodmhOCkFRMEJBZ3NDQVFBd0VBWUxLb1pJaHZoTkFRME"
"JBZ3dDQVFBd0VBWUxLb1pJaHZoTkFRMEJBZzBDQVFBd0VBWUwKS29aSWh2aE5BUTBCQWc0Q0FRQXdFQ"
"VlMS29aSWh2aE5BUTBCQWc4Q0FRQXdFQVlMS29aSWh2aE5BUTBCQWhBQwpBUUF3RUFZTEtvWklodmhO"
"QVEwQkFoRUNBUW93SHdZTEtvWklodmhOQVEwQkFoSUVFQkVSQWdRQmdBWUFBQUFBCkFBQUFBQUF3RUF"
"ZS0tvWklodmhOQVEwQkF3UUNBQUF3RkFZS0tvWklodmhOQVEwQkJBUUdBSkJ1MVFBQU1BOEcKQ2lxR1"
"NJYjRUUUVOQVFVS0FRQXdDZ1lJS29aSXpqMEVBd0lEU1FBd1JnSWhBSzZPMS9GNy80NFprcWhUN2FhN"
"gp5QVh6QlltRWxUVHRvL25rVUd4N1BtUktBaUVBMXliSWt6SjVwcXR1L21jOW5DUWNwRUJOdk5KZFNI"
"cW1jc04rCkV2dWJ3WlU9Ci0tLS0tRU5EIENFUlRJRklDQVRFLS0tLS0KLS0tLS1CRUdJTiBDRVJUSUZ"
"JQ0FURS0tLS0tCk1JSUNsekNDQWo2Z0F3SUJBZ0lWQU5Eb3F0cDExL2t1U1JlWVBIc1VaZERWOGxsTk"
"1Bb0dDQ3FHU000OUJBTUMKTUdneEdqQVlCZ05WQkFNTUVVbHVkR1ZzSUZOSFdDQlNiMjkwSUVOQk1Sb"
"3dHQVlEVlFRS0RCRkpiblJsYkNCRApiM0p3YjNKaGRHbHZiakVVTUJJR0ExVUVCd3dMVTJGdWRHRWdR"
"MnhoY21FeEN6QUpCZ05WQkFnTUFrTkJNUXN3CkNRWURWUVFHRXdKVlV6QWVGdzB4T0RBMU1qRXhNRFE"
"xTURoYUZ3MHpNekExTWpFeE1EUTFNRGhhTUhFeEl6QWgKQmdOVkJBTU1Ha2x1ZEdWc0lGTkhXQ0JRUT"
"BzZ1VISnZZMlZ6YzI5eUlFTkJNUm93R0FZRFZRUUtEQkZKYm5SbApiQ0JEYjNKd2IzSmhkR2x2YmpFV"
"U1CSUdBMVVFQnd3TFUyRnVkR0VnUTJ4aGNtRXhDekFKQmdOVkJBZ01Ba05CCk1Rc3dDUVlEVlFRR0V3"
"SlZVekJaTUJNR0J5cUdTTTQ5QWdFR0NDcUdTTTQ5QXdFSEEwSUFCTDlxK05NcDJJT2cKdGRsMWJrL3V"
"XWjUrVEdRbThhQ2k4ejc4ZnMrZktDUTNkK3VEelhuVlRBVDJaaERDaWZ5SXVKd3ZOM3dOQnA5aQpIQl"
"NTTUpNSnJCT2pnYnN3Z2Jnd0h3WURWUjBqQkJnd0ZvQVVJbVVNMWxxZE5JbnpnN1NWVXI5UUd6a25Cc"
"Xd3ClVnWURWUjBmQkVzd1NUQkhvRVdnUTRaQmFIUjBjSE02THk5alpYSjBhV1pwWTJGMFpYTXVkSEox"
"YzNSbFpITmwKY25acFkyVnpMbWx1ZEdWc0xtTnZiUzlKYm5SbGJGTkhXRkp2YjNSRFFTNWpjbXd3SFF"
"ZRFZSME9CQllFRk5EbwpxdHAxMS9rdVNSZVlQSHNVWmREVjhsbE5NQTRHQTFVZER3RUIvd1FFQXdJQk"
"JqQVNCZ05WSFJNQkFmOEVDREFHCkFRSC9BZ0VBTUFvR0NDcUdTTTQ5QkFNQ0EwY0FNRVFDSUMvOWorO"
"DRUK0h6dFZPL3NPUUJXSmJTZCsvMnVleEsKNCthQTBqY0ZCTGNwQWlBM2RoTXJGNWNENTJ0NkZxTXZB"
"SXBqOFhkR215MmJlZWxqTEpLK3B6cGNSQT09Ci0tLS0tRU5EIENFUlRJRklDQVRFLS0tLS0KLS0tLS1"
"CRUdJTiBDRVJUSUZJQ0FURS0tLS0tCk1JSUNqakNDQWpTZ0F3SUJBZ0lVSW1VTTFscWROSW56ZzdTVl"
"VyOVFHemtuQnF3d0NnWUlLb1pJemowRUF3SXcKYURFYU1CZ0dBMVVFQXd3UlNXNTBaV3dnVTBkWUlGS"
"nZiM1FnUTBFeEdqQVlCZ05WQkFvTUVVbHVkR1ZzSUVOdgpjbkJ2Y21GMGFXOXVNUlF3RWdZRFZRUUhE"
"QXRUWVc1MFlTQkRiR0Z5WVRFTE1Ba0dBMVVFQ0F3Q1EwRXhDekFKCkJnTlZCQVlUQWxWVE1CNFhEVEU"
"0TURVeU1URXdOREV4TVZvWERUTXpNRFV5TVRFd05ERXhNRm93YURFYU1CZ0cKQTFVRUF3d1JTVzUwWl"
"d3Z1UwZFlJRkp2YjNRZ1EwRXhHakFZQmdOVkJBb01FVWx1ZEdWc0lFTnZjbkJ2Y21GMAphVzl1TVJRd"
"0VnWURWUVFIREF0VFlXNTBZU0JEYkdGeVlURUxNQWtHQTFVRUNBd0NRMEV4Q3pBSkJnTlZCQVlUCkFs"
"VlRNRmt3RXdZSEtvWkl6ajBDQVFZSUtvWkl6ajBEQVFjRFFnQUVDNm5Fd01ESVlaT2ovaVBXc0N6YUV"
"LaTcKMU9pT1NMUkZoV0dqYm5CVkpmVm5rWTR1M0lqa0RZWUwwTXhPNG1xc3lZamxCYWxUVll4RlAyc0"
"pCSzV6bEtPQgp1ekNCdURBZkJnTlZIU01FR0RBV2dCUWlaUXpXV3AwMGlmT0R0SlZTdjFBYk9TY0dyR"
"EJTQmdOVkhSOEVTekJKCk1FZWdSYUJEaGtGb2RIUndjem92TDJObGNuUnBabWxqWVhSbGN5NTBjblZ6"
"ZEdWa2MyVnlkbWxqWlhNdWFXNTAKWld3dVkyOXRMMGx1ZEdWc1UwZFlVbTl2ZEVOQkxtTnliREFkQmd"
"OVkhRNEVGZ1FVSW1VTTFscWROSW56ZzdTVgpVcjlRR3prbkJxd3dEZ1lEVlIwUEFRSC9CQVFEQWdFR0"
"1CSUdBMVVkRXdFQi93UUlNQVlCQWY4Q0FRRXdDZ1lJCktvWkl6ajBFQXdJRFNBQXdSUUlnUVFzLzA4c"
"nljZFBhdUNGazhVUFFYQ01BbHNsb0JlN053YVFHVGNkcGEwRUMKSVFDVXQ4U0d2eEttanBjTS96MFdQ"
"OUR2bzhoMms1ZHUxaVdEZEJrQW4rMGlpQT09Ci0tLS0tRU5EIENFUlRJRklDQVRFLS0tLS0KAA")


_runtime_data = ("CiAgICAgICAgewogICAgICAgICAgICAiandrIiA6IHsKICAgICAgICAgICAgICA"
"gICJrdHkiOiJFQyIsCiAgICAgICAgICAgICAgICAidXNlIjoic2lnIiwKICAgICAgICAgICAgICAgIC"
"JjcnYiOiJQLTI1NiIsCiAgICAgICAgICAgICAgICAieCI6IjE4d0hMZUlnVzl3Vk42VkQxVHhncHF5M"
"kxzellrTWY2SjhualZBaWJ2aE0iLAogICAgICAgICAgICAgICAgInkiOiJjVjRkUzRVYUxNZ1BfNGZZ"
"NGo4aXI3Y2wxVFhsRmRBZ2N4NTVvN1RrY1NBIgogICAgICAgICAgICB9CiAgICAgICAgfQogICAgICA"
"gIAA")

class AzureAttestationTest(AzureTestCase):

    def setUp(self):
        super(AzureAttestationTest, self).setUp()


    # The caching infrastructure won't cache .well-known/openid_metadata responses so
    # mark the metadata related tests as live-only.
    @AttestationPreparer()
    @pytest.mark.live_test_only
    def test_shared_getopenidmetadata(self, attestation_location_short_name):
        attest_client = self.shared_client(attestation_location_short_name)
        open_id_metadata = attest_client.get_openidmetadata()
        print ('{}'.format(open_id_metadata))
        assert open_id_metadata["response_types_supported"] is not None
        if self.is_live:
            assert open_id_metadata["jwks_uri"] == self.shared_base_uri(attestation_location_short_name)+"/certs"
            assert open_id_metadata["issuer"] == self.shared_base_uri(attestation_location_short_name)

    @AttestationPreparer()
    @pytest.mark.live_test_only
    def test_aad_getopenidmetadata(self, attestation_aad_url):
        attest_client = self.create_client(attestation_aad_url)
        open_id_metadata = attest_client.get_openidmetadata()
        print ('{}'.format(open_id_metadata))
        assert open_id_metadata["response_types_supported"] is not None
        if self.is_live:
            assert open_id_metadata["jwks_uri"] == attestation_aad_url+"/certs"
            assert open_id_metadata["issuer"] == attestation_aad_url

    @AttestationPreparer()
    @pytest.mark.live_test_only
    def test_isolated_getopenidmetadata(self, attestation_isolated_url):
        attest_client = self.create_client(attestation_isolated_url)
        open_id_metadata = attest_client.get_openidmetadata()
        print ('{}'.format(open_id_metadata))
        assert open_id_metadata["response_types_supported"] is not None
        if self.is_live:
            assert open_id_metadata["jwks_uri"] == attestation_isolated_url+"/certs"
            assert open_id_metadata["issuer"] == attestation_isolated_url

    @AttestationPreparer()
    def test_shared_getsigningcertificates(self, attestation_location_short_name):
        attest_client = self.shared_client(attestation_location_short_name)
        signing_certificates = attest_client.get_signing_certificates()
        for cert in signing_certificates:
            x5c = cert.certificates[0] # type: cryptography.x509.Certificate
            print('Cert  iss:', x5c.issuer, '; subject:', x5c.subject)

    @AttestationPreparer()
    def test_aad_getsigningcertificates(self, attestation_aad_url):
        attest_client = self.create_client(attestation_aad_url)
        signing_certificates = attest_client.get_signing_certificates()
        for cert in signing_certificates:
            x5c = cert.certificates[0] # type: cryptography.x509.Certificate
            print('Cert  iss:', x5c.issuer, '; subject:', x5c.subject)

    @AttestationPreparer()
    def test_isolated_getsigningcertificates(self, attestation_isolated_url):
        attest_client = self.create_client(attestation_isolated_url)
        signing_certificates = attest_client.get_signing_certificates()
        for cert in signing_certificates:
            x5c = cert.certificates[0] # type: cryptography.x509.Certificate
            print('Cert  iss:', x5c.issuer, '; subject:', x5c.subject)

    @AttestationPreparer()
    def test_aad_attest_open_enclave(self, attestation_aad_url):
        attest_client = self.create_client(attestation_aad_url)
        oe_report = Base64Url.decode(_open_enclave_report)
        runtime_data = Base64Url.decode(_runtime_data)
        response = attest_client.attest_open_enclave(oe_report, None, False, runtime_data, False)
        runtime_data = Base64Url.decode(_runtime_data)
        response = attest_client.attest_open_enclave(oe_report, None, False, runtime_data, False)
        assert response.value.enclave_held_data == runtime_data
        assert response.value.sgx_collateral is not None

        #Now do the validation again, this time specifying runtime data as JSON.
        response = attest_client.attest_open_enclave(oe_report, None, False, runtime_data, True)
        # Because the runtime data is JSON, enclave_held_data will be empty.
        assert response.value.enclave_held_data == None
        assert response.value.runtime_claims.get('jwk') is not None
        assert response.value.runtime_claims['jwk']['crv']=='P-256'
        assert response.value.sgx_collateral is not None


    @AttestationPreparer()
    def test_shared_attest_open_enclave(self, attestation_location_short_name):
        attest_client = self.shared_client(attestation_location_short_name)
        oe_report = Base64Url.decode(_open_enclave_report)
        runtime_data = Base64Url.decode(_runtime_data)
        response = attest_client.attest_open_enclave(oe_report, None, False, runtime_data, False)
        assert response.value.enclave_held_data == runtime_data
        assert response.value.sgx_collateral is not None

        #Now do the validation again, this time specifying runtime data as JSON.
        response = attest_client.attest_open_enclave(oe_report, None, False, runtime_data, True)
        # Because the runtime data is JSON, enclave_held_data will be empty.
        assert response.value.enclave_held_data == None
        assert response.value.runtime_claims.get('jwk') is not None
        assert response.value.runtime_claims['jwk']['crv']=='P-256'
        assert response.value.sgx_collateral is not None

    @AttestationPreparer()
    def test_aad_attest_sgx_enclave(self, attestation_aad_url):
        attest_client = self.create_client(attestation_aad_url)
        oe_report = Base64Url.decode(_open_enclave_report)
        # Convert the OE report into an SGX quote by stripping off the first 16 bytes.
        quote = oe_report[16:]
        runtime_data = Base64Url.decode(_runtime_data)
        response = attest_client.attest_sgx_enclave(quote, None, False, runtime_data, False)
        runtime_data = Base64Url.decode(_runtime_data)
        response = attest_client.attest_sgx_enclave(quote, None, False, runtime_data, False)
        assert response.value.enclave_held_data == runtime_data
        assert response.value.sgx_collateral is not None

        #Now do the validation again, this time specifying runtime data as JSON.
        response = attest_client.attest_sgx_enclave(quote, None, False, runtime_data, True)
        # Because the runtime data is JSON, enclave_held_data will be empty.
        assert response.value.enclave_held_data == None
        assert response.value.runtime_claims.get('jwk') is not None
        assert response.value.runtime_claims['jwk']['crv']=='P-256'
        assert response.value.sgx_collateral is not None


    @AttestationPreparer()
    def test_shared_attest_sgx_enclave(self, attestation_location_short_name):
        attest_client = self.shared_client(attestation_location_short_name)
        oe_report = Base64Url.decode(_open_enclave_report)
        # Convert the OE report into an SGX quote by stripping off the first 16 bytes.
        quote = oe_report[16:]
        runtime_data = Base64Url.decode(_runtime_data)
        response = attest_client.attest_sgx_enclave(quote, None, False, runtime_data, False)
        assert response.value.enclave_held_data == runtime_data
        assert response.value.sgx_collateral is not None

        #Now do the validation again, this time specifying runtime data as JSON.
        response = attest_client.attest_sgx_enclave(quote, None, False, runtime_data, True)
        # Because the runtime data is JSON, enclave_held_data will be empty.
        assert response.value.enclave_held_data == None
        assert response.value.runtime_claims.get('jwk') is not None
        assert response.value.runtime_claims['jwk']['crv']=='P-256'
        assert response.value.sgx_collateral is not None


#    @AttestationPreparer()
#    def test_local_attest_open_enclave(self):
#        attest_client = self.create_client('http://localhost:8080')
#
#        oe_report = Base64Url.decode(_open_enclave_report)
##        # Convert the OE report into an SGX quote by stripping off the first 16 bytes.
##        quote = oe_report[16:-1]
#        runtime_data = Base64Url.decode(_runtime_data)
#        response = attest_client.attest_open_enclave(
#        oe_report,
#        None, False,
#        runtime_data, False, 
#        enforce_https=False,
#        headers={"tenantName": "tenant1"})
#        print(response)


    @AttestationPreparer()
    def test_shared_get_policy_sgx(self, attestation_location_short_name):
        attest_client = self.shared_admin_client(attestation_location_short_name)
        policy_response = attest_client.get_policy(AttestationType.SGX_ENCLAVE)
        print('Shared policy: ', policy_response.value)
        assert(policy_response.value.startswith('version'))
        print('Token: ', policy_response.token)

    @AttestationPreparer()
    def test_shared_get_policy_openenclave(self, attestation_location_short_name):
        attest_client = self.shared_admin_client(attestation_location_short_name)
        policy_response = attest_client.get_policy(AttestationType.OPEN_ENCLAVE)
        print('Shared policy: ', policy_response.value)
        assert(policy_response.value.startswith('version'))
        print('Token: ', policy_response.token)


    @AttestationPreparer()
    def test_isolated_get_policy_sgx(self, attestation_isolated_url):
        attest_client = self.create_admin_client(attestation_isolated_url)
        policy_response = attest_client.get_policy(AttestationType.SGX_ENCLAVE)
        print('Shared policy: ', policy_response.value)
        assert(policy_response.value.startswith('version'))
        print('Token: ', policy_response.token)

    @AttestationPreparer()
    def test_aad_get_policy_sgx(self, attestation_aad_url):
        attest_client = self.create_admin_client(attestation_aad_url)
        policy_response = attest_client.get_policy(AttestationType.SGX_ENCLAVE)
        print('Shared policy: ', policy_response.value)
        assert(policy_response.value.startswith('version'))
        print('Token: ', policy_response.token)

    @AttestationPreparer()
    def test_aad_set_policy_sgx_unsecured(self, attestation_aad_url):
        attestation_policy = u"version=1.0; authorizationrules{=> permit();}; issuancerules{};"

        attest_client = self.create_admin_client(attestation_aad_url)
        policy_set_response = attest_client.set_policy(AttestationType.SGX_ENCLAVE, attestation_policy)
        policy_get_response = attest_client.get_policy(AttestationType.SGX_ENCLAVE)
        assert policy_get_response.value == attestation_policy

        expected_policy = AttestationToken(body=StoredAttestationPolicy(attestation_policy=str(attestation_policy).encode('utf-8')))
        hasher = hashes.Hash(hashes.SHA256())
        hasher.update(expected_policy.serialize().encode('utf-8'))
        expected_hash = hasher.finalize()

        assert expected_hash == policy_set_response.value.policy_token_hash


    @AttestationPreparer()
    @pytest.mark.live_test_only
    def test_aad_set_policy_sgx_secured(self, attestation_aad_url, attestation_policy_signing_key0, attestation_policy_signing_certificate0):
        attestation_policy = u"version=1.0; authorizationrules{=> permit();}; issuancerules{};"

        decoded_cert = base64.b64decode(attestation_policy_signing_certificate0)

        signing_certificate = cryptography.x509.load_der_x509_certificate(decoded_cert)
        key = serialization.load_der_private_key(base64.b64decode(attestation_policy_signing_key0), password=None)

        attest_client = self.create_admin_client(attestation_aad_url)
        policy_set_response = attest_client.set_policy(AttestationType.SGX_ENCLAVE,
            attestation_policy,
            signing_key=SigningKey(key, signing_certificate))
        policy_get_response = attest_client.get_policy(AttestationType.SGX_ENCLAVE)
        assert policy_get_response.value == attestation_policy

        expected_policy = AttestationToken(body=StoredAttestationPolicy(attestation_policy=str(attestation_policy).encode('utf-8')))
        hasher = hashes.Hash(hashes.SHA256())
        hasher.update(expected_policy.serialize().encode('utf-8'))
        expected_hash = hasher.finalize()

        assert expected_hash == policy_set_response.value.policy_token_hash



#     @AttestationPreparer()
#     def test_aad_get_policy_management_signers(self, attestation_aad_url):
#         attest_client = self.create_client(attestation_aad_url)
#         policy_signers = attest_client.policy_certificates.get()
#         default_signers = policy_signers.token
#         policy_token = jwt.decode(
#             default_signers, 
#             options={"verify_signature":False, 'verify_exp': False},
#             leeway=10, 
#             algorithms=["none", "RS256"])
#         print("{}".format(policy_token))
#         policy_certificates = policy_token["x-ms-policy-certificates"]
#         assert len(policy_certificates["keys"])==0

#     def test_shared_get_policy_management_signers(self):
#         attest_client = self.shared_client()
#         policy_signers = attest_client.policy_certificates.get()
#         default_signers = policy_signers.token
#         policy_token = jwt.decode(
#             default_signers, 
#             options={"verify_signature":False, 'verify_exp': False},
#             leeway=10,
#             algorithms=["none", "RS256"])
#         print("{}".format(policy_token))
#         policy_certificates = policy_token["x-ms-policy-certificates"]
#         assert len(policy_certificates["keys"])==0

#     @AttestationPreparer()
#     def test_isolated_get_policy_management_signers(self, attestation_isolated_url):
#         attest_client = self.create_client(attestation_isolated_url)
#         policy_signers = attest_client.policy_certificates.get()
#         default_signers = policy_signers.token
#         policy_token = jwt.decode(
#             default_signers, 
#             options={"verify_signature":False, 'verify_exp': False},
#             leeway=10,
#             algorithms=["none", "RS256"])
#         print("{}".format(policy_token))
#         policy_certificates = policy_token["x-ms-policy-certificates"]
#         assert len(policy_certificates["keys"])==1
#         policy_key = policy_certificates["keys"][0]
#         x5cs = policy_key["x5c"]
#         assert len(x5cs) != 0
#         for cert in x5cs:
#             der_cert = base64.b64decode(cert)
#             cert = cryptography.x509.load_der_x509_certificate(der_cert)
#             print('Policy Management Certificate iss:', cert.issuer, '}; subject: ', cert.subject)
            
    def create_client(self, base_uri): #type() -> AttestationClient
            """
            docstring
            """
            credential = self.get_credential(AttestationClient)
            attest_client = self.create_client_from_credential(AttestationClient,
                credential=credential,
                instance_url=base_uri,
                token_validation_options = TokenValidationOptions(
                    validate_token=True,
                    validate_signature=True,
                    validate_issuer=self.is_live,
                    issuer=base_uri,
                    validate_expiration=self.is_live))
            return attest_client

    def create_admin_client(self, base_uri): #type() -> AttestationAdministrationClient:
            """
            docstring
            """
            credential = self.get_credential(AttestationAdministrationClient)
            attest_client = self.create_client_from_credential(AttestationAdministrationClient,
                credential=credential,
                instance_url=base_uri,
                token_validation_options = TokenValidationOptions(
                    validate_token=True,
                    validate_signature=True,
                    validate_issuer=self.is_live,
                    issuer=base_uri,
                    validate_expiration=self.is_live))
            return attest_client

    def shared_client(self, location_name): #type(str) -> AttestationClient:
            """
            docstring
            """
            return self.create_client(self.shared_base_uri(location_name))

    def shared_admin_client(self, location_name): #type(str) -> AttestationAdministrationClient:
            """
            docstring
            """
            return self.create_admin_client(self.shared_base_uri(location_name))


    @staticmethod
    def shared_base_uri(location_name): #type(str) -> str
        # When run with recorded tests, the location_name may be 'None', deal with it.
#        return 'https://shareduks.uks.test.attest.azure.net'
        if location_name is not None:
            return 'https://shared'+location_name+'.'+location_name+'.attest.azure.net'
        return 'https://sharedcus.cus.attest.azure.net'
   
class Base64Url:
    """Equivalent to base64.urlsafe_b64encode, but strips padding from the encoded and decoded strings.
    """
    @staticmethod
    def encode(unencoded):
        # type(bytes)->str
        base64val = base64.urlsafe_b64encode(unencoded)
        strip_trailing=base64val.split(b'=')[0] # pick the string before the trailing =
        return strip_trailing.decode('utf-8')

    @staticmethod
    def decode(encoded):
        # type(str)->bytes
        padding_added = encoded + "=" * ((len(encoded)* -1) % 4)
        return base64.urlsafe_b64decode(padding_added.encode('utf-8'))


#------------------------------------------------------------------------------
if __name__ == '__main__':
    unittest.main()
