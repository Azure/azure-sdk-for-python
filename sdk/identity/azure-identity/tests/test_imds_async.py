# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See LICENSE.txt in the project root for
# license information.
# -------------------------------------------------------------------------
import pytest

from azure.identity.aio._internal import AsyncImdsCredential


@pytest.mark.asyncio
async def test_imds_credential_async():
    credential = AsyncImdsCredential()
    token = await credential.get_token("https://management.azure.com/.default")
    assert token
