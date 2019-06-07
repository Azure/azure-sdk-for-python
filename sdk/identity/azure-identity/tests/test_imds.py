# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See LICENSE.txt in the project root for
# license information.
# -------------------------------------------------------------------------
from azure.identity._internal import ImdsCredential


def test_imds_credential():
    credential = ImdsCredential()
    token = credential.get_token("https://management.azure.com/.default")
    assert token
