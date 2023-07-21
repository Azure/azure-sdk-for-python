# Azure IoT Device Provisioning client library for Python

The IoT Hub Device Provisioning Service (DPS) is a helper service for IoT Hub that enables zero-touch, just-in-time provisioning to the right IoT hub without requiring human intervention, allowing customers to provision millions of devices in a secure and scalable manner. 

This service SDK provides data plane operations for backend apps. You can use this service SDK to create and manage individual enrollments and enrollment groups, and to query and manage device registration records.

Learn how to provision devices to your IoT hub(s) with our [quickstarts, tutorials, and samples](https://learn.microsoft.com/azure/iot-dps/).

## Getting started

### Prerequisites
* Python 3.7 or later is required to use this package. For more details, please read our page on [Azure SDK for Python version support policy](https://github.com/Azure/azure-sdk-for-python/wiki/Azure-SDKs-Python-version-support-policy).
* You must have an [Azure subscription](https://azure.microsoft.com/free/) and an
[Azure IoT Hub Device Provisioning Service](https://learn.microsoft.com/azure/iot-dps/about-iot-dps) to use this package.

This package has been tested with Python 3.7+.
For a more complete view of Azure libraries, see the [azure sdk python release](https://aka.ms/azsdk/python/all).


### Install the package
Install the Azure IoT Device Provisioning client library for Python with [pip](https://pypi.org/project/pip/):
```bash
pip install azure-iot-deviceprovisioning
```

### Create an IoT Hub Device Provisioning Service
If you wish to create a new Device Provisioning Service, you can use the
[Azure CLI](https://learn.microsoft.com/azure/iot-dps/quick-setup-auto-provision-cli):

```bash
# Create a new resource group (if necessary)
az group create --name my-resource-group --location westus2

# Create the DPS instance
az iot dps create --name my-dps --resource-group my-resource-group --location westus2
```

[Azure Portal](https://learn.microsoft.com/azure/iot-dps/quick-setup-auto-provision),
or [Bicep](https://learn.microsoft.com/azure/iot-dps/quick-setup-auto-provision-bicep?tabs=CLI),

### Create the client
The Azure IoT Device Provisioning client library for Python allows you to interact with three main operational categories: individual enrollments, enrollment groups, and device registration states.

Interaction with these resources starts with an instance of a DeviceProvisioningClient. To create the DeviceProvisioningClient object, you will need the DPS resource's endpoint URL and a credential that allows you to access the resource.

#### Creating the client from Azure credentials
To use an [Azure Active Directory (AAD) token credential](https://learn.microsoft.com/azure/iot-dps/concepts-control-access-dps-azure-ad),
   provide an instance of the desired credential type obtained from the
   [azure-identity](https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/identity/azure-identity#credentials) library.
   For example, [DefaultAzureCredential](https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/identity/azure-identity#defaultazurecredential)
   can be used to authenticate the client.

```python
from azure.iot.deviceprovisioning import DeviceProvisioningClient
from azure.identity import DefaultAzureCredential

# Initialize credential object
credential = DefaultAzureCredential()

# Create client using endpoint and credential
client = DeviceProvisioningClient(endpoint="https://my-dps.azure-device-provisioning.net/", credential=credential)
```

#### Using a DPS connection string:
Depending on your use case and authorization method, you may prefer to initialize a client instance with a DPS
connection string instead of providing the endpoint URL and credential separately. To do this, pass the DPS
connection string to the client's `from_connection_string` class method:

```python
from azure.iot.deviceprovisioning import DeviceProvisioningClient

connection_string = "Hostname=https;SharedAccessKeyName=xxxx;SharedAccessKey=xxxx"
client = DeviceProvisioningClient.from_connection_string(connection_string=connection_string)
```

#### Using SAS Credentials
A client instance can also be initialized with an `AzureNamedKeyCredential` using individual components of a DPS resource's Shared Access Policy, as well as an `AzureSasCredential` using a SAS token generated from the policy components and the DPS endpoint string.

```python
from azure.iot.deviceprovisioning import DeviceProvisioningClient
from azure.iot.deviceprovisioning import generate_sas_token
from azure.core.credentials import AzureNamedKeyCredential, AzureSasCredential

dps_endpoint = "https://my-dps.azure-device-provisioning.net/"
policy_name = "<access_policy_name>"
policy_key = "<access_policy_primary_key>"


# AzureNamedKeyCredential
credential = AzureNamedKeyCredential(name=policy_name, key=policy_key)

# AzureSasCredential
sas_token = generate_sas_token(dps_endpoint, policy_name, policy_key)
credential = AzureSasCredential(signature=sas_token)

client = DeviceProvisioningClient(endpoint=dps_endpoint, credential=credential)
```

### Async Clients 
This library includes a complete async API supported on Python 3.5+. To use it, you must
first install an async transport, such as [aiohttp](https://pypi.org/project/aiohttp/).
See
[azure-core documentation](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/core/azure-core/CLIENT_LIBRARY_DEVELOPER.md#transport)
for more information.

## Key concepts
The following operation groups comprise the Service data plane layer:
1. [Individual enrollments](https://learn.microsoft.com/azure/iot-dps/concepts-service#individual-enrollment)
2. [Enrollment groups](https://learn.microsoft.com/azure/iot-dps/concepts-service#enrollment-group)
3. [Device registration](https://learn.microsoft.com/azure/iot-dps/concepts-service#registration-record)

The Azure IoT Device Provisioning client library for Python allows you to interact with each of these components through different operation namespaces on the DeviceProvisioningClient.

## Examples
The following sections provide several code snippets covering some of the most common DPS service, including:

* [Create an individual device enrollment](#create-an-individual-device-enrollment "Create an individual device enrollment")
* [Create an enrollment with reprovisioning policies](#create-an-enrollment-with-reprovisioning-policies "Create an enrollment with reprovisioning policies")
* [Create an intermediate x509 certificate enrollment group](#create-an-intermediate-x509-certificate-enrollment-group "Create an intermediate x509 certificate enrollment group")
* [Create an x509 CA certificate enrollment group](#create-an-x509-ca-certificate-enrollment-group "Create an x509 CA certificate enrollment group")
* [Check device registration status](#check-device-registration-status "Check device registration status")

### Create an individual device enrollment
Create a symmetric key enrollment to provision an individual device and configure its initial state.
```python
from azure.iot.deviceprovisioning import DeviceProvisioningClient

# Initialize client
client = DeviceProvisioningClient.from_connection_string(connection_string="<connection_string>")

# Construct initial twin with desired properties of {"key": "value"} and a tag of {"env": "Development"}
initial_twin = {
    "properties": {
        "desired": {
            "key": "value"
        }
    },
    "tags": {
        "env": "Development"
    }
}

# Create a symmetric key individual enrollment with initial twin
client.individual_enrollment.create_or_update(
    id="<enrollment_id>",
    enrollment = {
        "registrationId": "<enrollment_id>",
        "attestation": {
            "type": "symmetricKey",
        },
        "deviceId": "<device_id>",
        "initialTwin": initial_twin
    }
)
```

### Create an enrollment with reprovisioning policies
Create an individual enrollment with a specific reprovisioning policy.
```python
from azure.iot.deviceprovisioning import DeviceProvisioningClient

# Initialize client
client = DeviceProvisioningClient.from_connection_string(connection_string="<connection_string>")

# Create a reprovisioning policy to migrate the device's data and reassess hub assignment
reprovision_policy = {
    "migrateDeviceData": True,
    "updateHubAssignment": True
}

# Create a symmetric key individual enrollment with reprovisioning policy
client.individual_enrollment.create_or_update(
    id="<enrollment_id>",
    enrollment = {
        "registrationId": "<enrollment_id>",
        "attestation": {
            "type": "symmetricKey",
        },
        "deviceId": "<device_id>",
        "reprovisionPolicy": reprovision_policy
    }
)
```

### Create an intermediate x509 certificate enrollment group
Create an x509 enrollment group to provision one or more devices using x509 attestation.
```python
from azure.iot.deviceprovisioning import DeviceProvisioningClient

# Initialize client
client = DeviceProvisioningClient.from_connection_string(connection_string="<connection_string>")

# Load certificate contents
certificate = open("certificate.pem", "rt", encoding="utf-8")
cert_contents = certificate.read()

# Create x509 enrollment group with an intermediate cert
client.enrollment_groups.create_or_update(
    id="<enrollment_group_id>",
    enrollment_group={
        "enrollmentGroupId": "<enrollment_group_id>",
        "attestation": {
            "type": "x509",
            "x509": {
                "signingCertificates": {
                    "primary": {"certificate": f"{cert_contents}"},
                    "secondary": {"certificate": f"{cert_contents}"},
                }
            },
        },
    }
)
```

### Create an x509 CA certificate enrollment group
Create an enrollment group with an x509 CA certificate attestation. 
This will ensure a registered device's certificate chain has been signed by the target CA cert at the control plane layer.
```python
from azure.iot.deviceprovisioning import DeviceProvisioningClient

# Initialize client
client = DeviceProvisioningClient.from_connection_string(connection_string="<connection_string>")

# Load certificate contents
ca_certificate = open("ca_certificate.pem", "rt", encoding="utf-8")
ca_contents = certificate.read()

# Create x509 enrollment group with CA References
client.enrollment_groups.create_or_update(
    id="<enrollment_group_id>",
    enrollment_group={
        "enrollmentGroupId": "<enrollment_group_id>",
        "attestation": {
            "type": "x509",
            "x509": {
                "caReferences": {
                    "primary": f"{ca_contents}",
                    "secondary": f"{ca_contents}",
                }
            },
        },
    }
)
```

### Check device registration status
```python
from azure.iot.deviceprovisioningservice import DeviceProvisioningClient

# Initialize client
client = DeviceProvisioningClient.from_connection_string(connection_string="<connection_string>")

# Query device registrations for an enrollment group
device_registrations = client.device_registration_state.query(
    id="<enrollment_group_id>"
)

# Get device registration status for a particular device
state = client.device_registration_state.get(
    id="<device_id>"
)
```


## Troubleshooting


### Connection String errors
If you see an error message that states `IoT DPS connection string has missing property: [property]`, it indicates that your connection string is not formed correctly.

Please ensure your connection string is semicolon-delimited, and contains the following properties: `hostname`, `sharedaccesskeyname`, and `sharedaccesskey`.

### Standard HTTPResponse errors
The client methods in this SDK raise an [HttpResponseError](https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/core/azure-core#httpresponseerror) on request failure.
The HttpResponseError raised by the Azure IoT Hub Device Provisioning client library includes detailed error response information that provides useful insights into what went wrong and includes corrective actions to fix common issues.

This error information can be found inside the `message` property of the `HttpResponseError` instance.

Here is an example of how to catch and handle these errors:

```python
try:
    client.individual_enrollment.create_or_update(
        id="<enrollment_id>",
        enrollment = {
            "registrationId": "<enrollment_id>",
            "attestation": {
                "type": "symmetricKey",
            },
        }
    )
except HttpResponseError as error:
    # handle the error here
    if error.status_code == 409:
        pass
```

- `HTTP 400` errors indicate a malformed or bad request. Verify that your inputs are of the correct type and that you have provided all required properties.

- `HTTP 401` errors indicate problems authenticating. Check the exception message or logs for more information.

- `HTTP 403` errors indicate that the provided user credentials are not authorized to perform a specific operation on this Device Provisioning Service resource. 
This can also occur if you have incorrectly generated a SAS credential. Verify your credentials and ensure access to your DPS resource.

- `HTTP 409` errors indicate a resource conflict. This can occur if:
  - You are trying to create an object that already exists
  - You are updating an object using a `create_or_update_` method without providing an `eTag` / `if-match` value

## Next steps

### More sample code
Get started with our [samples](https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/iothub/azure-iot-deviceprovisioning/samples/).
prov
Several samples, as well as async samples, are available to you in the samples directory.

- [Device Registration States](https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/iothub/azure-iot-deviceprovisioning/samples/dps_service_sample_device_registration.py) ([async version](https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/iothub/azure-iot-deviceprovisioning/samples/dps_service_sample_device_registration_async.py)):
    - Create a basic enrollment group
    - Register a device (Requires device SDK)
    - Query device registration states for an enrollment group
    - Get device registration state
    - Delete device registration state

- [Enrollment Groups](https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/iothub/azure-iot-deviceprovisioning/samples/dps_service_sample_enrollment_groups.py) ([async version](https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/iothub/azure-iot-deviceprovisioning/samples/dps_service_sample_enrollment_groups_async.py)):
    - Create a symmetric key enrollment group
    - Create an x509 certificate enrollment group
    - Get an enrollment group
    - Update an enrollment group
    - Get enrollment group attestation mechanism
    - Bulk enrollment group operations
    - Delete enrollment group


- [Individual Enrollments](https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/iothub/azure-iot-deviceprovisioning/samples/dps_service_sample_individual_enrollments.py) ([async version](https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/iothub/azure-iot-deviceprovisioning/samples/dps_service_sample_individual_enrollments_async.py)):
    - Create a symmetric key individual enrollment
    - Create a TPM attestation individual enrollment
    - Create an x509 certificate individual enrollment
    - Get an individual enrollment
    - Update an individual enrollment
    - Get an individual enrollment's attestation mechanism
    - Bulk individual enrollment operations
    - Delete an individual enrollment

### Additional documentation
For more extensive documentation on Azure IoT Hub Device Provisioning Service, see the [Azure IoT Hub Device Provisioning Service documentation](https://learn.microsoft.com/azure/iot-dps/) on learn.microsoft.com.

## Contributing
This project welcomes contributions and suggestions.  Most contributions require you to agree to a Contributor License Agreement (CLA) declaring that you have the right to, and actually do, grant us the rights to use your contribution. For details, visit https://cla.microsoft.com.

When you submit a pull request, a CLA-bot will automatically determine whether you need to provide a CLA and decorate the PR appropriately (e.g., label, comment). Simply follow the instructions provided by the bot. You will only need to do this once across all repos using our CLA.

This project has adopted the [Microsoft Open Source Code of Conduct](https://opensource.microsoft.com/codeofconduct/). For more information see the [Code of Conduct FAQ](https://opensource.microsoft.com/codeofconduct/faq/) or contact [opencode@microsoft.com](mailto:opencode@microsoft.com) with any additional questions or comments.
