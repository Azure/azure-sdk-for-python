from azure.servicebus import ServiceBusClient
import logging

logging.basicConfig(level=logging.DEBUG)

conn_str = "Endpoint=sb://llaw-sb-test.servicebus.windows.net/;SharedAccessKeyName=RootManageSharedAccessKey;SharedAccessKey=t1SD+YrDxGWJ6wAAQuj+1vgJlb77mAbsCiDXkaxYQx0="
topic_name = "cr_cert"
subscription_name = "cr_cert"
# certificates = "C:\\Users\\llawrence\\Documents\\38_cert\\Lib\\site-packages\\certifi\\cacert.pem"
certificates = "C:\\Users\\llawrence\\Documents\\azure-sdk-for-python\\.certificate\\uamqp_cert.pem"
# certificates = "cacert.pem"

def run():
    with ServiceBusClient.from_connection_string(conn_str, connection_verify=certificates) as client:
        receiver = client.get_subscription_receiver(topic_name, subscription_name)

        while True:
            for msg in receiver.receive_messages():
                print(msg)
run()

# from azure.servicebus.aio import ServiceBusClient
# import logging
# import asyncio

# # logging.basicConfig(level=logging.INFO)

# conn_str = "Endpoint=sb://llaw-sb-test.servicebus.windows.net/;SharedAccessKeyName=RootManageSharedAccessKey;SharedAccessKey=t1SD+YrDxGWJ6wAAQuj+1vgJlb77mAbsCiDXkaxYQx0="
# topic_name = "cr_cert"
# subscription_name = "cr_cert"
# certificates = "cacert.pem"

# async def run():
#     async with ServiceBusClient.from_connection_string(conn_str, connection_verify=certificates) as client:
#         receiver = client.get_subscription_receiver(topic_name, subscription_name)

#         while True:
#             for msg in await receiver.receive_messages():
#                 print(msg)

# asyncio.run(run())