# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
from azure.core.credentials import AzureKeyCredential
from azure.ai.personalizer.aio import PersonalizerClient, PersonalizerAdministrationClient
import asyncio


def create_async_personalizer_client(personalizer_endpoint, personalizer_api_key):
    credential = AzureKeyCredential(personalizer_api_key)
    client = PersonalizerClient(personalizer_endpoint, credential=credential)
    return client


def create_async_personalizer_admin_client(personalizer_endpoint, personalizer_api_key):
    credential = AzureKeyCredential(personalizer_api_key)
    client = PersonalizerAdministrationClient(personalizer_endpoint, credential=credential)
    return client


async def enable_multi_slot(personalizer_endpoint, personalizer_api_key, is_live):
    client = create_async_personalizer_admin_client(personalizer_endpoint, personalizer_api_key)
    policy = await client.get_policy()
    if policy["arguments"].__contains__("--ccb_explore_adf"):
        return

    configuration = await client.get_service_configuration()
    if configuration.get("isAutoOptimizationEnabled"):
        configuration["isAutoOptimizationEnabled"] = False
        await client.update_service_configuration(configuration)
        if is_live:
            await asyncio.sleep(30)

    multi_slot_policy = {
        "name": "enable multi slot",
        "arguments": policy["arguments"].replace("--cb_explore_adf", "--ccb_explore_adf")
    }

    await client.update_policy(multi_slot_policy)
    if is_live:
        await asyncio.sleep(30)
