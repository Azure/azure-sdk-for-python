# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------
import os
import logging
from azure.messaging.webpubsubclient import WebPubSubClient, WebPubSubClientCredential
from azure.messaging.webpubsubservice import WebPubSubServiceClient
from azure.messaging.webpubsubclient.models import OpenClientError, SendMessageError
from dotenv import load_dotenv

load_dotenv()

_LOGGER = logging.getLogger(__name__)

# The following code is to show how to handle exceptions in WebPubSubClient, and it
# may not run directly
def main():
    service_client = WebPubSubServiceClient.from_connection_string(  # type: ignore
        connection_string=os.getenv("WEBPUBSUB_CONNECTION_STRING", ""), hub="hub"
    )
    client = WebPubSubClient(
        credential=WebPubSubClientCredential(
            client_access_url_provider=lambda: service_client.get_client_access_token(
                roles=["webpubsub.joinLeaveGroup", "webpubsub.sendToGroup"]
            )["url"]
        ),
    )
    # catch OpenClientError
    while True:
        try:
            client.open()
            break
        # you may just want to try again
        except OpenClientError:
            pass

    # catch SendMessageError
    while True:
        try:
            client.join_group(group_name="hello_world_exceptions")
            break
        except SendMessageError as err:
            if err.error_detail is None:
                # connection is closed, and you may need to open client again
                client.close()
                client.open()
            elif err.error_detail.name == "NoAckMessageReceivedFromServer":
                # no ack from service, you may want to try again
                pass
            # for other name of error detail, it belongs to your business logic and you
            # may want to handle it with reference of https://learn.microsoft.com/azure/azure-web-pubsub/concept-client-protocols#ack-response
            elif err.error_detail.name == "...":
                pass
                
    client.close()


if __name__ == "__main__":
    main()
