# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
from azure.identity._internal import ImdsCredential


def test_imds_credential():
    credential = ImdsCredential()
    token = credential.get_token("https://management.azure.com/.default")
    assert token
