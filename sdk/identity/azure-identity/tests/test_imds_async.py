# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import pytest

from azure.identity.aio._internal import ImdsCredential


@pytest.mark.asyncio
async def test_imds_credential_async():
    credential = ImdsCredential()
    token = await credential.get_token("https://management.azure.com/.default")
    assert token
