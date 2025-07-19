# pylint: disable=line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import json

import pytest

from azure.keyvault.securitydomain import SecurityDomainClient

from _shared.test_case import KeyVaultTestCase
from _test_case import ClientPreparer
from utils import get_certificate_info, write_security_domain, write_transfer_key
from wrapping import use_wrapping_keys


class TestSecurityDomain(KeyVaultTestCase):
    @pytest.mark.live_test_only
    @ClientPreparer()
    def test_security_domain_download_and_upload(
        self, client: SecurityDomainClient, upload_client: SecurityDomainClient, **kwargs
    ):
        """Test downloading a security domain and uploading it to another Managed HSM.

        This test requires two Managed HSMs to be set up, one for downloading and one for uploading. The URL of the
        first Managed HSM is specified in the environment variable AZURE_MANAGEDHSM_URL, and the second is specified
        in SECONDARY_MANAGEDHSM_URL.
        """
        # Load the certificate{x}.cer files from /resources and use them to download the security domain.
        certs_object = get_certificate_info()
        poller = client.begin_download(certificate_info=certs_object, skip_activation_polling=True)
        result = poller.result()
        status = client.get_download_status()
        assert status.status
        assert status.status.lower() == "inprogress"
        assert result.value

        # Get the transfer key of the secondary HSM, and write it and the security domain to files.
        jwk = str(upload_client.get_transfer_key().transfer_key)
        transfer_key = json.loads(jwk)
        write_transfer_key(transfer_key)
        write_security_domain(result.value)
        # Wrap the security domain using the certificate{x}.pem keys.
        wrapped_security_domain = use_wrapping_keys()

        # Upload the wrapped security domain to the secondary HSM.
        poller = upload_client.begin_upload(security_domain=wrapped_security_domain)
        result = poller.result()
        assert result is None
        status = upload_client.get_upload_status()
        assert status.status
        assert status.status.lower() == "success"
