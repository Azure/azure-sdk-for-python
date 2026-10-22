# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
import os
import time
import asyncio
from argparse import ArgumentParser
from pathlib import Path
from azure.messaging.webpubsubclient.aio import WebPubSubClient, WebPubSubClientCredential
from azure.messaging.webpubsubservice.aio import WebPubSubServiceClient
from azure.messaging.webpubsubclient.models import (
    WebPubSubDataType,
)
from process_monitor import ProcessMonitor, get_base_logger
from dotenv import load_dotenv


async def main(log_file_name: str = "", log_interval: int = 5, duration: int = 24 * 3600, messages_num: int = 1000):
    logger = get_base_logger(__name__, log_file_name)
    load_dotenv()
    service_client = WebPubSubServiceClient.from_connection_string(  # type: ignore
        connection_string=os.getenv("WEBPUBSUB_CONNECTION_STRING", ""), hub="hub"
    )
    async def client_access_url_provider():
        return (await service_client.get_client_access_token(
            roles=["webpubsub.joinLeaveGroup", "webpubsub.sendToGroup"]
        ))["url"]
    client = WebPubSubClient(
        credential=WebPubSubClientCredential(
            client_access_url_provider=client_access_url_provider
        ),
    )
    message = "0" * 1024
    start_time = time.time()
    with ProcessMonitor(logger_name=Path(__file__).name, log_file_name=log_file_name, log_interval=log_interval):
        async with client:
            while time.time() - start_time < duration:
                group_name = "test"
                # await client.join_group(group_name)
                await asyncio.gather(
                    *[client.send_to_group(group_name, message, WebPubSubDataType.TEXT) for _ in range(messages_num)]
                )
                logger.info(f"Succeed to send {messages_num} messages")


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument(
        "--log-file-name",
        help="output log file name. Default value is '' which means doesn't output",
        type=str,
        default="",
    )
    parser.add_argument("--log-interval", help="interval to log. Default value is 5s", type=int, default=5)
    parser.add_argument(
        "--duration", help="how long the test continue. Default value is 24 hours", type=int, default=24 * 3600
    )
    parser.add_argument(
        "--messages-num", help="Messages number to send every time. Default value is 1000", type=int, default=1000
    )

    args, _ = parser.parse_known_args()
    asyncio.run(
        main(
            log_file_name=args.log_file_name,
            log_interval=args.log_interval,
            duration=args.duration,
            messages_num=args.messages_num,
        )
    )
