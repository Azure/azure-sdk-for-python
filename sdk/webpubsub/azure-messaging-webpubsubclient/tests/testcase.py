# coding: utf-8
# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
from typing import List
import functools
import threading
from devtools_testutils import AzureRecordedTestCase, PowerShellPreparer
from azure.messaging.webpubsubclient import WebPubSubClient, WebPubSubClientCredential
from azure.messaging.webpubsubclient.models import OnGroupDataMessageArgs
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
