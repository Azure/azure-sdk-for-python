# Enumerate updates using Device Update for IoT Hub client SDK

In this sample we will enumerate updates imported to Device Update for IoT Hub using Python SDK client library.

## Prerequisites

* Python 3.6 or later is required to use this package
* You need an [Azure subscription][https://azure.microsoft.com/free/], and a [Device Update for IoT Hub][https://docs.microsoft.com/azure/iot-hub-device-update/understand-device-update] 
account and instance to use this package.

Set the following environment variables:

- `AZURE_CLIENT_ID`: AAD service principal client id
- `AZURE_TENANT_ID`: AAD tenant id
- `AZURE_CLIENT_SECRET` or `AZURE_CLIENT_CERTIFICATE_PATH`: AAD service principal client secret

- `DEVICEUPDATE_ENDPOINT`: Device Update for IoT Hub hostname
- `DEVICEUPDATE_INSTANCE_ID`: Device Update for IoT Hub instance name
- `DEVICEUPDATE_UPDATE_PROVIDER`: Update provider to retrieve
- `DEVICEUPDATE_UPDATE_NAME`: Update name to retrieve
- `DEVICEUPDATE_UPDATE_VERSION`: Update version to retrieve

## Sample

The sample will enumerate already imported device updates from Device Update for IoT Hub.

### Get update client

First we need to instantiate service client (using environment variables):

``` python
endpoint = os.environ["DEVICEUPDATE_ENDPOINT"]
instance = os.environ["DEVICEUPDATE_INSTANCE_ID"]
client = DeviceUpdateClient(credential=DefaultAzureCredential(), endpoint=endpoint, instance_id=instance)
```

### Enumerate update providers

Let's start by enumerating all update providers:

``` python
response = client.device_update.list_providers()
for item in response:
    print(f"  {item}")
```

### Enumerate update names

Let's enumerate all update names for a given update provider:

``` python
update_provider = os.environ["DEVICEUPDATE_UPDATE_PROVIDER"]
response = client.device_update.list_names(update_provider)
for item in response:
    print(f"  {item}")
```

### Enumerate update versions

Let's enumerate all update version for a given update provider and update name:

``` python
update_name = os.environ["DEVICEUPDATE_UPDATE_NAME"]
response = client.device_update.list_versions(update_provider, update_name)
for item in response:
    print(f"  {item}")
```
