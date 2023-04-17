# Azure IoT Hub Device Provisioning Service client library for Python

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
Install the Azure IoT Hub Device Provisioning Service client library for Python with [pip](https://pypi.org/project/pip/):
```bash
pip install azure-iot-deviceprovisioningservice
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
The Device Provisioning Service client library for Python allows you to interact with three main operational categories: individual enrollments, enrollment groups, and device registration states.

Interaction with these resources starts with an instance of a ProvisioningServiceClient. To create the ProvisioningServiceClient object, you will need the DPS resource's endpoint URL and a credential that allows you to access the resource.

#### Creating the client from Azure credentials
To use an [Azure Active Directory (AAD) token credential](https://learn.microsoft.com/azure/iot-dps/concepts-control-access-dps-azure-ad),
   provide an instance of the desired credential type obtained from the
   [azure-identity](https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/identity/azure-identity#credentials) library.
   For example, [DefaultAzureCredential](https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/identity/azure-identity#defaultazurecredential)
   can be used to authenticate the client.

```python
from azure.iot.deviceprovisioningservice import ProvisioningServiceClient
from azure.identity import DefaultAzureCredential

# Initialize credential object
credential = DefaultAzureCredential()

# Create client using endpoint and credential
client = ProvisioningServiceClient(endpoint="https://my-dps.azure-device-provisioning.net/", credential=credential)
```

#### Using a DPS connection string:
Depending on your use case and authorization method, you may prefer to initialize a client instance with a DPS
connection string instead of providing the endpoint URL and credential separately. To do this, pass the DPS
connection string to the client's `from_connection_string` class method:

```python
from azure.iot.deviceprovisioningservice import ProvisioningServiceClient

connection_string = "Hostname=https;SharedAccessKeyName=xxxx;SharedAccessKey=xxxx"
client = ProvisioningServiceClient.from_connection_string(connection_string=connection_string)
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

The Device Provisioning Service client library for Python allows you to interact with each of these components through different operation namespaces on the ProvisioningServiceClient.

## Examples
The following sections provide several code snippets covering some of the most common DPS service, including:

* [Create an individual device enrollment](#create-an-individual-device-enrollment "Create an individual device enrollment")
* [Create an intermediate x509 enrollment group](#create-an-intermediate-x509-enrollment-group "Create an intermediate x509 enrollment group")
* [Create an x509 CA certificate enrollment group](#create-an-x509-ca-certificate-enrollment-group "Create an x509 CA certificate enrollment group")
* [Check device registration status](#check-device-registration-status "Check device registration status")

### Create an individual device enrollment
Create an individual enrollment to provision an individual device using symmetric key attestation.
```python
from azure.iot.deviceprovisioningservice import ProvisioningServiceClient

# Initialize client
client = ProvisioningServiceClient.from_connection_string(connection_string="<connection_string>")

# Load certificate contents

# Create a symmetric key individual enrollment
client.individual_enrollments.create_or_update(
    id="<enrollment_id>",
    enrollment = {
        "registrationId": "<enrollment_id>"
        "attestation": {
            "type": "symmetricKey",
        },
    }
)
```

### Create an intermediate x509 enrollment group
Create an x509 enrollment group to provision one or more devices using x509 attestation.
```python
from azure.iot.deviceprovisioningservice import ProvisioningServiceClient

# Initialize client
client = ProvisioningServiceClient.from_connection_string(connection_string="<connection_string>")

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
from azure.iot.deviceprovisioningservice import ProvisioningServiceClient

# Initialize client
client = ProvisioningServiceClient.from_connection_string(connection_string="<connection_string>")

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
from azure.iot.deviceprovisioningservice import ProvisioningServiceClient

# Initialize client
client = ProvisioningServiceClient.from_connection_string(connection_string="<connection_string>")

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

## Next steps

### More sample code
Get started with our [samples]<!--(https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/deviceprovisioningservices/azure-iot-deviceprovisioningservice/samples/)-->.

Several samples, as well as async samples, are available to you in the samples directory.

- [Device Registration States]<!--(https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/deviceprovisioningservices/azure-iot-deviceprovisioningservice/samples/dps_service_sample_device_registration.py)--> ([async version]<!--(https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/deviceprovisioningservices/azure-iot-deviceprovisioningservice/samples/dps_service_sample_device_registration_async.py)-->):
    - Create a basic enrollment group
    - Register a device (Requires device SDK)
    - Query device registration states for an enrollment group
    - Get device registration state
    - Delete device registration state

- [Enrollment Groups]<!--(https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/deviceprovisioningservices/azure-iot-deviceprovisioningservice/samples/dps_service_sample_enrollment_groups.py)--> ([async version]<!--(https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/deviceprovisioningservices/azure-iot-deviceprovisioningservice/samples/dps_service_sample_enrollment_groups_async.py)-->):
    - Create a symmetric key enrollment group
    - Create an x509 certificate enrollment group
    - Get an enrollment group
    - Update an enrollment group
    - Get enrollment group attestation mechanism
    - Bulk enrollment group operations
    - Delete enrollment group


- [Individual Enrollments]<!--(https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/deviceprovisioningservices/azure-iot-deviceprovisioningservice/samples/dps_service_sample_individual_enrollments.py)--> ([async version]<!--(https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/deviceprovisioningservices/azure-iot-deviceprovisioningservice/samples/dps_service_sample_individual_enrollments_async.py)-->):
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
