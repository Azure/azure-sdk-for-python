# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: remote_rendering_client_sample_async.py
DESCRIPTION:
    These samples demonstrate creating a remote rendering client, converting an asset into the format used in rendering
    sessions, listing created asset conversions, starting a rendering session, extending the lifetime of a rendering 
    session, stopping a rendering session and listing rendering sessions.

USAGE:
    python remote_rendering_client_sample_async.py
    Set the environment variables with your own values before running the sample:
    ARR_SERVICE_ENDPOINT - the endpoint of the Azure Remote Rendering service in the desired region.
        e.g. "https://remoterendering.eastus.mixedreality.azure.com" for the East US region
        Supported regions can be found at https://docs.microsoft.com/en-us/azure/remote-rendering/reference/regions
    ARR_ACCOUNT_DOMAIN - the Remote Rendering account domain. e.g. "eastus.mixedreality.azure.com"
    ARR_ACCOUNT_ID - the Remote Rendering account identifier.
    ARR_ACCOUNT_KEY - the Remote Rendering account primary or secondary key.
"""

import asyncio
import logging
import os
import sys
import time
import uuid

from azure.core.async_paging import AsyncItemPaged
from azure.core.credentials import AzureKeyCredential
from azure.mixedreality.remoterendering import (AssetConversionInputSettings,
                                                AssetConversionOutputSettings,
                                                AssetConversionStatus,
                                                RenderingSession,
                                                RenderingSessionSize,
                                                RenderingSessionStatus)
from azure.mixedreality.remoterendering.aio import RemoteRenderingClient

# Create a logger for the 'azure' SDK
logger = logging.getLogger("azure")
logger.setLevel(logging.DEBUG)

# Configure a console output
handler = logging.StreamHandler(stream=sys.stdout)
logger.addHandler(handler)

# Enable network trace logging. This will be logged at DEBUG level.
# By default, logging is disabled.
logging_policy_enabled = os.environ.get("ARR_LOGGING_ENABLED", None)

logging_policy = None
if logging_policy_enabled:
    logging_policy = NetworkTraceLoggingPolicy()
    logging_policy.enable_http_logger = True

arr_endpoint = os.environ.get("ARR_SERVICE_ENDPOINT", None)
if not arr_endpoint:
    raise ValueError("Set ARR_SERVICE_ENDPOINT env before run this sample.")

account_id = os.environ.get("ARR_ACCOUNT_ID", None)
if not account_id:
    raise ValueError("Set ARR_ACCOUNT_ID env before run this sample.")

account_domain = os.environ.get("ARR_ACCOUNT_DOMAIN", None)
if not account_domain:
    raise ValueError("Set ARR_ACCOUNT_DOMAIN env before run this sample.")

account_key = os.environ.get("ARR_ACCOUNT_KEY", None)
if not account_key:
    raise ValueError("Set ARR_ACCOUNT_KEY env before run this sample.")

storage_container_uri = os.environ.get("ARR_STORAGE_CONTAINER_URI", None)
if not storage_container_uri:
    raise ValueError("Set ARR_STORAGE_CONTAINER_URI env before run this sample.")

input_blob_prefix = os.environ.get("ARR_STORAGE_INPUT_BLOB_PREFIX", None)
# if no input_blob_prefix is specified the whole content of the storage container will be retrieved for conversions
# this is not recommended since copying lots of unneeded files will slow down conversions

relative_input_asset_path = os.environ.get("ARR_STORAGE_INPUT_ASSET_PATH", None)
if not relative_input_asset_path:
    raise ValueError("Set ARR_STORAGE_INPUT_ASSET_PATH env before run this sample.")

# use AzureKeyCredentials to authenticate to the service - other auth options include AAD and getting
# STS token using the mixed reality STS client
key_credential = AzureKeyCredential(account_key)

client = RemoteRenderingClient(
    endpoint=arr_endpoint,
    account_id=account_id,
    account_domain=account_domain,
    credential=key_credential,
    logging_policy=logging_policy
)


async def perform_asset_conversion():
    try:
        # a UUID is a good conversion ID - guaranteed to be unique on an account
        conversion_id = str(uuid.uuid4())

        # In order to convert a model the input model needs to be retrieved from blob storage and the result of the
        # conversion process will be written back to blob storage
        # The subset of files which will be retrieved from the given input storage container is controlled by the
        # input_settings blob_prefix more details at:
        # https://docs.microsoft.com/en-us/azure/remote-rendering/resources/troubleshoot#conversion-file-download-errors
        input_settings = AssetConversionInputSettings(
            storage_container_uri=storage_container_uri,
            blob_prefix=input_blob_prefix,  # if not specified all files from the input container will be retrieved
            relative_input_asset_path=relative_input_asset_path,
            # container_read_list_sas #if storage is not linked with the ARR account provide a SAS here to grant access.
        )

        output_settings = AssetConversionOutputSettings(
            storage_container_uri=storage_container_uri,  # Note: different input/output containers can be specified
            blob_prefix="output/"+conversion_id,
            # output_asset_filename= convertedAsset.arrAsset # if not specified the output will be "<inputfile>.arrAsset".
            # container_write_sas  #if storage is not linked with the ARR account provide a SAS here to grant access.
        )

        conversion_poller = await client.begin_asset_conversion(conversion_id=conversion_id,
                                                                input_settings=input_settings,
                                                                output_settings=output_settings)

        print("conversion with id:", conversion_id, "created. Waiting for completion.")
        conversion = await conversion_poller.result()
        print("conversion with id:", conversion_id, "finished with result:", conversion.status)
        print(conversion.output.asset_uri)

        # a poller can also be acquired by id
        # id_poller = await client.get_asset_conversion_poller(conversion_id=conversion_id)
        # conversion = await id_poller.result()

        # we can also get the status of an individual asset conversion like this:
        conversion = await client.get_asset_conversion(conversion_id)
        print("individual conversion retrieved with id:", conversion.id)
        print("\tconversion status:", conversion.status)

    except Exception as e:
        print("An error occurred: ", e)


async def list_all_asset_conversions():
    print("listing conversions for remote rendering account: ", account_id)
    print("conversions:")
    conversions = await client.list_asset_conversions()
    async for c in conversions:
        created_on = c.created_on.strftime("%m/%d/%Y, %H:%M:%S")
        print("\t conversion:  id:", c.id, "status:", c.status, "created on:", created_on)
        if c.status == AssetConversionStatus.SUCCEEDED:
            print("\t\tconversion result URI:", c.output.asset_uri)


async def demonstrate_rendering_session_lifecycle():
    try:
        # a UUID is a good session ID - guaranteed to be unique on an account
        session_id = str(uuid.uuid4())
        print("starting rendering session with id:", session_id)
        session_poller = await client.begin_rendering_session(
            session_id=session_id, size=RenderingSessionSize.STANDARD, lease_time_minutes=5)
        print("rendering session with id:", session_id, "created. Waiting for session to be ready.")

        session = await session_poller.result()
        print("session with id:", session.id, "is ready. lease_time_minutes:", session.lease_time_minutes)

        # a poller can also be acquired by id
        # id_poller = await client.get_rendering_session_poller(session_id=session_id)
        # session = await id_poller.result()

        # one can now connect to the rendering session using the runtime SDK on a Hololens 2
        print(session)

        # we can also get the properties of an individual session by id:
        session = await client.get_rendering_session(session_id)
        print(session)

        # if the session should run longer than initially requested we can extend the lifetime of the session
        session = client.get_rendering_session(session_id)
        if session.lease_time_minutes - session.elapsed_time_minutes < 2:
            session = await client.update_rendering_session(
                session_id=session_id, lease_time_minutes=session.lease_time_minutes + 10)
            print("session with id:", session.id, "updated. New lease time:", session.lease_time_minutes, "minutes")

        # once we do not need the session anymore we can stop the session
        await client.stop_rendering_session(session_id)
        print("session with id:", session_id, "stopped")
    except Exception as e:
        print("An error occurred: ", e)


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
