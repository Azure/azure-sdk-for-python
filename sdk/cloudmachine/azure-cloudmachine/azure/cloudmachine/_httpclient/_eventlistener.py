# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

import json
import time
from typing import Optional, TYPE_CHECKING
from queue import Empty
from threading import Event

from blinker import Namespace

from azure.core.pipeline.transport import HttpTransport

from ._servicebus import CloudMachineServiceBus
from ..resources import resources
if TYPE_CHECKING:
    from .._client import CloudMachineClient

cloudmachine_events = Namespace()

cm_servicebus = resources.get('servicebus', cls=CloudMachineServiceBus)['CLOUDMACHINE']

class EventListener:
    _listener_topic: str = "cm_internal_topic"
    _listen_subscription: str = "cm_internal_subscription"

    def __init__(
            self,
            cloudmachine: 'CloudMachineClient',
            transport: Optional[HttpTransport] = None
    ) -> None:
        self._client = cm_servicebus.client(transport=transport)
        self._cm = cloudmachine
        self.shutdown = Event()

    def __call__(self):
        while not self.shutdown.is_set():
            try:
                event_msg = self._client.get(
                    topic=self._listener_topic,
                    subscription=self._listen_subscription,
                    timeout=10
                )
                event = json.loads(event_msg.content)
                cloudmachine_events[event['eventType']].send(self._cm, event=event['data'])
                self._client.task_done(
                    event_msg,
                    topic=self._listener_topic,
                    subscription=self._listen_subscription
                )
            except KeyError:
                self._client.task_done(
                    event_msg,
                    topic=self._listener_topic,
                    subscription=self._listen_subscription,
                    delete=False)
            except Empty:
                time.sleep(1)
            except Exception as exp:
                # TODO: log error
                print(exp)

    def close(self):
        self.shutdown.set()
        self._client.close()
