# Azure IoT Device Provisioning client library for Python Samples

These are code samples that show common usage of the Azure IoT Device Provisioning client library.
The async versions of any sample files will be appended with `_async` to show async client usage examples.


## Prerequisites
* Python 3.7 or later is required to use this package
* You must have an [Azure subscription](https://azure.microsoft.com/free/) and an
[Azure IoT Device Provisioning Service](https://learn.microsoft.com/azure/iot-dps/) resource to run these samples.

## Setup

1. Install the Azure IoT Device Provisioning client library for Python with [pip](https://pypi.org/project/pip/):

```bash
pip install azure-iot-deviceprovisioning
```

2. Clone or download this sample repository
3. Open the sample folder in Visual Studio Code or your IDE of choice.

## Running the samples

1. Open a terminal window and `cd` to the directory that the samples are saved in.
2. Set the environment variables specified in the sample file you wish to run.
3. Follow the usage described in the file, e.g. `python dps_service_sample_individual_enrollments.py`

## Samples

- [Client Initialization and Credentials](https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/iothub/azure-iot-deviceprovisioning/samples/dps_service_sample_client_authentication.py) ([async version](https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/iothub/azure-iot-deviceprovisioning/samples/dps_service_sample_client_authentication_async.py)):
    - Connection string authentication
    - Using AzureNamedKey credentials
    - Using AzureSasCredential authentication
    - Using custom Active Directory credentials
    - Using Default Azure Credentials

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
    - Create a symmetric key individual enrollment with initial twin properties
    - Create a TPM attestation individual enrollment
    - Create an x509 certificate individual enrollment
    - Get an individual enrollment
    - Update an individual enrollment
    - Update reprovisioning policy of an enrollment
    - Get an individual enrollment's attestation mechanism
    - Bulk individual enrollment operations
    - Delete an individual enrollment


## Next steps

Check out the [API reference documentation](https://learn.microsoft.com/rest/api/iot-dps/) to learn more about
what you can do with the Azure IoT Device Provisioning client library.