# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

import json
import time
from typing import TYPE_CHECKING, Union
from queue import Empty
from threading import Event
from urllib.parse import urlparse

from azure.core.pipeline.transport import HttpTransport

from ._storage import StorageFile, DeletedFile
from ..events import cloudmachine_events
if TYPE_CHECKING:
    from .._client import CloudMachineClient


class EventListener:
    _listener_topic: str = "cm_internal_topic"
    _listen_subscription: str = "cm_internal_subscription"

    def __init__(
            self,
            cloudmachine: 'CloudMachineClient',
            *,
            retry_events: Union[bool, int] = False
    ) -> None:
        self._cm = cloudmachine
        if retry_events and not isinstance(retry_events, int):
            self._retry_events = 5
        self._retry_events: int = retry_events or 0
        self.shutdown = Event()

    def __call__(self):
        while not self.shutdown.is_set():
            event_msg = None
            try:
                event_msg = self._cm.messaging.get(
                    topic=self._listener_topic,
                    subscription=self._listen_subscription,
                    timeout=10
                )
                event = json.loads(event_msg.content)
                event_type = event['eventType']
                if event_type == 'Microsoft.Storage.BlobCreated':
                    uploaded = event['data']
                    url: str = uploaded['blobUrl']
                    parsed_url = urlparse(url)
                    _, container, blobname = parsed_url.path.split('/', 2)
                    storage_file = StorageFile(
                        content=None,
                        filename=blobname,
                        container=container,
                        content_length=uploaded['contentLength'],
                        etag=uploaded['eTag'],
                        endpoint=url,
                        content_type=uploaded['contentType'],
                        responsedata=event
                    )
                    cloudmachine_events[event_type].send(self._cm, event=storage_file)
                    self._cm.messaging.task_done(
                        event_msg,
                        topic=self._listener_topic,
                        subscription=self._listen_subscription
                    )
                elif event_type == 'Microsoft.Storage.BlobDeleted':
                    uploaded = event['data']
                    url = uploaded['blobUrl']
                    parsed_url = urlparse(url)
                    _, container, blobname = parsed_url.path.split('/', 2)
                    deleted_file = DeletedFile(
                        filename=blobname,
                        container=container,
                        endpoint=url,
                        responsedata=event
                    )
                    cloudmachine_events[event_type].send(self._cm, event=deleted_file)
                    self._cm.messaging.task_done(
                        event_msg,
                        topic=self._listener_topic,
                        subscription=self._listen_subscription
                    )
                elif event_type in cloudmachine_events:
                    cloudmachine_events[event_type].send(self._cm, event=event['data'])
                    self._cm.messaging.task_done(
                        event_msg,
                        topic=self._listener_topic,
                        subscription=self._listen_subscription
                    )
                else:
                    self._cm.messaging.task_done(
                        event_msg,
                        topic=self._listener_topic,
                        subscription=self._listen_subscription,
                        delete=False
                    )
            except Empty:
                time.sleep(1)
            except Exception as exp:
                if event_msg:
                    if self._retry_events < event_msg.delivery_count:
                        self._cm.messaging.task_done(
                            event_msg,
                            topic=self._listener_topic,
                            subscription=self._listen_subscription
                        )
                    else:
                        self._cm.messaging.task_done(
                            event_msg,
                            topic=self._listener_topic,
                            subscription=self._listen_subscription,
                            delete=False
                        )
                # TODO: log error 
                # print(exp)

    def close(self):
        self.shutdown.set()
