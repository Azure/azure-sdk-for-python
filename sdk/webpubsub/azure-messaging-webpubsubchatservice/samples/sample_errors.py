# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------
import os

from azure.messaging.webpubsubchatservice import WebPubSubChatServiceClient


def handle_service_errors(client):
    # [START handle_service_errors]
    import os
    from azure.core.exceptions import HttpResponseError

    try:
        role = client.get_role(os.environ.get("WPS_CHAT_ROLE_NAME", "user.python_sample"))
        print(role.name, role.permissions)
    except HttpResponseError as error:
        print(f"Chat service request failed with status {error.status_code}")
        raise
    # [END handle_service_errors]


def main():
    if not os.environ.get("WPS_CHAT_CONNECTION_STRING"):
        raise SystemExit("Set WPS_CHAT_CONNECTION_STRING to run this sample.")
    with WebPubSubChatServiceClient.from_connection_string(
        os.environ["WPS_CHAT_CONNECTION_STRING"], os.environ.get("WPS_CHAT_HUB", "test_hub")
    ) as client:
        handle_service_errors(client)


if __name__ == "__main__":
    main()
