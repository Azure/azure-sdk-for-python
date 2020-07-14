# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
# pylint:disable=protected-access
import datetime
from copy import deepcopy
from typing import Optional
from dateutil.tz import tzutc
import datetime as dt

from msrest.serialization import Model

from azure.eventgrid._generated.models._models import EventGridEvent as InternalEventGridEvent, \
    CloudEvent as InternalCloudEvent


class CloudEvent(InternalCloudEvent):   #pylint:disable=too-many-instance-attributes
    """Properties of an event published to an Event Grid topic using the CloudEvent 1.0 Schema.

    All required parameters must be populated in order to send to Azure.

    :param id: Required. An identifier for the event. The combination of id and source must be
     unique for each distinct event.
    :type id: str
    :param source: Required. Identifies the context in which an event happened. The combination of
     id and source must be unique for each distinct event.
    :type source: str
    :param data: Event data specific to the event type.
    :type data: object
    :param type: Required. Type of event related to the originating occurrence.
    :type type: str
    :param time: The time (in UTC) the event was generated, in RFC3339 format.
    :type time: ~datetime.datetime
    :param specversion: Required. The version of the CloudEvents specification which the event
     uses.
    :type specversion: str
    :param dataschema: Identifies the schema that data adheres to.
    :type dataschema: str
    :param datacontenttype: Content type of data value.
    :type datacontenttype: str
    :param subject: This describes the subject of the event in the context of the event producer
     (identified by source).
    :type subject: str
    """

    def __init__(
        self,
        **kwargs
    ):
        self.id = kwargs['id']
        self.source = kwargs['source']
        self.data = kwargs.get('data', None)
        self.type = kwargs['type']
        self.time = kwargs.get('time', dt.datetime.now(tzutc()).isoformat())
        self.specversion = kwargs['specversion']
        self.dataschema = kwargs.get('dataschema', None)
        self.datacontenttype = kwargs.get('datacontenttype', None)
        self.subject = kwargs.get('subject', None)

    @classmethod
    def from_dict(cls, source):
        """
        Returns an array of CloudEvent objects given a dict of events following the CloudEvent schema.

        :param source: Required. The dict object following the CloudEvent schema.
        :type source: dict

        :rtype: List[~azure.eventgrid.CloudEvent]
        """
        events = []
        i = 1
        for event in source:
            try:
                events.append(CloudEvent(**event))
            except Exception as e:
                print("CloudEvent {} in file is incorrectly formatted with error: {}.".format(i, e))

        return events

class EventGridEvent(InternalEventGridEvent):
    """Properties of an event published to an Event Grid topic using the EventGrid Schema.

    Variables are only populated by the server, and will be ignored when sending a request.

    All required parameters must be populated in order to send to Azure.

    :param id: Required. An unique identifier for the event.
    :type id: str
    :param topic: The resource path of the event source.
    :type topic: str
    :param subject: Required. A resource path relative to the topic path.
    :type subject: str
    :param data: Required. Event data specific to the event type.
    :type data: object
    :param event_type: Required. The type of the event that occurred.
    :type event_type: str
    :param event_time: Required. The time (in UTC) the event was generated.
    :type event_time: ~datetime.datetime
    :ivar metadata_version: The schema version of the event metadata.
    :vartype metadata_version: str
    :param data_version: Required. The schema version of the data object.
    :type data_version: str
    """

    _validation = {
        'id': {'required': True},
        'subject': {'required': True},
        'data': {'required': True},
        'event_type': {'required': True},
        'event_time': {'required': True},
        'metadata_version': {'readonly': True},
        'data_version': {'required': True},
    }

    _attribute_map = {
        'id': {'key': 'id', 'type': 'str'},
        'topic': {'key': 'topic', 'type': 'str'},
        'subject': {'key': 'subject', 'type': 'str'},
        'data': {'key': 'data', 'type': 'object'},
        'event_type': {'key': 'eventType', 'type': 'str'},
        'event_time': {'key': 'eventTime', 'type': 'iso-8601'},
        'metadata_version': {'key': 'metadataVersion', 'type': 'str'},
        'data_version': {'key': 'dataVersion', 'type': 'str'},
    }

    def __init__(
        self,
        **kwargs
    ):
        self.id = kwargs['id']
        self.topic = kwargs.get('topic', None)
        self.subject = kwargs['subject']
        self.data = kwargs['data']
        self.event_type = kwargs['event_type']
        self.event_time = kwargs.get('event_time', dt.datetime.now(tzutc()).isoformat())
        self.metadata_version = None
        self.data_version = kwargs['data_version']

    @classmethod
    def from_dict(cls, source):
        """
        Returns an array of EventGridEvent objects given a dict of events following the EventGridEvent schema.

        :param source: Required. The dict object following the EventGridEvent schema.
        :type source: dict

        :rtype: List[~azure.eventgrid.EventGridEvent]
        """
        events = []
        i = 1
        for event in source:
            try:
                events.append(EventGridEvent(**event))
            except Exception as e:
                print("EventGridEvent {} in file is incorrectly formatted with error: {}.".format(i, e))

        return events
