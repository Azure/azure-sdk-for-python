import os
import sys
from samples.runner import SampleRunner

tenant_id = "72f988bf-86f1-41af-91ab-2d7cd011db47"  # os.getenv("AZURE_TENANT_ID")
client_id = "1e5942b3-36f1-43eb-88d9-98c12d95000b"  # os.getenv("AZURE_CLIENT_ID")
storage_name = os.getenv("AZURE_STORAGE_NAME")
storage_key = os.getenv("AZURE_STORAGE_KEY")

account_endpoint = "adu-sdk-testing.api.adu.microsoft.com"  # os.getenv("AZURE_ACCOUNT_ENDPOINT")
instance_id = "sdkinstance"  # os.getenv("AZURE_INSTANCE_ID")
device_tag = "joegroup"


def sample_device_update(delete):
    print("Device Update for IoT Hub client library for Python sample")
    print()

    runner = SampleRunner(
        tenant_id,
        client_id,
        account_endpoint,
        instance_id,
        storage_name,
        storage_key,
        device_tag,
        delete=delete)
    runner.run()

    print("Finished.")


if __name__ == '__main__':
    sample_device_update(sys.argv[1].lower() == "true" if len(sys.argv) > 1 else False)
