# coding=utf-8

from azure.communication.messages import NotificationMessagesClient

"""
# PREREQUISITES
    pip install azure-communication-messages
# USAGE
    python stream_get_media.py
"""


def main():
    client = NotificationMessagesClient(
        endpoint="https://my-resource.communication.azure.com",
        credential="CREDENTIAL",
    )

    response = client.download_media(
        id="d19e68ec-bdd6-4a50-8dfb-cbb1642df6ab",
    )
    print(response)


# x-ms-original-file: 2025-01-15-preview/Stream_GetMedia.json
if __name__ == "__main__":
    main()
