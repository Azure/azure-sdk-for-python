# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
from azure.keyvault.certificates import CertificatePolicy
from pytest import raises

def test_policy_expected_errors():
    with raises(ValueError) as ex:
        cert_policy = CertificatePolicy("issuer-name")
    assert "subject" in str(ex.value), "Error should be thrown since we haven't set a subject or sans"