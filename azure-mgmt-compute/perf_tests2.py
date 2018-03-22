import asyncio
import time

from azure.mgmt.compute.v2017_12_01 import ComputeManagementClient
from azure.common.credentials import get_azure_cli_credentials


async def test_vm_images_async(client):
    result = []
    result_list = []
    location = "westus"

    result_list_pub = await client.virtual_machine_images.list_publishers_async(
        location
    )

    result_list_offers = []
    for res in result_list_pub:
        publisher_name = res.name

        # Create tuple (future, publisher_name), since result future does not contain "publisher_name"
        result_list_offers.append((
            asyncio.ensure_future(client.virtual_machine_images.list_offers_async(
                location,
                publisher_name
            )),
            publisher_name
        ))

    while result_list_offers:
        result_list_skus = []
        list_offer_future, publisher_name = result_list_offers.pop(0)
        for offer in await list_offer_future:
            offer_name = offer.name
            # Create tuple (future, publisher_name, offer_name)
            result_list_skus.append((
                asyncio.ensure_future(client.virtual_machine_images.list_skus_async(
                    location,
                    publisher_name,
                    offer_name
                )),
                publisher_name,
                offer_name
            ))
        while result_list_skus:
            list_skus_future, publisher_name, offer_name = result_list_skus.pop(0)
            for skus in await list_skus_future:
                sku_name = skus.name

                # Create tuple (future, publisher_name, offer_name, sku_name)
                result_list.append((
                    asyncio.ensure_future(client.virtual_machine_images.list_async(
                        location,
                        publisher_name,
                        offer_name,
                        sku_name
                    )),
                    publisher_name,
                    offer_name,
                    sku_name
                ))
        
    for version_future, publisher_name, offer_name, sku_name in result_list:
        for version in await version_future:
            result.append((
                publisher_name,
                offer_name,
                sku_name,
                version,
            ))

    return result


def main():
    credentials, SUBSCRIPTION_ID = get_azure_cli_credentials()
    client = ComputeManagementClient(credentials, SUBSCRIPTION_ID)

    print("Async tests")
    loop = asyncio.get_event_loop()
    before = time.time()
    result = loop.run_until_complete(test_vm_images_async(client))
    after = time.time()
    print("Time elapsed: {}".format(after - before))
    print("Result lenght: {}".format(len(result)))

if __name__ == "__main__":
    main()
