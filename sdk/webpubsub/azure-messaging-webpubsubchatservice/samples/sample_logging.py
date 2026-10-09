# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------
import os


def configure_logging():
    # [START configure_logging]
    import logging
    import os
    import sys

    from azure.identity import DefaultAzureCredential
    from azure.messaging.webpubsubchatservice import WebPubSubChatServiceClient

    logger = logging.getLogger("azure")
    logger.setLevel(logging.DEBUG)
    logger.addHandler(logging.StreamHandler(stream=sys.stdout))

    with DefaultAzureCredential() as credential:
        with WebPubSubChatServiceClient(
            os.environ["WPS_CHAT_ENDPOINT"],
            os.environ.get("WPS_CHAT_HUB", "test_hub"),
            credential,
            logging_enable=True,
        ) as client:
            print(type(client).__name__)
    # [END configure_logging]


def main():
    if not os.environ.get("WPS_CHAT_ENDPOINT"):
        raise SystemExit("Set WPS_CHAT_ENDPOINT to run this sample.")
    configure_logging()


if __name__ == "__main__":
    main()
