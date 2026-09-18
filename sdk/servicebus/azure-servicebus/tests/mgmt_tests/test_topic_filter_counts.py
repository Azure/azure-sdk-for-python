# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
"""Unit tests for the topic runtime filter-count properties (no live infrastructure required)."""

from xml.etree import ElementTree

from azure.servicebus.management._generated.models import (
    TopicDescription as InternalTopicDescription,
    TopicDescriptionEntry,
)
from azure.servicebus.management._models import TopicRuntimeProperties

_CONNECT_NS = "http://schemas.microsoft.com/netservices/2010/10/servicebus/connect"


def _topic_entry_xml(*, subscription_count, sql_filter_count=None, correlation_filter_count=None):
    """Build a minimal ATOM topic entry, mirroring the shape the service returns from a GET."""
    filter_elements = ""
    if sql_filter_count is not None:
        filter_elements += "<SqlFilterCount>{}</SqlFilterCount>".format(sql_filter_count)
    if correlation_filter_count is not None:
        filter_elements += "<CorrelationFilterCount>{}</CorrelationFilterCount>".format(correlation_filter_count)
    return (
        '<entry xmlns="http://www.w3.org/2005/Atom">'
        '<content type="application/xml">'
        '<TopicDescription xmlns="{ns}">'
        "<SubscriptionCount>{sub}</SubscriptionCount>"
        "{filters}"
        "</TopicDescription>"
        "</content>"
        "</entry>"
    ).format(ns=_CONNECT_NS, sub=subscription_count, filters=filter_elements)


def test_topic_runtime_properties_expose_filter_counts():
    internal = InternalTopicDescription(subscription_count=2, sql_filter_count=7, correlation_filter_count=9)
    runtime = TopicRuntimeProperties._from_internal_entity("my-topic", internal)

    assert runtime.subscription_count == 2
    assert runtime.sql_filter_count == 7
    assert runtime.correlation_filter_count == 9


def test_topic_runtime_properties_filter_counts_default_none_when_absent():
    # A service region that has not yet deployed the topic filter-count feature omits the
    # elements; the counts must default to None, just like subscription_count.
    internal = InternalTopicDescription(subscription_count=1)
    runtime = TopicRuntimeProperties._from_internal_entity("my-topic", internal)

    assert runtime.subscription_count == 1
    assert runtime.sql_filter_count is None
    assert runtime.correlation_filter_count is None


def test_topic_filter_counts_deserialize_from_atom_xml():
    # Deserialize a real ATOM topic entry through the admin client's deserialization path so the
    # generated <SqlFilterCount>/<CorrelationFilterCount> element-to-attribute mapping is guarded in
    # CI (a wrong xml.name in the hand-edited generated attribute_map would surface only in a live
    # test otherwise).
    xml = _topic_entry_xml(subscription_count=2, sql_filter_count=3, correlation_filter_count=1)
    entry = TopicDescriptionEntry.deserialize(ElementTree.fromstring(xml))
    runtime = TopicRuntimeProperties._from_internal_entity("my-topic", entry.content.topic_description)

    assert runtime.subscription_count == 2
    assert runtime.sql_filter_count == 3
    assert runtime.correlation_filter_count == 1


def test_topic_filter_counts_deserialize_absent_from_atom_xml():
    # An entry from an older api-version omits the filter-count elements entirely; the deserialized
    # counts must be None, distinguishing "not returned" from a real zero.
    xml = _topic_entry_xml(subscription_count=2)
    entry = TopicDescriptionEntry.deserialize(ElementTree.fromstring(xml))
    runtime = TopicRuntimeProperties._from_internal_entity("my-topic", entry.content.topic_description)

    assert runtime.subscription_count == 2
    assert runtime.sql_filter_count is None
    assert runtime.correlation_filter_count is None
