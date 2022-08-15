# Import update using Device Update for IoT Hub client SDK

In this sample we will import update to Device Update for IoT Hub using Python SDK client library.

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

- `DEVICEUPDATE_PAYLOAD_FILE`: Payload local file path
- `DEVICEUPDATE_PAYLOAD_URL`: Payload Azure Blob URL
- `DEVICEUPDATE_MANIFEST_FILE`: Import manifest local file path
- `DEVICEUPDATE_MANIFEST_URL`: Import manifest Azure Blob URL

## Sample

The sample will import update to Device Update for IoT Hub.

### Create service client

Let's assume you have device update (provided by device builder) and you want to import it into your Device Update for IoT Hub instance. 
For device update to be importable you need not only the actual payload file but also the corresponding import manifest document. 
See [Import-Concepts](https://docs.microsoft.com/azure/iot-hub-device-update/import-concepts) for details about import manifest.

``` python
endpoint = os.environ["DEVICEUPDATE_ENDPOINT"]
instance = os.environ["DEVICEUPDATE_INSTANCE_ID"]
client = DeviceUpdateClient(credential=DefaultAzureCredential(), endpoint=endpoint, instance_id=instance)
```

### Create import request

Before we can import device update, we need to upload all device update artifacts, in our case payload file and import 
manifest file, to an Azure Blob container. Let's assume we have local artifact file and import manifest 
local filepath as well as Azure Blob Urls save in environment variables..

We will need to be able to calculate file hash and file size. For that we will use the following methods:

``` python
def get_file_size(file_path):
    return os.path.getsize(file_path)

def get_file_hash(file_path):
    with open(file_path, "rb") as f:
        bytes = f.read()  # read entire file as bytes
        return base64.b64encode(hashlib.sha256(bytes).digest()).decode("utf-8")
```

Now we can create import request.

``` python
payload_file = os.environ["DEVICEUPDATE_PAYLOAD_FILE"]
payload_url = os.environ["DEVICEUPDATE_PAYLOAD_URL"]
manifest_file = os.environ["DEVICEUPDATE_MANIFEST_FILE"]
manifest_url = os.environ["DEVICEUPDATE_MANIFEST_URL"]

content = [{
    "importManifest": {
        "url": manifest_url,
        "sizeInBytes": get_file_size(manifest_file),
        "hashes": {
            "sha256": get_file_hash(manifest_file)
        }
    },
    "files": [{
        "fileName": os.path.basename(payload_file),
        "url": payload_url
    }]
}]
```

### Import update

Now we can start import process.

``` python
response = client.device_update.begin_import_update(content)
response.wait
```
