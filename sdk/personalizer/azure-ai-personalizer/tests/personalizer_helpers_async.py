from azure.core.credentials import AzureKeyCredential
from azure.ai.personalizer.aio import PersonalizerClient
import asyncio


def create_async_personalizer_client(personalizer_endpoint, personalizer_api_key):
    credential = AzureKeyCredential(personalizer_api_key)
    client = PersonalizerClient(personalizer_endpoint, credential=credential)
    return client


async def enable_multi_slot(client, is_live):
    policy = await client.policy.get()
    if policy["arguments"].__contains__("--ccb_explore_adf"):
        return

    configuration = await client.service_configuration.get()
    if configuration.get("isAutoOptimizationEnabled"):
        configuration["isAutoOptimizationEnabled"] = False
        await client.service_configuration.put(configuration)
        if is_live:
            asyncio.sleep(30)

    multi_slot_policy = {
        "name": "enable multi slot",
        "arguments": policy["arguments"].replace("--cb_explore_adf", "--ccb_explore_adf")
    }

    await client.policy.update(multi_slot_policy)
    if is_live:
        asyncio.sleep(30)
