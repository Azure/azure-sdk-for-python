# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import pytest
from azure.communication.callingserver.aio import CallingServerClient
from azure.communication.callingserver import CallingServerClient as CallingServerClientSync
from io import BytesIO

@pytest.mark.asyncio
@pytest.mark.skip
async def test_download_content():
    metadata_url = "https://storage.asm.skype.com/v1/objects/0-wus-d4-6afafe78b9e313d77933b87578eabc9e/content/acsmetadata"
    connection_string = "endpoint=https://acstelephonyportaltesting.communication.azure.com/;accesskey=/cJGRzQtFVNneQVqbUlRvsvOLwEgQwsWDQxjLnWPWcTSg3RwAfnYY4v9Ce/mN4iAZ50znB8B0UMmQ/cDHLnEtw=="

    calling_server_client = CallingServerClient.from_connection_string(connection_string)
    downloader = await calling_server_client.download(metadata_url)
    stream = BytesIO()
    await downloader.readinto(stream)
    print(stream)

@pytest.mark.skip
def test_download():
    metadata_url = "https://storage.asm.skype.com/v1/objects/0-wus-d4-6afafe78b9e313d77933b87578eabc9e/content/acsmetadata"
    connection_string = "endpoint=https://acstelephonyportaltesting.communication.azure.com/;accesskey=/cJGRzQtFVNneQVqbUlRvsvOLwEgQwsWDQxjLnWPWcTSg3RwAfnYY4v9Ce/mN4iAZ50znB8B0UMmQ/cDHLnEtw=="

    calling_server_client = CallingServerClientSync.from_connection_string(connection_string)
    print(calling_server_client.start_download(content_url=metadata_url))
