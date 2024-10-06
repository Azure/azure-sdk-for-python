# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

from typing import Optional
import os
from concurrent.futures import Future, Executor, ThreadPoolExecutor

from blinker import Namespace

from azure.identity import DefaultAzureCredential
from azure.servicebus import ServiceBusClient


cloudmachine_events = Namespace()
FILE_UPLOADED = cloudmachine_events.signal('file-uploaded')


class Process(Future):

    def __init__(self, future: Future) -> None:
        self._future = future


class Processer(Executor):

    def __init__(self, *, max_workers: int = 10) -> None:
        self._executor = ThreadPoolExecutor

    def submit(self, fn, /, *args, **kwargs) -> Process:
        future = self._executor.submit(fn, *args, **kwargs)
        return Process(future)

    def map(self, fn, *iterables, timeout: Optional[int] = None, chunksize: int = 1):
        self._executor.map(fn, *iterables, timeout=timeout, chunksize=chunksize)


class EventListener:
    _listener_topic: str = "cm_internal_topic"
    _listen_subscription: str = "cm_internal_subscription"

    def __init__(self) -> None:
        endpoint = os.environ['AZURE_SERVICE_BUS_ENDPOINT']
        credential = DefaultAzureCredential()
        self._client = ServiceBusClient(
            fully_qualified_namespace=endpoint,
            credential=credential,
        )
        self._listener = self._client.get_subscription_receiver(
            topic_name=self._listener_topic,
            subscription_name=self._listen_subscription,
        )

    def __call__(self):
        try:
            with self._listener as receiver:
                for msg in receiver:
                    print(str(msg))
                    FILE_UPLOADED.send(msg)
        except Exception as exp:
            print(exp)

    def close(self):
        self._client.close()