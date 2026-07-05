# coding: utf-8
# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
from typing import List
import functools
import time
import threading
from devtools_testutils import AzureRecordedTestCase, PowerShellPreparer
from azure.messaging.webpubsubclient import WebPubSubClient, WebPubSubClientCredential
from azure.messaging.webpubsubclient.models import OnGroupDataMessageArgs, SendMessageError
from azure.messaging.webpubsubservice import WebPubSubServiceClient


class WebpubsubClientTest(AzureRecordedTestCase):
    def create_client(
        self,
        endpoint,
        hub: str = "Hub",
        roles: List[str] = ["webpubsub.joinLeaveGroup", "webpubsub.sendToGroup"],
        **kwargs,
    ):
        credential = self.get_credential(WebPubSubServiceClient)
        service_client = self.create_client_from_credential(
            WebPubSubServiceClient,
            credential=credential,
            endpoint=endpoint,
            hub=hub,
        )
        return WebPubSubClient(
            credential=WebPubSubClientCredential(lambda: service_client.get_client_access_token(roles=roles)["url"]),
            **kwargs,
        )

    @staticmethod
    def setup_events(client):
        """Subscribe connected/disconnected/group-message events and return their wait handles."""
        connected_event = threading.Event()
        disconnected_event = threading.Event()
        message_event = threading.Event()

        def _on_connected(*args, **kwargs):
            connected_event.set()

        def _on_disconnected(*args, **kwargs):
            disconnected_event.set()

        def _on_group_message(msg):
            on_group_message(msg)
            message_event.set()

        client.subscribe("connected", _on_connected)
        client.subscribe("disconnected", _on_disconnected)
        client.subscribe("group-message", _on_group_message)
        return connected_event, disconnected_event, message_event

    @staticmethod
    def retry_send_until_message(client, group_name, data, message_event, retries=30):
        """Retry send_to_group until message_event fires, handling SendMessageError from rejoin lag."""
        for _ in range(retries):
            try:
                client.send_to_group(group_name, data, "text")
            except SendMessageError:
                time.sleep(1)
                continue
            if message_event.wait(timeout=2):
                return
        message_event.wait(timeout=2)


WebpubsubClientPowerShellPreparer = functools.partial(
    PowerShellPreparer,
    "webpubsubclient",
    webpubsubclient_endpoint="https://myservice.webpubsub.azure.com",
)

TEST_RESULT = set()


def on_group_message(msg: OnGroupDataMessageArgs):
    TEST_RESULT.add(msg.data)


class SafeThread(threading.Thread):
    def __init__(self, *args, **kwargs):
        super(SafeThread, self).__init__(*args, **kwargs)
        self.exception = None

    def run(self) -> None:
        try:
            super(SafeThread, self).run()
        except Exception as ex:
            self.exception = ex

    def join(self, *args, **kwargs) -> None:
        super(SafeThread, self).join(*args, **kwargs)
        if self.exception:
            raise self.exception
