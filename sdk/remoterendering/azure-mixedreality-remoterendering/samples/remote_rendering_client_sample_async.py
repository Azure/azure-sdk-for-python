# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

import asyncio
import os
import time
import uuid

from azure.core.credentials import AzureKeyCredential
from azure.core.async_paging import AsyncItemPaged
from azure.mixedreality.remoterendering import (AssetConversionInputSettings,
                                                AssetConversionOutputSettings,
                                                AssetConversionStatus,
                                                RenderingSession, RenderingSessionSize,
                                                RenderingSessionStatus)
from azure.mixedreality.remoterendering.aio import RemoteRenderingClient

arr_endpoint = os.environ.get("ARR_ENDPOINT", None)
if not arr_endpoint:
    raise ValueError(
        "Set ARR_SERVICE_ENDPOINT env before run this sample.")

account_id = os.environ.get("ARR_ACCOUNT_ID", None)
if not account_id:
    raise ValueError("Set ARR_ACCOUNT_ID env before run this sample.")

account_domain = os.environ.get("ARR_ACCOUNT_DOMAIN", None)
if not account_domain:
    raise ValueError("Set ARR_ACCOUNT_DOMAIN env before run this sample.")

account_key = os.environ.get("ARR_ACCOUNT_KEY", None)
if not account_key:
    raise ValueError("Set ARR_ACCOUNT_KEY env before run this sample.")

key_credential = AzureKeyCredential(account_key)

client = RemoteRenderingClient(remote_rendering_endpoint=arr_endpoint,
                               account_id=account_id, account_domain=account_domain, credential=key_credential)


async def perform_asset_conversion():
    conversion_id = str(uuid.uuid4())

    input_settings = AssetConversionInputSettings(
        storage_container_uri="https://arrrunnerteststorage.blob.core.windows.net/arrinput",
        relative_input_asset_path="box.fbx",
        blob_prefix="input")
    output_settings = AssetConversionOutputSettings(
        storage_container_uri="https://arrrunnerteststorage.blob.core.windows.net/arroutput",
        blob_prefix=conversion_id)

    conversion_poller = await client.begin_asset_conversion(conversion_id=conversion_id,
                                                            input_settings=input_settings,
                                                            output_settings=output_settings)
    print("conversion with id:", conversion_id,
          "created. Waiting for completion.")
    conversion = await conversion_poller.result()

    # a poller can also be acquired by a continuation token
    token_poller = await client.get_asset_conversion_poller(continuation_token=conversion_poller.continuation_token())
    conversion = await token_poller.result()

    # a poller can also be acquired by id
    id_poller = await client.get_asset_conversion_poller(conversion_id=conversion_id)
    conversion = await id_poller.result()

    print("conversion with id:", conversion_id,
          "finished with result:", conversion.status)

    # we can also get the status of an individual asset conversion like this:
    conversion = await client.get_asset_conversion(conversion_id)
    print("individual conversion retrieved with id:", conversion.id)
    print("\tconversion status:", conversion.status)


async def list_all_asset_conversions():
    print("listing conversions for remote rendering account: ", account_id)
    print("conversions:")
    conversions = await client.list_asset_conversions()
    async for c in conversions:
        print("\t conversion:  id:", c.id, "status:", c.status,
              "created on", c.created_on.strftime("%m/%d/%Y, %H:%M:%S"))
        if(c.status == AssetConversionStatus.SUCCEEDED):
            print("\t\tconversion result URI:", c.output.asset_uri)


async def demonstrate_rendering_session_lifecycle():
    session_id = str(uuid.uuid4())
    print("starting rendering session with id:", session_id)
    session_poller = await client.begin_rendering_session(
        session_id=session_id, size=RenderingSessionSize.STANDARD, max_lease_time_minutes=5)
    print("rendering session with id:", session_id,
          "created. Waiting for session to be ready.")
    session = await session_poller.result()
    print("session with id:", session.id, "is ready. max_lease_time_minutes:",
          session.max_lease_time_minutes)

    # a poller can also be acquired by a continuation token
    token = session_poller.continuation_token()
    token_poller = await client.get_rendering_session_poller(continuation_token=token)
    session = await token_poller.result()

    # a poller can also be acquired by id
    id_poller = await client.get_rendering_session_poller(session_id=session_id)
    session = await id_poller.result()

    # one can now connect to the rendering session using the runtime SDK on a Hololens 2
    print(session)

    # we can also get the properties of an individual session by id:
    session = await client.get_rendering_session(session_id)
    print(session)

    # if the session should run longer than initially requested we can extend the lifetime of the session
    session = await client.extend_rendering_session(
        session_id=session_id, max_lease_time_minutes=10)
    print("session with id:", session.id, "updated. New lease time:",
          session.max_lease_time_minutes, "minutes")

    # once we do not need the session anymore we can stop the session
    await client.stop_rendering_session(session_id)
    print("session with id:", session_id, "stopped")


async def list_all_rendering_sessions():
    print("listing sessions for account:", account_id)
    print("sessions:")
    rendering_sessions = await client.list_rendering_sessions()
    async for session in rendering_sessions:
        print("\t session:  id:", session.id, "status:", session.status,
              "created on:", session.created_on.strftime("%m/%d/%Y, %H:%M:%S"))


async def main():
    async with client:
        await perform_asset_conversion()
        await list_all_asset_conversions()
        await demonstrate_rendering_session_lifecycle()
        await list_all_rendering_sessions()

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
