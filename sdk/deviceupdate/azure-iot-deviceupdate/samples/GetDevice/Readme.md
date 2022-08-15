# Get device information using Device Update for IoT Hub client SDK

In this sample we will retrieve some basic device management information from Device Update for IoT Hub using Python SDK client library.

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
- `DEVICEUPDATE_DEVICE_GROUP`: Device group for which we will retrieve best updates for

## Sample

The sample will retrieve several information from Device Update for IoT Hub.

### Device management client

First we need to instantiate service client (using environment variables):

``` python
endpoint = os.environ["DEVICEUPDATE_ENDPOINT"]
instance = os.environ["DEVICEUPDATE_INSTANCE_ID"]
client = DeviceUpdateClient(credential=DefaultAzureCredential(), endpoint=endpoint, instance_id=instance)
```

### Enumerate devices

We can now enumerate all registered devices and print their device identifiers:

``` python
response = client.device_management.list_devices()
for item in response:
    print(f"  {item['deviceId']}")
```

### Enumerate device groups

We can enumerate all available device groups and print their group identifiers:

``` python
response = client.device_management.list_groups()
for item in response:
    print(f"  {item['groupId']}")
```

### Enumerate device classes

We can enumerate all available device classes and print their device class identifiers:

``` python
response = client.device_management.list_device_classes()
for item in response:
    print(f"  {item['deviceClassId']}")
```

### Get best updates for all devices within a specific device group

Finally, lets find out all best updates for all devices in a specific group, groupped by their device class identifier:

``` python
group = os.environ["DEVICEUPDATE_DEVICE_GROUP"]
response = client.device_management.list_best_updates_for_group(group)
for item in response:
    print(f"  {item['update']['updateId']['provider']}")
    print(f"  {item['update']['updateId']['name']}")
    print(f"  {item['update']['updateId']['version']}")
```
