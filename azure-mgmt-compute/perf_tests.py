import asyncio
import time

from azure.mgmt.compute.v2017_12_01 import ComputeManagementClient
from devtools_testutils.mgmt_settings_real import SUBSCRIPTION_ID, get_credentials

from azure.mgmt.compute.v2017_12_01.operations.virtual_machine_images_operations_async import VirtualMachineImagesOperations
#from azure.mgmt.compute.v2017_12_01.operations import VirtualMachineImagesOperations
print(VirtualMachineImagesOperations)

IMAGES_TO_PULL = 40

def test_vm_images_sync(client):
    result = []
    location = "westus"
    result_list_pub = client.virtual_machine_images.list_publishers(
        location
    )
    for res in result_list_pub:
        publisher_name = res.name

        result_list_offers = client.virtual_machine_images.list_offers(
            location,
            publisher_name
        )

        for res in result_list_offers:
            offer = res.name

            result_list_skus = client.virtual_machine_images.list_skus(
                location,
                publisher_name,
                offer
            )

            for res in result_list_skus:
                skus = res.name

                result_list = client.virtual_machine_images.list(
                    location,
                    publisher_name,
                    offer,
                    skus
                )

                for res in result_list:
                    version = res.name

                    result_get = client.virtual_machine_images.get(
                        location,
                        publisher_name,
                        offer,
                        skus,
                        version
                    )
                    result.append((
                        publisher_name,
                        offer,
                        skus,
                        version,
                        result_get
                    ))

    return result

def main():
    credentials = get_credentials()
    client = ComputeManagementClient(credentials, SUBSCRIPTION_ID)

    print(client.virtual_machine_images)

    print("Sync tests")
    before = time.time()
    test_vm_images_sync(client)
    after = time.time()
    print("Time elapsed: {}".format(after - before))

if __name__ == "__main__":
    main()
