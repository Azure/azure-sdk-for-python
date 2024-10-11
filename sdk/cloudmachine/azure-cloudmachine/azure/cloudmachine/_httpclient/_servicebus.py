# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

import json
import os
import time
from urllib.parse import quote
from datetime import datetime, timezone, timedelta
from dataclasses import dataclass, field
from queue import Empty
from threading import Thread, Event
from functools import partial
import email
from concurrent.futures import Executor
import xml.etree.ElementTree as ET
from typing import IO, Any, Dict, Generator, List, Literal, Mapping, Optional, Protocol, Type, Union, overload

from azure.core.rest import HttpRequest, HttpResponse
from azure.core.tracing.decorator import distributed_trace
from azure.core.utils import case_insensitive_dict
from azure.core.exceptions import HttpResponseError

from ._base import CloudMachineClientlet
from ._utils import deserialize_rfc


@dataclass
class Message:
    id: str
    delivery_count: int
    sequence_number: int
    enqueued_sequence_number: int
    enqueued_time_utc: datetime
    state: str
    time_to_live: int
    content: bytes

    def __repr__(self):
        return repr(self.content)

@dataclass
class LockedMessage(Message):
    lock_token: str
    locked_until_utc: datetime
    _renew_interval: int
    _renew_lock: Optional[Thread] = None
    _stop_renew: Event = field(default_factory=Event)


class CloudMachineServiceBus(CloudMachineClientlet):
    _id: Literal["ServiceBus"] = "ServiceBus"
    default_topic_name: str = "cm_default_topic"
    default_subscription_name: str = "cm_default_subscription"

    def _load_response(self, response: HttpResponse) -> ET:
        return ET.fromstring(response.read().decode('utf-8'))

    def _renew_lock(self, message: LockedMessage, queue, topic, subscription, **kwargs) -> None:
        while not message._stop_renew.is_set():
            time.sleep(message._renew_interval)
            if message._stop_renew.is_set():
                return
            request = build_message_process_request(
                "POST",
                queue,
                topic or self.default_topic_name,
                subscription or self.default_subscription_name,
                message.id,
                message.lock_token
            )
            try:
                self._send_request(request, **kwargs)
            except HttpResponseError as e:
                # log renewal exception
                print("Lock renew failed", e)
                return

    def get_client(self, **kwargs) -> 'azure.servicebus.ServiceBusClient':
        try:
            from azure.servicebus import ServiceBusClient
        except ImportError as e:
            raise ImportError("Please install azure-servicebus SDK to use SDK client.") from e
        return ServiceBusClient(
            fully_qualified_namespace=self._endpoint,
            credential=self._credential,
            **kwargs
        )

    def full(self, **kwargs) -> Literal[False]:
        return False
    
    def empty(self, **kwargs) -> bool:
        return not self.qsize(**kwargs) > 0

    def join(self, **kwargs) -> None:
        while self.qsize(**kwargs) > 0:
            time.sleep(0.1)

    @overload
    def qsize(
            self,
            *,
            queue: str,
            **kwargs
    ) -> int:
        ...
    @overload
    def qsize(
            self,
            *,
            topic: str = "cm_default_topic",
            subscription: str = "cm_default_subscription",
            **kwargs
    ) -> int:
        ...
    @distributed_trace
    def qsize(
            self,
            *,
            queue: Optional[str] = None,
            topic: Optional[str] = None,
            subscription: Optional[str] = None,
            **kwargs
    ) -> int:
        request = build_get_request(
            queue,
            topic or self.default_topic_name,
            subscription or self.default_subscription_name
        )
        response = self._send_request(request, **kwargs)
        details = self._load_response(response)
        if queue:
            # TODO: This is probably wrong for a queue
            return int(details[5][0][12][0].text)
        return int(details[5][0][12][0].text)

    @overload
    def get(
            self,
            block: bool = True,
            timeout: Optional[int] = None,
            *,
            queue: str,
            lock: Literal[True] = True,
            renew_interval: int = 15,
            **kwargs
    ) -> LockedMessage:
        ...
    @overload
    def get(
            self,
            block: bool = True,
            timeout: Optional[int] = None,
            *,
            queue: str,
            lock: Literal[False],
            **kwargs
    ) -> Message:
        ...
    @overload
    def get(
            self,
            block: bool = True,
            timeout: Optional[int] = None,
            *,
            topic: str = "cm_default_topic",
            subscription: str = "cm_default_subscription",
            lock: Literal[True] = True,
            renew_interval: int = 15,
            **kwargs
    ) -> LockedMessage:
        ...
    @overload
    def get(
            self,
            block: bool = True,
            timeout: Optional[int] = None,
            *,
            topic: str = "cm_default_topic",
            subscription: str = "cm_default_subscription",
            lock: Literal[False],
            **kwargs
    ) -> Message:
        ...
    @distributed_trace
    def get(
            self,
            block: bool = True,
            timeout: Optional[int] = None,
            *,
            queue: Optional[str] = None,
            topic: Optional[str] = None,
            subscription: Optional[str] = None,
            lock: bool = True,
            renew_interval: int = 15,
            **kwargs
    ) -> Message:
        timeout = timeout if block else None
        request = build_receive_request(
            "POST" if lock else "DELETE",
            queue,
            topic or self.default_topic_name,
            subscription or self.default_subscription_name,
            timeout=timeout
        )
        response = self._send_request(request, **kwargs)
        if response.status_code == 204:
            raise Empty()

        content = response.read()
        properties = json.loads(response.headers['BrokerProperties'])
        if lock:
            message = LockedMessage(
                id=properties['MessageId'],
                delivery_count=properties['DeliveryCount'],
                enqueued_sequence_number=properties['EnqueuedSequenceNumber'],
                lock_token=properties['LockToken'],
                sequence_number=properties['SequenceNumber'],
                enqueued_time_utc=deserialize_rfc(properties['EnqueuedTimeUtc']),
                locked_until_utc=deserialize_rfc(properties['LockedUntilUtc']),
                state=properties["State"],
                time_to_live=properties["TimeToLive"],
                content=content,
                _renew_interval=renew_interval
            )
            message._renew_lock = Thread(
                target=partial(self._renew_lock, message, queue, topic, subscription),
                daemon=True
            )
            message._renew_lock.start()
            return message
        return Message(
                id=properties['MessageId'],
                delivery_count=properties['DeliveryCount'],
                enqueued_sequence_number=properties['EnqueuedSequenceNumber'],
                sequence_number=properties['SequenceNumber'],
                enqueued_time_utc=deserialize_rfc(properties['EnqueuedTimeUtc']),
                state=properties["State"],
                time_to_live=properties["TimeToLive"],
                content=content
            )

    @overload
    def get_nowait(
            self,
            *,
            queue: str = "default",
            lock: Literal[True] = True,
            **kwargs
    ) -> LockedMessage:
        ...
    @overload
    def get_nowait(
            self,
            *,
            queue: str = "default",
            lock: Literal[False],
            **kwargs
    ) -> Message:
        ...
    @overload
    def get_nowait(
            self,
            *,
            topic: str,
            subscription: str,
            lock: Literal[True] = True,
            **kwargs
    ) -> LockedMessage:
        ...
    @overload
    def get_nowait(
            self,
            *,
            topic: str,
            subscription: str,
            lock: Literal[False],
            **kwargs
    ) -> Message:
        ...
    @distributed_trace
    def get_nowait(
            self,
            *,
            queue: Optional[str] = None,
            topic: Optional[str] = None,
            subscription: Optional[str] = None,
            lock: bool = True,
            **kwargs
    ) -> Message:
        return self.get(False, queue=queue, topic=topic, subscription=subscription, lock=lock, **kwargs)

    @overload
    def task_done(
            self,
            message: LockedMessage,
            /, *,
            queue: str,
            delete: bool = True,
            **kwargs
    ) -> None:
        ...
    @overload
    def task_done(
            self,
            message: LockedMessage,
            /, *,
            topic: str = "cm_default_topic",
            subscription: str = "cm_default_subscription",
            delete: bool = True,
            **kwargs
    ) -> None:
        ...
    @distributed_trace
    def task_done(
            self,
            message: LockedMessage,
            /, *,
            queue: Optional[str] = None,
            topic: Optional[str] = None,
            subscription: Optional[str] = None,
            delete: bool = True,
            **kwargs
    ) -> None:
        request = build_message_process_request(
            "DELETE" if delete else "PUT",
            queue,
            topic or self.default_topic_name,
            subscription or self.default_subscription_name,
            message.id,
            message.lock_token
        )
        self._send_request(request, **kwargs)
        message._stop_renew.set()

########## Request Builders ##########

def build_receive_request(
    method: Literal["POST", "DELETE"],
    queue: Optional[str],
    topic: Optional[str],
    subscription: Optional[str],
    *,
    timeout: Optional[int] = None,
    **kwargs: Any
) -> HttpRequest:
    _headers = case_insensitive_dict(kwargs.pop("headers", {}) or {})
    _params = case_insensitive_dict(kwargs.pop("params", {}) or {})

    # Construct URL
    if queue:
        _url = "/{queue}/messages/head"
        path_format_arguments = {
            "queue": quote(queue),
        }
    else:
        _url = "{topic}/subscriptions/{subscription}/messages/head"
        path_format_arguments = {
            "topic": quote(topic),
            "subscription": quote(subscription),
        }
    _url: str = _url.format(**path_format_arguments)  # type: ignore
    # Construct parameters
    if timeout is not None:
        _params["timeout"] = timeout
    return HttpRequest(method=method, url=_url, params=_params, headers=_headers, **kwargs)


def build_message_process_request(
    method: Literal["PUT", "POST", "DELETE"],
    queue: Optional[str],
    topic: Optional[str],
    subscription: Optional[str],
    message_id: str,
    lock_token: str,
    **kwargs: Any
) -> HttpRequest:
    _headers = case_insensitive_dict(kwargs.pop("headers", {}) or {})
    _params = case_insensitive_dict(kwargs.pop("params", {}) or {})

    # Construct URL
    if queue:
        _url = "{queue}/messages/{message_id}/{lock_token}"
        path_format_arguments = {
            "queue": quote(queue),
            "message_id": quote(message_id),
            "lock_token": quote(lock_token)
        }
    else:
        _url = "{topic}/subscriptions/{subscription}/messages/{message_id}/{lock_token}"
        path_format_arguments = {
            "topic": quote(topic),
            "subscription": quote(subscription),
            "message_id": quote(message_id),
            "lock_token": quote(lock_token)
        }
    _url: str = _url.format(**path_format_arguments)  # type: ignore
    return HttpRequest(method=method, url=_url, params=_params, headers=_headers, **kwargs)


def build_get_request(
    queue: Optional[str],
    topic: Optional[str],
    subscription: Optional[str],
    *,
    enrich: bool = False,
    **kwargs: Any
) -> HttpRequest:
    _headers = case_insensitive_dict(kwargs.pop("headers", {}) or {})
    _params = case_insensitive_dict(kwargs.pop("params", {}) or {})

    api_version: str = kwargs.pop("api_version", _params.pop("api-version", "2021-05"))
    accept = _headers.pop("Accept", "application/xml, application/atom+xml")

    # Construct URL
    if queue:
        _url = "/{queue}"
        path_format_arguments = {
            "queue": quote(queue),
        }
    else:
        _url = "/{topic}/subscriptions/{subscription}"
        path_format_arguments = {
            "topic": quote(topic),
            "subscription": quote(subscription),
        }
    _url: str = _url.format(**path_format_arguments)  # type: ignore

    # Construct parameters
    if enrich is not None:
        _params["enrich"] = quote(json.dumps(enrich))
    _params["api-version"] = quote(api_version)

    # Construct headers
    _headers["Accept"] = accept

    return HttpRequest(method="GET", url=_url, params=_params, headers=_headers, **kwargs)