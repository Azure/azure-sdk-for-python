# coding: utf-8

#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------

from typing import Any, Dict
import pytest
import asyncio
import functools
import os


from devtools_testutils import AzureTestCase, PowerShellPreparer
from azure_devtools.scenario_tests.utilities import trim_kwargs_from_test_function
from devtools_testutils.azure_testcase import _is_autorest_v3
from devtools_testutils import AzureTestCase
from azure.security.attestation.aio import (
    AttestationClient,
    AttestationAdministrationClient)
from azure.security.attestation import(
    AttestationType,
    TpmAttestationRequest,
    AttestationData,
    TokenValidationOptions)
import cryptography
import cryptography.x509
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization
from preparers import AttestationPreparer
import json

from test_policy_getset import Base64Url


_open_enclave_report = ("AQAAAAIAAADkEQAAAAAAAAMAAg" +
    "AAAAAABQAKAJOacjP3nEyplAoNs5V_Bgc42MPzGo7hPWS_h-3tExJrAAAAABERAwX_g" +
    "AYAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAUAAAAAAAAA" +
    "BwAAAAAAAAC3eSAmGL7LY2do5dkC8o1SQiJzX6-1OeqboHw_wXGhwgAAAAAAAAAAAAA" +
    "AAAAAAAAAAAAAAAAAAAAAAAAAAAAALBpElSroIHE1xsKbdbjAKTcu6UtnfhXCC9QjQP" +
    "ENQaoAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA" +
    "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAB" +
    "AAEAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA" +
    "AAAAAAAAAAAAAAAAA7RGp65ffwXBToyppkucdBPfsmW5FUZq3EJNq-0j5BB0AAAAAAA" +
    "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAADAQAAB4iv_XjOJsrFMrPvIYOBCeMR2q6" +
    "xB08KluTNAtIgpZQUIzLNyy78Gmb5LE77UIVye2sao77dOGiz3wP2f5jhEE5iovgPhy" +
    "6-Qg8JQkqe8XJI6B5ZlWsfq3E7u9EvH7ZZ33MihT7aM-sXca4u92L8OIhpM2cfJguOS" +
    "AS3Q4pR4NdRERAwX_gAYAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA" +
    "AAAAAAABUAAAAAAAAABwAAAAAAAAA_sKzghp0uMPKOhtcMdmQDpU-7zWWO7ODhuUipF" +
    "VkXQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAjE9XddeWUD6WE393xoqC" +
    "mgBWrI3tcBQLCBsJRJDFe_8AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA" +
    "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA" +
    "AAAAAAAAAAAAAAAAABAAUAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA" +
    "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAD9rOmAu-jSSf1BAj_cC0mu7YCnx4QosD" +
    "78yj3sQX81IAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAH5Au8JZ_dpXiLY" +
    "aE1TtyGjGz0dtFZa7eGooRGTQzoJJuR8Xj-zUvyCKE4ABy0pajfE8lOGSUHuJoifisJ" +
    "NAhg4gAAABAgMEBQYHCAkKCwwNDg8QERITFBUWFxgZGhscHR4fBQDIDQAALS0tLS1CR" +
    "UdJTiBDRVJUSUZJQ0FURS0tLS0tCk1JSUVmekNDQkNhZ0F3SUJBZ0lVRk5xSnZZZTU4" +
    "ZXlpUjI2Yzd0L2lxU0pNYnFNd0NnWUlLb1pJemowRUF3SXcKY1RFak1DRUdBMVVFQXd" +
    "3YVNXNTBaV3dnVTBkWUlGQkRTeUJRY205alpYTnpiM0lnUTBFeEdqQVlCZ05WQkFvTQ" +
    "pFVWx1ZEdWc0lFTnZjbkJ2Y21GMGFXOXVNUlF3RWdZRFZRUUhEQXRUWVc1MFlTQkRiR" +
    "0Z5WVRFTE1Ba0dBMVVFCkNBd0NRMEV4Q3pBSkJnTlZCQVlUQWxWVE1CNFhEVEl4TURR" +
    "eU1USXdOVGt6T0ZvWERUSTRNRFF5TVRJd05Ua3oKT0Zvd2NERWlNQ0FHQTFVRUF3d1p" +
    "TVzUwWld3Z1UwZFlJRkJEU3lCRFpYSjBhV1pwWTJGMFpURWFNQmdHQTFVRQpDZ3dSU1" +
    "c1MFpXd2dRMjl5Y0c5eVlYUnBiMjR4RkRBU0JnTlZCQWNNQzFOaGJuUmhJRU5zWVhKa" +
    "E1Rc3dDUVlEClZRUUlEQUpEUVRFTE1Ba0dBMVVFQmhNQ1ZWTXdXVEFUQmdjcWhrak9Q" +
    "UUlCQmdncWhrak9QUU1CQndOQ0FBUTgKU2V1NWV4WCtvMGNkclhkeEtHMGEvQXRzdnV" +
    "lNVNoUFpmOHgwa2czc0xSM2E5TzVHWWYwcW1XSkptL0c4bzZyVgpvbVI2Nmh3cFJXNl" +
    "pqSm9ocXdvT280SUNtekNDQXBjd0h3WURWUjBqQkJnd0ZvQVUwT2lxMm5YWCtTNUpGN" +
    "Wc4CmV4UmwwTlh5V1Uwd1h3WURWUjBmQkZnd1ZqQlVvRktnVUlaT2FIUjBjSE02THk5" +
    "aGNHa3VkSEoxYzNSbFpITmwKY25acFkyVnpMbWx1ZEdWc0xtTnZiUzl6WjNndlkyVnl" +
    "kR2xtYVdOaGRHbHZiaTkyTWk5d1kydGpjbXcvWTJFOQpjSEp2WTJWemMyOXlNQjBHQT" +
    "FVZERnUVdCQlFzbnhWelhVWnhwRkd5YUtXdzhWZmdOZXBjcHpBT0JnTlZIUThCCkFmO" +
    "EVCQU1DQnNBd0RBWURWUjBUQVFIL0JBSXdBRENDQWRRR0NTcUdTSWI0VFFFTkFRU0NB" +
    "Y1V3Z2dIQk1CNEcKQ2lxR1NJYjRUUUVOQVFFRUVEeEI4dUNBTVU0bmw1ZlBFaktxdG8" +
    "wd2dnRmtCZ29xaGtpRytFMEJEUUVDTUlJQgpWREFRQmdzcWhraUcrRTBCRFFFQ0FRSU" +
    "JFVEFRQmdzcWhraUcrRTBCRFFFQ0FnSUJFVEFRQmdzcWhraUcrRTBCCkRRRUNBd0lCQ" +
    "WpBUUJnc3Foa2lHK0UwQkRRRUNCQUlCQkRBUUJnc3Foa2lHK0UwQkRRRUNCUUlCQVRB" +
    "UkJnc3EKaGtpRytFMEJEUUVDQmdJQ0FJQXdFQVlMS29aSWh2aE5BUTBCQWdjQ0FRWXd" +
    "FQVlMS29aSWh2aE5BUTBCQWdnQwpBUUF3RUFZTEtvWklodmhOQVEwQkFna0NBUUF3RU" +
    "FZTEtvWklodmhOQVEwQkFnb0NBUUF3RUFZTEtvWklodmhOCkFRMEJBZ3NDQVFBd0VBW" +
    "UxLb1pJaHZoTkFRMEJBZ3dDQVFBd0VBWUxLb1pJaHZoTkFRMEJBZzBDQVFBd0VBWUwK" +
    "S29aSWh2aE5BUTBCQWc0Q0FRQXdFQVlMS29aSWh2aE5BUTBCQWc4Q0FRQXdFQVlMS29" +
    "aSWh2aE5BUTBCQWhBQwpBUUF3RUFZTEtvWklodmhOQVEwQkFoRUNBUW93SHdZTEtvWk" +
    "lodmhOQVEwQkFoSUVFQkVSQWdRQmdBWUFBQUFBCkFBQUFBQUF3RUFZS0tvWklodmhOQ" +
    "VEwQkF3UUNBQUF3RkFZS0tvWklodmhOQVEwQkJBUUdBSkJ1MVFBQU1BOEcKQ2lxR1NJ" +
    "YjRUUUVOQVFVS0FRQXdDZ1lJS29aSXpqMEVBd0lEUndBd1JBSWdjREZEZHl1UFRHRVR" +
    "ORm5BU0QzOApDWTNSNmlBREpEVHZBbHZTWDNIekk4a0NJRDZsVm1DWklYUHk4ekpKMW" +
    "gvMnJ1NjJsdlVVWDJJaU1ibVFOUEEwClBzMC8KLS0tLS1FTkQgQ0VSVElGSUNBVEUtL" +
    "S0tLQotLS0tLUJFR0lOIENFUlRJRklDQVRFLS0tLS0KTUlJQ2x6Q0NBajZnQXdJQkFn" +
    "SVZBTkRvcXRwMTEva3VTUmVZUEhzVVpkRFY4bGxOTUFvR0NDcUdTTTQ5QkFNQwpNR2d" +
    "4R2pBWUJnTlZCQU1NRVVsdWRHVnNJRk5IV0NCU2IyOTBJRU5CTVJvd0dBWURWUVFLRE" +
    "JGSmJuUmxiQ0JECmIzSndiM0poZEdsdmJqRVVNQklHQTFVRUJ3d0xVMkZ1ZEdFZ1Eye" +
    "GhjbUV4Q3pBSkJnTlZCQWdNQWtOQk1Rc3cKQ1FZRFZRUUdFd0pWVXpBZUZ3MHhPREEx" +
    "TWpFeE1EUTFNRGhhRncwek16QTFNakV4TURRMU1EaGFNSEV4SXpBaApCZ05WQkFNTUd" +
    "rbHVkR1ZzSUZOSFdDQlFRMHNnVUhKdlkyVnpjMjl5SUVOQk1Sb3dHQVlEVlFRS0RCRk" +
    "piblJsCmJDQkRiM0p3YjNKaGRHbHZiakVVTUJJR0ExVUVCd3dMVTJGdWRHRWdRMnhoY" +
    "21FeEN6QUpCZ05WQkFnTUFrTkIKTVFzd0NRWURWUVFHRXdKVlV6QlpNQk1HQnlxR1NN" +
    "NDlBZ0VHQ0NxR1NNNDlBd0VIQTBJQUJMOXErTk1wMklPZwp0ZGwxYmsvdVdaNStUR1F" +
    "tOGFDaTh6NzhmcytmS0NRM2QrdUR6WG5WVEFUMlpoRENpZnlJdUp3dk4zd05CcDlpCk" +
    "hCU1NNSk1KckJPamdic3dnYmd3SHdZRFZSMGpCQmd3Rm9BVUltVU0xbHFkTkluemc3U" +
    "1ZVcjlRR3prbkJxd3cKVWdZRFZSMGZCRXN3U1RCSG9FV2dRNFpCYUhSMGNITTZMeTlq" +
    "WlhKMGFXWnBZMkYwWlhNdWRISjFjM1JsWkhObApjblpwWTJWekxtbHVkR1ZzTG1OdmJ" +
    "TOUpiblJsYkZOSFdGSnZiM1JEUVM1amNtd3dIUVlEVlIwT0JCWUVGTkRvCnF0cDExL2" +
    "t1U1JlWVBIc1VaZERWOGxsTk1BNEdBMVVkRHdFQi93UUVBd0lCQmpBU0JnTlZIUk1CQ" +
    "WY4RUNEQUcKQVFIL0FnRUFNQW9HQ0NxR1NNNDlCQU1DQTBjQU1FUUNJQy85ais4NFQr" +
    "SHp0Vk8vc09RQldKYlNkKy8ydWV4Swo0K2FBMGpjRkJMY3BBaUEzZGhNckY1Y0Q1MnQ" +
    "2RnFNdkFJcGo4WGRHbXkyYmVlbGpMSksrcHpwY1JBPT0KLS0tLS1FTkQgQ0VSVElGSU" +
    "NBVEUtLS0tLQotLS0tLUJFR0lOIENFUlRJRklDQVRFLS0tLS0KTUlJQ2pqQ0NBalNnQ" +
    "XdJQkFnSVVJbVVNMWxxZE5JbnpnN1NWVXI5UUd6a25CcXd3Q2dZSUtvWkl6ajBFQXdJ" +
    "dwphREVhTUJnR0ExVUVBd3dSU1c1MFpXd2dVMGRZSUZKdmIzUWdRMEV4R2pBWUJnTlZ" +
    "CQW9NRVVsdWRHVnNJRU52CmNuQnZjbUYwYVc5dU1SUXdFZ1lEVlFRSERBdFRZVzUwWV" +
    "NCRGJHRnlZVEVMTUFrR0ExVUVDQXdDUTBFeEN6QUoKQmdOVkJBWVRBbFZUTUI0WERUR" +
    "TRNRFV5TVRFd05ERXhNVm9YRFRNek1EVXlNVEV3TkRFeE1Gb3dhREVhTUJnRwpBMVVF" +
    "QXd3UlNXNTBaV3dnVTBkWUlGSnZiM1FnUTBFeEdqQVlCZ05WQkFvTUVVbHVkR1ZzSUV" +
    "OdmNuQnZjbUYwCmFXOXVNUlF3RWdZRFZRUUhEQXRUWVc1MFlTQkRiR0Z5WVRFTE1Ba0" +
    "dBMVVFQ0F3Q1EwRXhDekFKQmdOVkJBWVQKQWxWVE1Ga3dFd1lIS29aSXpqMENBUVlJS" +
    "29aSXpqMERBUWNEUWdBRUM2bkV3TURJWVpPai9pUFdzQ3phRUtpNwoxT2lPU0xSRmhX" +
    "R2pibkJWSmZWbmtZNHUzSWprRFlZTDBNeE80bXFzeVlqbEJhbFRWWXhGUDJzSkJLNXp" +
    "sS09CCnV6Q0J1REFmQmdOVkhTTUVHREFXZ0JRaVpReldXcDAwaWZPRHRKVlN2MUFiT1" +
    "NjR3JEQlNCZ05WSFI4RVN6QkoKTUVlZ1JhQkRoa0ZvZEhSd2N6b3ZMMk5sY25ScFptb" +
    "GpZWFJsY3k1MGNuVnpkR1ZrYzJWeWRtbGpaWE11YVc1MApaV3d1WTI5dEwwbHVkR1Zz" +
    "VTBkWVVtOXZkRU5CTG1OeWJEQWRCZ05WSFE0RUZnUVVJbVVNMWxxZE5JbnpnN1NWClV" +
    "yOVFHemtuQnF3d0RnWURWUjBQQVFIL0JBUURBZ0VHTUJJR0ExVWRFd0VCL3dRSU1BWU" +
    "JBZjhDQVFFd0NnWUkKS29aSXpqMEVBd0lEU0FBd1JRSWdRUXMvMDhyeWNkUGF1Q0ZrO" +
    "FVQUVhDTUFsc2xvQmU3TndhUUdUY2RwYTBFQwpJUUNVdDhTR3Z4S21qcGNNL3owV1A5" +
    "RHZvOGgyazVkdTFpV0RkQmtBbiswaWlBPT0KLS0tLS1FTkQgQ0VSVElGSUNBVEUtLS0" +
    "tLQoA")


_runtime_data = ("CiAgICAgICAgewogI" +
    "CAgICAgICAgICAiandrIiA6IHsKICAgICAgICAgICAgICAgICJrdHkiOiJFQyIsCiAg" +
    "ICAgICAgICAgICAgICAidXNlIjoic2lnIiwKICAgICAgICAgICAgICAgICJjcnYiOiJ" +
    "QLTI1NiIsCiAgICAgICAgICAgICAgICAieCI6IjE4d0hMZUlnVzl3Vk42VkQxVHhncH" +
    "F5MkxzellrTWY2SjhualZBaWJ2aE0iLAogICAgICAgICAgICAgICAgInkiOiJjVjRkU" +
    "zRVYUxNZ1BfNGZZNGo4aXI3Y2wxVFhsRmRBZ2N4NTVvN1RrY1NBIgogICAgICAgICAg" +
    "ICB9CiAgICAgICAgfQogICAgICAgIA")

class AsyncAzureAttestationTest(AzureTestCase):
    def __init__(self, *args, **kwargs):
        super(AsyncAzureAttestationTest, self).__init__(*args, **kwargs)

    @AttestationPreparer()
    @AzureTestCase.await_prepared_test
    async def test_shared_getopenidmetadataasync(self, attestation_location_short_name):
        attest_client = self.shared_client(attestation_location_short_name)
        open_id_metadata = (await attest_client.get_openidmetadata())
        print ('{}'.format(open_id_metadata))
        assert open_id_metadata["response_types_supported"] is not None
        if self.is_live:
            assert open_id_metadata["jwks_uri"] == self.shared_base_uri(attestation_location_short_name)+"/certs"
            assert open_id_metadata["issuer"] == self.shared_base_uri(attestation_location_short_name)

    @AttestationPreparer()
    @pytest.mark.live_test_only
    async def test_aad_getopenidmetadataasync(self, attestation_aad_url):
        attest_client = self.create_client(attestation_aad_url)
        open_id_metadata = await attest_client.get_openidmetadata()
        assert open_id_metadata["response_types_supported"] is not None
        assert open_id_metadata["jwks_uri"] == attestation_aad_url+"/certs"
        assert open_id_metadata["issuer"] == attestation_aad_url

    @AttestationPreparer()
    @pytest.mark.live_test_only
    async def test_isolated_getopenidmetadataasync(self, attestation_isolated_url):
        attest_client = self.create_client(attestation_isolated_url)
        open_id_metadata = await attest_client.get_openidmetadata()
        assert open_id_metadata["response_types_supported"] is not None
        assert open_id_metadata["jwks_uri"] == attestation_isolated_url+"/certs"
        assert open_id_metadata["issuer"] == attestation_isolated_url

    @AttestationPreparer()
    async def test_shared_getsigningcertificatesasync(self, attestation_location_short_name):
        attest_client = self.shared_client(attestation_location_short_name)
        signers = await attest_client.get_signing_certificates()
        for signer in signers:
            cryptography.x509.load_der_x509_certificate(signer.certificates[0], backend=default_backend())

    @AttestationPreparer()
    async def test_aad_getsigningcertificatesasync(self, attestation_aad_url):
        #type: (str) -> None
        attest_client = self.create_client(attestation_aad_url)
        signers = await attest_client.get_signing_certificates()
        for signer in signers:
            cryptography.x509.load_der_x509_certificate(signer.certificates[0], backend=default_backend())

    @AttestationPreparer()
    async def test_isolated_getsigningcertificatesasync(self, attestation_isolated_url):
        #type: (str) -> None
        attest_client = self.create_client(attestation_isolated_url)
        signers = await attest_client.get_signing_certificates()
        for signer in signers:
            cryptography.x509.load_der_x509_certificate(signer.certificates[0], backend=default_backend())



    async def _test_attest_open_enclave(self, client_uri):
        #type: (str) -> None
        attest_client = self.create_client(client_uri)
        oe_report = Base64Url.decode(_open_enclave_report)
        runtime_data = Base64Url.decode(_runtime_data)
        response = await attest_client.attest_open_enclave(
                oe_report,
                runtime_data=AttestationData(runtime_data, is_json=False))
        assert response.value.enclave_held_data == runtime_data
        assert response.value.sgx_collateral is not None

        #Now do the validation again, this time specifying runtime data as JSON.
        response = await attest_client.attest_open_enclave(oe_report, runtime_data=AttestationData(runtime_data, is_json=True))
        # Because the runtime data is JSON, enclave_held_data will be empty.
        assert response.value.enclave_held_data == None
        assert response.value.runtime_claims.get('jwk') is not None
        assert response.value.runtime_claims['jwk']['crv']=='P-256'
        assert response.value.sgx_collateral is not None

        assert response.token.get_body().iss == response.value.issuer


    @AttestationPreparer()
    async def test_shared_attest_open_enclave(self, attestation_location_short_name):
        #type: (str) -> None
        await self._test_attest_open_enclave(self.shared_base_uri(attestation_location_short_name))

    @AttestationPreparer()
    async def test_aad_attest_open_enclave(self, attestation_aad_url):
        #type: (str) -> None
        await self._test_attest_open_enclave(attestation_aad_url)

    @AttestationPreparer()
    async def test_isolated_attest_open_enclave(self, attestation_isolated_url):
        #type: (str) -> None
        await self._test_attest_open_enclave(attestation_isolated_url)

    async def _test_attest_sgx_enclave(self, base_uri):
        #type: (str) -> None
        attest_client = self.create_client(base_uri)
        oe_report = Base64Url.decode(_open_enclave_report)
        # Convert the OE report into an SGX quote by stripping off the first 16 bytes.
        quote = oe_report[16:]
        runtime_data = Base64Url.decode(_runtime_data)
        response = await attest_client.attest_sgx_enclave(
            quote, runtime_data=AttestationData(runtime_data, is_json=False))
        assert response.value.enclave_held_data == runtime_data
        assert response.value.sgx_collateral is not None

        #Now do the validation again, this time specifying runtime data as JSON.
        response = await attest_client.attest_sgx_enclave(quote, runtime_data=AttestationData(runtime_data, is_json=True))
        # Because the runtime data is JSON, enclave_held_data will be empty.
        assert response.value.enclave_held_data == None
        assert response.value.runtime_claims.get('jwk') is not None
        assert response.value.runtime_claims['jwk']['crv']=='P-256'
        assert response.value.sgx_collateral is not None

        #And try #3, this time letting the AttestationData type figure it out.
        response = await attest_client.attest_sgx_enclave(quote, runtime_data=AttestationData(runtime_data))
        # Because the runtime data is JSON, enclave_held_data will be empty.
        assert response.value.enclave_held_data == None
        assert response.value.runtime_claims.get('jwk') is not None
        assert response.value.runtime_claims['jwk']['crv']=='P-256'
        assert response.value.sgx_collateral is not None


    @AttestationPreparer()
    async def test_aad_attest_sgx_enclave(self, attestation_aad_url):
        #type: (str) -> None
        await self._test_attest_sgx_enclave(attestation_aad_url)

    @AttestationPreparer()
    async def test_isolated_attest_sgx_enclave(self, attestation_isolated_url):
        #type: (str) -> None
        await self._test_attest_sgx_enclave(attestation_isolated_url)


    @AttestationPreparer()
    async def test_shared_attest_sgx_enclave(self, attestation_location_short_name):
        #type: (str) -> None
        await self._test_attest_sgx_enclave(self.shared_base_uri(attestation_location_short_name))


    @AttestationPreparer()
    async def test_tpm_attestation(
        self,
        attestation_aad_url):
        #type: (str) -> None
        client = self.create_client(attestation_aad_url)
        admin_client = self.create_adminclient(attestation_aad_url)

        # TPM attestation requires that there be a policy present, so set one.
        basic_policy = "version=1.0; authorizationrules{=> permit();}; issuancerules{};"
        await admin_client.set_policy(AttestationType.TPM, basic_policy)

        encoded_payload = json.dumps({ "payload": { "type": "aikcert" } }).encode("ascii")
        tpm_response = await client.attest_tpm(TpmAttestationRequest(encoded_payload))

        decoded_response = json.loads(tpm_response.data)
        assert decoded_response["payload"] is not None
        payload = decoded_response["payload"]
        assert payload["challenge"] is not None
        assert payload["service_context"] is not None

    """
        # Commented out call showing the modifications needed to convert this to a call
        # to an MAA instance running locally for diagnostic purposes.
        @AttestationPreparer()
        def test_local_attest_open_enclave(self):
            attest_client = self.create_client('http://localhost:8080')

            oe_report = Base64Url.decode(_open_enclave_report)
    #        # Convert the OE report into an SGX quote by stripping off the first 16 bytes.
    #        quote = oe_report[16:-1]
            runtime_data = Base64Url.decode(_runtime_data)
            response = attest_client.attest_open_enclave(
            oe_report,
            None, False,
            runtime_data, False, 
            enforce_https=False,
            headers={"tenantName": "tenant1"})
            print(response)
    """



    def create_client(self, base_uri, **kwargs):
        #type: (str, Dict[str, Any]) -> AttestationClient
        """
        docstring
        """
        credential = self.get_credential(AttestationClient, is_async=True)
        attest_client = self.create_client_from_credential(AttestationClient,
            credential=credential,
            instance_url=base_uri,
            token_validation_options = TokenValidationOptions(
                validate_token=True,
                validate_signature=True,
                validate_issuer=self.is_live,
                issuer=base_uri,
                validate_expiration=self.is_live),
            **kwargs)
        return attest_client

    def create_adminclient(self, base_uri, **kwargs): 
        #type: (str, Any) -> AttestationAdministrationClient
        """
        docstring
        """
        credential = self.get_credential(AttestationAdministrationClient, is_async=True)
        attest_client = self.create_client_from_credential(AttestationAdministrationClient,
            credential=credential,
            instance_url=base_uri,
            token_validation_options = TokenValidationOptions(
                validate_token=True,
                validate_signature=True,
                validate_issuer=self.is_live,
                issuer=base_uri,
                validate_expiration=self.is_live),
            **kwargs)
        return attest_client
        
    def shared_client(self, location_name):
        """
        docstring
        """
        return self.create_client(self.shared_base_uri(location_name))

    def shared_base_uri(self, location_name: str):
        return 'https://shared' + location_name +'.'+ location_name + '.attest.azure.net'
