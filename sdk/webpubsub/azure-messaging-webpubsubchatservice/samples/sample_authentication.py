# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------
import os


def connection_string_auth():
    # [START connection_string_auth]
    import os
    from azure.messaging.webpubsubservice.chat import WebPubSubChatServiceClient

    hub = os.environ.get("WPS_CHAT_HUB", "test_hub")
    with WebPubSubChatServiceClient.from_connection_string(
        os.environ["WPS_CHAT_CONNECTION_STRING"], hub
    ) as connection_string_client:
        print(type(connection_string_client).__name__)
    # [END connection_string_auth]


def key_auth():
    # [START key_auth]
    import os
    from azure.core.credentials import AzureKeyCredential
    from azure.messaging.webpubsubservice.chat import WebPubSubChatServiceClient

    endpoint = os.environ["WPS_CHAT_ENDPOINT"]
    hub = os.environ.get("WPS_CHAT_HUB", "test_hub")
    with WebPubSubChatServiceClient(
        endpoint,
        hub,
        AzureKeyCredential(os.environ["WPS_CHAT_ACCESS_KEY"]),
    ) as key_client:
        print(type(key_client).__name__)
    # [END key_auth]


def entra_auth():
    # [START entra_auth]
    import os
    from azure.identity import DefaultAzureCredential
    from azure.messaging.webpubsubservice.chat import WebPubSubChatServiceClient

    endpoint = os.environ["WPS_CHAT_ENDPOINT"]
    hub = os.environ.get("WPS_CHAT_HUB", "test_hub")
    with WebPubSubChatServiceClient(endpoint, hub, DefaultAzureCredential()) as entra_client:
        print(type(entra_client).__name__)
    # [END entra_auth]


def main():
    required = (
        "WPS_CHAT_ENDPOINT",
        "WPS_CHAT_CONNECTION_STRING",
        "WPS_CHAT_ACCESS_KEY",
    )
    missing = [name for name in required if not os.environ.get(name)]
    if missing:
        print(f"Set {', '.join(missing)} to run this sample.")
        return

    connection_string_auth()
    key_auth()
    entra_auth()


if __name__ == "__main__":
    main()
