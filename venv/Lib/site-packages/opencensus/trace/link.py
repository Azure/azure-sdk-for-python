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


class Type(object):
    """The relationship of the current span relative to the linked span: child,
    parent, or unspecified.

    Attributes:
      TYPE_UNSPECIFIED (int): The relationship of the two spans is unknown.
      CHILD_LINKED_SPAN (int): The linked span is a child of the current span.
      PARENT_LINKED_SPAN (int): The linked span is a parent of the current
      span.
    """
    TYPE_UNSPECIFIED = 0
    CHILD_LINKED_SPAN = 1
    PARENT_LINKED_SPAN = 2


class Link(object):
    """A pointer from the current span to another span in the same trace or in
    a different trace. For example, this can be used in batching operations,
    where a single batch handler processes multiple requests from different
    traces or when the handler receives a request from a different project.

    :type trace_id: str
    :param trace_id: The [TRACE_ID] for a trace within a project.

    :type span_id: str
    :param span_id: The [SPAN_ID] for a span within a trace.

    :type type: Enum of :class:`~opencensus.trace.link.Type`
    :param type: The relationship of the current span relative to the linked
                 span.

    :type attributes: :class:`~opencensus.trace.attributes.Attributes`
    :param attributes: A set of attributes on the link. You have have up to 32
                       attributes per link.
    """
    def __init__(self, trace_id, span_id, type=None, attributes=None):
        self.trace_id = trace_id
        self.span_id = span_id

        if type is None:
            type = Type.TYPE_UNSPECIFIED

        self.type = type
        self.attributes = attributes

    def format_link_json(self):
        """Convert a Link object to json format."""
        link_json = {}
        link_json['trace_id'] = self.trace_id
        link_json['span_id'] = self.span_id
        link_json['type'] = self.type

        if self.attributes is not None:
            link_json['attributes'] = self.attributes

        return link_json
