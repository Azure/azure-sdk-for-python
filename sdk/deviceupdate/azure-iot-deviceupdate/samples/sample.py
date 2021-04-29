import os
import sys
from samples.runner import SampleRunner

tenant_id = os.getenv("AZURE_TENANT_ID")
client_id = os.getenv("AZURE_CLIENT_ID")
client_secret = os.getenv("AZURE_CLIENT_SECRET")
storage_name = os.getenv("AZURE_STORAGE_NAME")
storage_key = os.getenv("AZURE_STORAGE_KEY")

account_endpoint = os.getenv("AZURE_ACCOUNT_ENDPOINT")
instance_id = os.getenv("AZURE_INSTANCE_ID")
device_id = os.getenv("AZURE_DEVICE_ID")
device_tag = device_id


def sample_device_update(delete):
    print("Device Update for IoT Hub client library for Python sample")
    print()

    runner = SampleRunner(
        tenant_id,
        client_id,
        client_secret,
        account_endpoint,
        instance_id,
        storage_name,
        storage_key,
        device_id,
        device_tag,
        delete=delete)
    runner.run()

    print("Finished.")


if __name__ == '__main__':
    sample_device_update(sys.argv[1].lower() == "true" if len(sys.argv) > 1 else False)
