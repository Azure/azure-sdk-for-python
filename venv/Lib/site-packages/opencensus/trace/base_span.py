# Copyright 2018, OpenCensus Authors
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

"""Module containing base class for Span."""


class BaseSpan(object):
    """Base class for Opencensus spans.
    Subclasses of :class:`BaseSpan` must implement the below methods.
    """

    @staticmethod
    def on_create(callback):
        raise NotImplementedError

    @property
    def children(self):
        """The child spans of the current span."""
        raise NotImplementedError

    def span(self, name='child_span'):
        """Create a child span for the current span and append it to the child
        spans list.

        :type name: str
        :param name: (Optional) The name of the child span.

        :rtype: :class: `~opencensus.trace.span.Span`
        :returns: A child Span to be added to the current span.
        """
        raise NotImplementedError

    def add_attribute(self, attribute_key, attribute_value):
        """Add attribute to span.

        :type attribute_key: str
        :param attribute_key: Attribute key.

        :type attribute_value:str
        :param attribute_value: Attribute value.
        """
        raise NotImplementedError

    def add_annotation(self, description, **attrs):
        """Add an annotation to span.

        :type description: str
        :param description: A user-supplied message describing the event.
                        The maximum length for the description is 256 bytes.

        :type attrs: kwargs
        :param attrs: keyworded arguments e.g. failed=True, name='Caching'
        """
        raise NotImplementedError

    def add_message_event(self, message_event):
        """Add a message event to this span.

        :type message_event: :class:`opencensus.trace.time_event.MessageEvent`
        :param message_event: The message event to attach to this span.
        """
        raise NotImplementedError

    def add_link(self, link):
        """Add a Link.

        :type link: :class: `~opencensus.trace.link.Link`
        :param link: A Link object.
        """
        raise NotImplementedError

    def set_status(self, status):
        """Sets span status.

        :type code: :class: `~opencensus.trace.status.Status`
        :param code: A Status object.
        """
        raise NotImplementedError

    def start(self):
        """Set the start time for a span."""
        raise NotImplementedError

    def finish(self):
        """Set the end time for a span."""
        raise NotImplementedError

    def __iter__(self):
        """Iterate through the span tree."""
        raise NotImplementedError

    def __enter__(self):
        """Start a span."""
        raise NotImplementedError

    def __exit__(self, exception_type, exception_value, traceback):
        """Finish a span."""
        raise NotImplementedError
