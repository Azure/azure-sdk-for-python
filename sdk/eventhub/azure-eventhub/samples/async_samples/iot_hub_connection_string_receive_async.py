#!/usr/bin/env python

# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

"""
This sample demonstrates how to convert an Iot Hub connection string to
an Event Hubs connection string that points to the built-in messaging endpoint.
The Event Hubs connection string is then used with the EventHubConsumerClient to
receive events.
More information about the built-in messaging endpoint can be found at:
https://docs.microsoft.com/en-us/azure/iot-hub/iot-hub-devguide-messages-read-builtin
"""

import os
import time
from base64 import b64encode, b64decode
from hashlib import sha256
from hmac import HMAC
import asyncio
from urllib.parse import urlencode, quote_plus
from uamqp import ReceiveClient, Source
from uamqp.errors import LinkRedirect

from provisioningserviceclient import ProvisioningServiceClient
from provisioningserviceclient.models import IndividualEnrollment, AttestationMechanism
from azure.iot.device.aio import ProvisioningDeviceClient, IoTHubDeviceClient
from azure.iot.device import Message
from azure.eventhub import EventData
from azure.eventhub.aio import EventHubProducerClient, EventHubConsumerClient


def generate_sas_token(uri, policy, key, expiry=None):
    """Create a shared access signiture token as a string literal.
    :returns: SAS token as string literal.
    :rtype: str
    """
    if not expiry:
        expiry = time.time() + 3600
    encoded_uri = quote_plus(uri)
    ttl = int(expiry)
    sign_key = '%s\n%d' % (encoded_uri, ttl)
    signature = b64encode(HMAC(b64decode(key), sign_key.encode('utf-8'), sha256).digest())
    result = {
        'sr': uri,
        'sig': signature,
        'se': str(ttl)}
    if policy:
        result['skn'] = policy
    return 'SharedAccessSignature ' + urlencode(result)

async def send_messages_with_provisioned_iot_device(iothub_conn_str):
    #dps_conn_str = 'HostName=swathip-test-iot-provisioning.azure-devices-provisioning.net;SharedAccessKeyName=provisioningserviceowner;SharedAccessKey=eR3Vnxivm9R40MbtgAJ9slsh7TQdYzYj7Dgdohg28kE='
    ##os.environ["DPS_SERVICE_CONNECTION_STR"]
    #endorsement_key = 'AToAAQALAAMAsgAgg3GXZ0SEs/gakMyNRqXXJP1S124GUgtk8qHaGzMUaaoABgCAAEMAEAgAAAAAAAEAtW6MOyCu/Nih47atIIoZtlYkhLeCTiSrtRN3q6hqgOllA979No4BOcDWF90OyzJvjQknMfXS/Dx/IJIBnORgCg1YX/j4EEtO7Ase29Xd63HjvG8M94+u2XINu79rkTxeueqW7gPeRZQPnl1xYmqawYcyzJS6GKWKdoIdS+UWu6bJr58V3xwvOQI4NibXKD7htvz07jLItWTFhsWnTdZbJ7PnmfCa2vbRH/9pZIow+CcAL9mNTNNN4FdzYwapNVO+6SY/W4XU0Q+dLMCKYarqVNH5GzAWDfKT8nKzg69yQejJM8oeUWag/8odWOfbszA+iFjw3wVNrA5n8grUieRkPQ=='
    ##os.environ["DPS_ENDORSEMENT_KEY"]
    #registration_id = 'test_registration_id'
    ##os.environ["DPS_REGISTRATION_ID"]
    #provisioning_host = os.getenv("PROVISIONING_HOST")
    #id_scope = os.getenv("PROVISIONING_IDSCOPE")
    #provisioning_service_client = ProvisioningServiceClient.create_from_connection_string(dps_conn_str)
    ##registration_id = os.getenv("PROVISIONING_REGISTRATION_ID")
    ##symmetric_key = os.getenv("PROVISIONING_SYMMETRIC_KEY")
    #att_mech = AttestationMechanism.create_with_tpm(endorsement_key)
    #individual_enrollment = IndividualEnrollment.create(registration_id, att_mech, device_id='test-device-id')
    ##provisioning_service_client.delete(individual_enrollment)
    #individual_enrollment = provisioning_service_client.create_or_update(individual_enrollment)

    ##provisioning_device_client = ProvisioningDeviceClient.create_from_symmetric_key(
    ##    provisioning_host=provisioning_host,
    ##    registration_id=registration_id,
    ##    id_scope=id_scope,
    ##    symmetric_key=symmetric_key,
    ##)

    #print(dir(individual_enrollment))
    #registration_state = individual_enrollment.registration_state
    #print(dir(registration_state))
    #registration_result = await provisioning_service_client.register()

    #print("The complete registration result is")
    #print(registration_result.registration_state.device_id)

    #if registration_result.status == "assigned":
    #device_client = IoTHubDeviceClient.create_from_symmetric_key(
    #    symmetric_key=symmetric_key,
    #    hostname=registration_result.registration_state.assigned_hub,
    #    device_id=registration_result.registration_state.device_id,
    #)
    device_client = IoTHubDeviceClient.create_from_connection_string('HostName=swathip-test-iot-hub-aaaaaaaaaa.azure-devices.net;DeviceId=swathip-test-device-id;SharedAccessKey=5ho6Stu6VHIjmzz+bZl8w0EfvwhlXprup2HePcy0f20=')
    # Connect the client.
    await device_client.connect()

    for i in range(3):
        message = Message("Sending to IotHub, message {}".format(i))
        print("Sending message: {}".format(message))
        await device_client.send_message(message)
        print("Message sent succesfully.")
        time.sleep(1)

    # finally, disconnect
    await device_client.disconnect()
    #else:
    #    print("Can not send messages from the provisioned device")

def parse_iot_conn_str(iothub_conn_str):
    hostname = None
    shared_access_key_name = None
    shared_access_key = None
    for element in iothub_conn_str.split(';'):
        key, _, value = element.partition('=')
        if key.lower() == 'hostname':
            hostname = value.rstrip('/')
        elif key.lower() == 'sharedaccesskeyname':
            shared_access_key_name = value
        elif key.lower() == 'sharedaccesskey':
            shared_access_key = value
    if not all([hostname, shared_access_key_name, shared_access_key]):
        raise ValueError("Invalid connection string")
    return hostname, shared_access_key_name, shared_access_key

def convert_iothub_to_eventhub_conn_str(iothub_conn_str):
    hostname, shared_access_key_name, shared_access_key = parse_iot_conn_str(iothub_conn_str)
    iot_hub_name = hostname.split(".")[0]
    operation = '/messages/events/ConsumerGroups/{}/Partitions/{}'.format('$Default', 0)
    username = '{}@sas.root.{}'.format(shared_access_key_name, iot_hub_name)
    sas_token = generate_sas_token(hostname, shared_access_key_name, shared_access_key)
    uri = 'amqps://{}:{}@{}{}'.format(quote_plus(username),
                                      quote_plus(sas_token), hostname, operation)
    source_uri = Source(uri)
    receive_client = ReceiveClient(source_uri)
    try:
        receive_client.receive_message_batch(max_batch_size=1)
    except LinkRedirect as redirect:
        # Once a redirect error is received, close the original client and recreate a new one to the re-directed address
        receive_client.close()
        fully_qualified_name = redirect.hostname.decode("utf-8")
        print("NAME:")
        print(iot_hub_name)
        print(iot_hub_name[:25])
        conn_str = "Endpoint=sb://{}/;SharedAccessKeyName={};SharedAccessKey={}".format(
            fully_qualified_name,
            shared_access_key_name,
            shared_access_key
            #iot_hub_name[:25]
        )
        print(conn_str)
        return conn_str
    except Exception as exp:
        raise ValueError(
            "{} is not an invalid IoT Hub connection string. The underlying exception is {}".format(
                iothub_conn_str,
                exp,
            )
        )

async def receive_events_from_iothub(iothub_conn_str):
    """Convert the iot hub connection string to the built-in eventhub connection string
    and receive events from the eventhub
    """
    eventhub_conn_str = convert_iothub_to_eventhub_conn_str(iothub_conn_str)
    consumer_client = EventHubConsumerClient.from_connection_string(eventhub_conn_str, consumer_group="$Default")

    async def on_event_batch(partition_context, events):
        # put your code here
        print("received {} events from partition {}".format(len(events), partition_context.partition_id))

    async with consumer_client:
        await consumer_client.receive_batch(
            on_event_batch,
            starting_position=-1  # "-1" is from the beginning of the partition.
        )

async def main():
    iothub_conn_str = 'HostName=swathip-test-iot-hub-aaaaaaaaaa.azure-devices.net;SharedAccessKeyName=iothubowner;SharedAccessKey=u1Lxmqh/gViXrP0cbImpIrxb5eT1R9HOZg97Xuei/do='#HostName=swathip-test-iot.azure-devices.net;SharedAccessKeyName=iothubowner;SharedAccessKey=VNq0G9TZV+ndgqS8lOZ1OmWuinoO7TKZ+r4cVeSmek4='
    #iothub_conn_str = os.environ["IOTHUB_CONNECTION_STR"]
    #device_id = 'swathip-test-iot-device-sample'
    #device_id = os.environ["IOTHUB_DEVICE"]
    await send_messages_with_provisioned_iot_device(iothub_conn_str)
    await receive_events_from_iothub(iothub_conn_str)

loop = asyncio.get_event_loop()
loop.run_until_complete(main())
