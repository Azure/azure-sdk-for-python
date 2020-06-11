# Copyright 2017, OpenCensus Authors
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from opencensus.common import utils


class Type(object):
    """
    Indicates whether the message was sent or received.

    Attributes:
      TYPE_UNSPECIFIED (int): Unknown event type.
      SENT (int): Indicates a sent message.
      RECEIVED (int): Indicates a received message.
    """
    TYPE_UNSPECIFIED = 0
    SENT = 1
    RECEIVED = 2


class Annotation(object):
    """Text annotation with a set of attributes.

    :type timestamp: :class:`~datetime.datetime`
    :param timestamp: The timestamp indicating the time the event occurred.

    :type description: str
    :param description: A user-supplied message describing the event.
                        The maximum length for the description is 256 bytes.

    :type attributes: :class:`~opencensus.trace.attributes.Attributes`
    :param attributes: A set of attributes on the annotation.
                       You can have up to 4 attributes per Annotation.
    """
    def __init__(self, timestamp, description, attributes=None):
        self.timestamp = utils.to_iso_str(timestamp)
        self.description = description
        self.attributes = attributes

    def format_annotation_json(self):
        annotation_json = {}
        annotation_json['description'] = utils.get_truncatable_str(
            self.description)

        if self.attributes is not None:
            annotation_json['attributes'] = self.attributes.\
                format_attributes_json()

        return annotation_json


class MessageEvent(object):
    """An event describing a message sent/received between Spans.

    :type timestamp: :class:`~datetime.datetime`
    :param timestamp: The timestamp indicating the time the event occurred.

    :type type: Enum of :class: `~opencensus.trace.time_event.Type`
    :param type: Indicates whether the message was sent or received.

    :type id: str (int64 format)
    :param id: An identifier for the MessageEvent's message that can be used
               to match SENT and RECEIVED MessageEvents. It is recommended to
               be unique within a Span.

    :type uncompressed_size_bytes: str (int64 format)
    :param uncompressed_size_bytes: The number of uncompressed bytes sent or
                                    received.

    :type compressed_size_bytes: str (int64 format)
    :param compressed_size_bytes: The number of compressed bytes sent or
                                  received. If missing assumed to be the same
                                  size as uncompressed.

    """
    def __init__(self, timestamp, id, type=None, uncompressed_size_bytes=None,
                 compressed_size_bytes=None):
        self.timestamp = utils.to_iso_str(timestamp)

        if type is None:
            type = Type.TYPE_UNSPECIFIED

        if compressed_size_bytes is None and \
                uncompressed_size_bytes is not None:
            compressed_size_bytes = uncompressed_size_bytes

        self.id = id
        self.type = type
        self.uncompressed_size_bytes = uncompressed_size_bytes
        self.compressed_size_bytes = compressed_size_bytes

    def format_message_event_json(self):
        message_event_json = {}

        message_event_json['id'] = self.id
        message_event_json['type'] = self.type

        if self.uncompressed_size_bytes is not None:
            message_event_json[
                'uncompressed_size_bytes'] = self.uncompressed_size_bytes

        if self.compressed_size_bytes is not None:
            message_event_json[
                'compressed_size_bytes'] = self.compressed_size_bytes

        return message_event_json
