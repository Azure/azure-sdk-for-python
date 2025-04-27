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


class TestSecurityDomain(KeyVaultTestCase):
    @pytest.mark.live_test_only
    @ClientPreparer()
    def test_security_domain_download_and_upload(
        self, client: SecurityDomainClient, upload_client: SecurityDomainClient, **kwargs
    ):
        # Before running this test, create security domain certificates
        # 1. Create private keys: `openssl genrsa -pubout -out <>-certificate[0-2].key 2048`
        # 2. Create certificates: `openssl req -new -x509 -days 365 -key <>-certificate[0-2].key -out <>-certificate[0-2].cer`
        certs_object = get_certificate_info()
        poller = client.begin_download(certificate_info=certs_object, skip_activation_polling=True)
        result = poller.result()
        status = client.get_download_status()
        assert status.status
        assert status.status.lower() == "inprogress"
        assert result.value

        jwk = str(upload_client.get_transfer_key().transfer_key)
        transfer_key = json.loads(jwk)
        write_transfer_key(transfer_key)
        write_security_domain(result.value)

        # At this point, use the Azure CLI to encrypt the security domain to prepare for upload
        # `az keyvault security-domain restore-blob --sd-exchange-key <>-transfer-key.pem --sd-file <>-security-domain.json --sd-wrapping-keys <>-certificate0.key <>-certificate1.key <>-certificate2.key --sd-file-restore-blob <>-restore-blob.json`
        poller = upload_client.begin_upload(security_domain=result)
        result = poller.result()
        assert result is None
        status = upload_client.get_upload_status()
        assert status.status
        assert status.status.lower() == "success"
