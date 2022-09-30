# Deploy an update to a group of devices using Device Update for IoT Hub client SDK

In this sample we will deploy an update to a group of devices in Device Update for IoT Hub using Python SDK client library.

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
- `DEVICEUPDATE_DEVICE_GROUP`: Device group to which we want to deploy the update

## Sample

The sample will deploy an update to a group of devices in Device Update for IoT Hub.

### Device management client

First we need to instantiate service client (using environment variables):

``` python
endpoint = os.environ["DEVICEUPDATE_ENDPOINT"]
instance = os.environ["DEVICEUPDATE_INSTANCE_ID"]
client = DeviceUpdateClient(credential=DefaultAzureCredential(), endpoint=endpoint, instance_id=instance)
```

### Create deployment

We will now create a new deployment object:

``` python
update_provider = os.environ["DEVICEUPDATE_UPDATE_PROVIDER"]
update_name = os.environ["DEVICEUPDATE_UPDATE_NAME"]
update_version = os.environ["DEVICEUPDATE_UPDATE_VERSION"]
group = os.environ["DEVICEUPDATE_DEVICE_GROUP"]
deployment_id = uuid.uuid4().hex
deployment = {
    "deploymentId": deployment_id,
    "startDateTime": str(datetime.now(timezone.utc)),
    "update": {
        "updateId": {
            "provider": update_provider,
            "name": update_name,
            "version": update_version
        }
    },
    "groupId": group
}
```

### Deploy update

We can now deploy the update:

``` python
response = client.device_management.create_or_update_deployment(group, deployment_id, deployment)
```

### Check deployment state

We can now monitor deployment state:

``` python
response = client.device_management.get_deployment(group, deployment_id)
print(response)
```
