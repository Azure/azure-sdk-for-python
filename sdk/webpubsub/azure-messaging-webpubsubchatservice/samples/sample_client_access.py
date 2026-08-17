# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------
import os


def client_access():
    # [START client_access]
    import os
    from azure.messaging.webpubsubservice.chat import WebPubSubChatServiceClient

    connection_string = os.environ["WPS_CHAT_CONNECTION_STRING"]
    with WebPubSubChatServiceClient.from_connection_string(
        connection_string,
        os.environ.get("WPS_CHAT_HUB", "test_hub"),
    ) as client:
        access = client.get_client_access_token(user_id="sample-user")
        print(access["url"])
    # [END client_access]


def main():
    if not os.environ.get("WPS_CHAT_CONNECTION_STRING"):
        print("Set WPS_CHAT_CONNECTION_STRING to run this sample.")
        return
    client_access()


if __name__ == "__main__":
    main()
