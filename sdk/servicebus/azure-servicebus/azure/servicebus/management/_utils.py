# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
from datetime import datetime, timedelta
from typing import TYPE_CHECKING, cast, Union, Mapping, Type, Any, Optional
from xml.etree.ElementTree import ElementTree, SubElement, QName
import isodate
import six

from . import _constants as constants
from ._api_version import DEFAULT_VERSION
from ._handle_response_error import _handle_response_error

if TYPE_CHECKING:
    # pylint: disable=unused-import, ungrouped-imports
    from typing import TypeVar
    from ._models import (
        QueueProperties,
        TopicProperties,
        SubscriptionProperties,
        RuleProperties,
        InternalQueueDescription,
        InternalTopicDescription,
        InternalSubscriptionDescription,
        InternalRuleDescription,
    )

    PropertiesType = TypeVar(
        "PropertiesType",
        QueueProperties,
        TopicProperties,
        SubscriptionProperties,
        RuleProperties,
    )

# Refer to the async version of this module under ..\aio\management\_utils.py for detailed explanation.

try:
    import urllib.parse as urlparse
except ImportError:
    import urlparse  # type: ignore  # for python 2.7


def extract_rule_data_template(feed_class, convert, feed_element):
    """Special version of function extrat_data_template for Rule.

    Pass both the XML entry element and the rule instance to function `convert`. Rule needs to extract
    KeyValue from XML Element and set to Rule model instance manually. The autorest/msrest serialization/deserialization
    doesn't work for this special part.
    After autorest is enhanced, this method can be removed.
    Refer to autorest issue https://github.com/Azure/autorest/issues/3535
    """
    deserialized = feed_class.deserialize(feed_element)
    next_link = None
    if deserialized.link and len(deserialized.link) == 2:
        next_link = deserialized.link[1].href
    if deserialized.entry:
        list_of_entities = [
            convert(*x) if convert else x
            for x in zip(
                feed_element.findall(constants.ATOM_ENTRY_TAG), deserialized.entry
            )
        ]
    else:
        list_of_entities = []
    return next_link, iter(list_of_entities)


def extract_data_template(feed_class, convert, feed_element):
    deserialized = feed_class.deserialize(feed_element)
    list_of_entities = [convert(x) if convert else x for x in deserialized.entry]
    next_link = None
    if deserialized.link and len(deserialized.link) == 2:
        next_link = deserialized.link[1].href
    return next_link, iter(list_of_entities)


def get_next_template(list_func, *args, **kwargs):
    """Call list_func to get the XML data and deserialize it to XML ElementTree.

    azure.core.async_paging.AsyncItemPaged will call `extract_data_template` and use the returned
    XML ElementTree to call a partial function created from `extrat_data_template`.

    """
    start_index = kwargs.pop("start_index", 0)
    max_page_size = kwargs.pop("max_page_size", 100)
    api_version = kwargs.pop("api_version", DEFAULT_VERSION)
    if args[0]:
        queries = urlparse.parse_qs(urlparse.urlparse(args[0]).query)
        start_index = int(queries[constants.LIST_OP_SKIP][0])
        max_page_size = int(queries[constants.LIST_OP_TOP][0])
        api_version = queries[constants.API_VERSION_PARAM_NAME][0]
    with _handle_response_error():
        feed_element = cast(
            ElementTree,
            list_func(
                skip=start_index, top=max_page_size, api_version=api_version, **kwargs
            ),
        )
    return feed_element


def deserialize_value(value, value_type):
    if value_type in ("int", "long"):
        value = int(value)
    elif value_type == "boolean":
        value = value.lower() == "true"
    elif value_type == "double":
        value = float(value)
    elif value_type == "dateTime":
        value = isodate.parse_datetime(value)
    elif value_type == "duration":
        value = isodate.parse_duration(value)
        # Note: If value ever includes a month or year, will return an isodate type, and should be reassessed
    return value


def serialize_value_type(value):
    if isinstance(value, float):
        return "double", str(value)
    if isinstance(
        value, bool
    ):  # Attention: bool is subclass of int. So put bool ahead of int
        return "boolean", str(value).lower()
    if isinstance(value, six.string_types):
        return "string", value
    if isinstance(value, six.integer_types):
        return "int" if value <= constants.INT32_MAX_VALUE else "long", str(value)
    if isinstance(value, datetime):
        return "dateTime", isodate.datetime_isoformat(value)
    if isinstance(value, timedelta):
        return "duration", isodate.duration_isoformat(value)
    raise ValueError(
        "value {} of type {} is not supported for the key value".format(
            value, type(value)
        )
    )


def deserialize_key_values(xml_parent, key_values):
    """deserialize xml Element and replace the values in dict key_values with correct data types.

    The deserialized XML is like:

    <KeyValueOfstringanyType>
        <Key>key_string</Key>
        <Value xmlns:d6p1="http://www.w3.org/2001/XMLSchema" xsi:type="d6p1:string">str1</Value>
    </KeyValueOfstringanyType>
    <KeyValueOfstringanyType>
        <Key>key_int</Key>
        <Value xmlns:d6p1="http://www.w3.org/2001/XMLSchema" xsi:type="d6p1:int">2</Value>
    </KeyValueOfstringanyType>
    ...

    After autorest is enhanced, this method can be removed.
    Refer to autorest issue https://github.com/Azure/autorest/issues/3535

    :param xml_parent: The parent xml Element that contains some children of <KeyValueOfstringanyType>.
    :param key_values: The dict that contains the key values. The value could have wrong data types.
    :return: This method returns `None`. It will update each value of key_values to correct value type.
    """
    key_values_ele = xml_parent.findall(constants.RULE_KEY_VALUE_TAG)
    for key_value_ele in key_values_ele:
        key_ele = key_value_ele.find(constants.RULE_KEY_TAG)
        value_ele = key_value_ele.find(constants.RULE_VALUE_TAG)
        key = key_ele.text
        value = value_ele.text
        value_type = value_ele.attrib[constants.RULE_VALUE_TYPE_TAG]
        value_type = value_type.split(":")[1]
        value = deserialize_value(value, value_type)
        key_values[key] = value


def deserialize_rule_key_values(entry_ele, rule_description):
    """Deserialize a rule's filter and action that have key values from xml.

    CorrelationRuleFilter.properties, SqlRuleFilter.parameters and SqlRuleAction.parameters may contain
    data (dict is not empty).

    After autorest is enhanced, this method can be removed.
    Refer to autorest issue https://github.com/Azure/autorest/issues/3535
    """
    content = entry_ele.find(constants.ATOM_CONTENT_TAG)
    if content:
        correlation_filter_properties_ele = (
            content.find(constants.RULE_DESCRIPTION_TAG)
            .find(constants.RULE_FILTER_TAG)
            .find(constants.RULE_FILTER_COR_PROPERTIES_TAG)
        )
        if correlation_filter_properties_ele:
            deserialize_key_values(
                correlation_filter_properties_ele, rule_description.filter.properties
            )
        sql_filter_parameters_ele = (
            content.find(constants.RULE_DESCRIPTION_TAG)
            .find(constants.RULE_FILTER_TAG)
            .find(constants.RULE_PARAMETERS_TAG)
        )
        if sql_filter_parameters_ele:
            deserialize_key_values(
                sql_filter_parameters_ele, rule_description.filter.parameters
            )
        sql_action_parameters_ele = (
            content.find(constants.RULE_DESCRIPTION_TAG)
            .find(constants.RULE_ACTION_TAG)
            .find(constants.RULE_PARAMETERS_TAG)
        )
        if sql_action_parameters_ele:
            deserialize_key_values(
                sql_action_parameters_ele, rule_description.action.parameters
            )


def serialize_key_values(xml_parent, key_values):
    """serialize a dict to xml Element and put it under xml_parent

    The serialized XML is like:

    <KeyValueOfstringanyType>
        <Key>key_string</Key>
        <Value xmlns:d6p1="http://www.w3.org/2001/XMLSchema" xsi:type="d6p1:string">str1</Value>
    </KeyValueOfstringanyType>
    <KeyValueOfstringanyType>
        <Key>key_int</Key>
        <Value xmlns:d6p1="http://www.w3.org/2001/XMLSchema" xsi:type="d6p1:int">2</Value>
    </KeyValueOfstringanyType>
    ...

    :param xml_parent: The parent xml Element for the serialized xml.
    :param key_values: The dict that contains the key values.
    :return: `xml_parent` is mutated. The returned value is `None`.

    After autorest is enhanced, this method can be removed.
    Refer to autorest issue https://github.com/Azure/autorest/issues/3535
    """
    xml_parent.clear()
    if key_values:
        for key, value in key_values.items():
            value_type, value_in_str = serialize_value_type(value)
            key_value_ele = SubElement(
                xml_parent, QName(constants.SB_XML_NAMESPACE, constants.RULE_KEY_VALUE)
            )
            key_ele = SubElement(
                key_value_ele, QName(constants.SB_XML_NAMESPACE, constants.RULE_KEY)
            )
            key_ele.text = key
            type_qname = QName(constants.XML_SCHEMA_INSTANCE_NAMESPACE, "type")
            value_ele = SubElement(
                key_value_ele,
                QName(constants.SB_XML_NAMESPACE, constants.RULE_VALUE),
                {type_qname: constants.RULE_VALUE_TYPE_XML_PREFIX + ":" + value_type},
            )
            value_ele.text = value_in_str
            value_ele.attrib[
                "xmlns:" + constants.RULE_VALUE_TYPE_XML_PREFIX
            ] = constants.XML_SCHEMA_NAMESPACE


def serialize_rule_key_values(entry_ele, rule_descripiton):
    """Serialize a rule's filter and action that have key values into xml.

    CorrelationRuleFilter.properties, SqlRuleFilter.parameters and SqlRuleAction.parameters may contain
    data (dict is not empty). Serialize them to XML.

    After autorest is enhanced, this method can be removed.
    Refer to autorest issue https://github.com/Azure/autorest/issues/3535
    """
    content = entry_ele.find(constants.ATOM_CONTENT_TAG)
    if content:
        correlation_filter_parameters_ele = (
            content.find(constants.RULE_DESCRIPTION_TAG)
            .find(constants.RULE_FILTER_TAG)
            .find(constants.RULE_FILTER_COR_PROPERTIES_TAG)
        )
        if correlation_filter_parameters_ele:
            serialize_key_values(
                correlation_filter_parameters_ele, rule_descripiton.filter.properties
            )
        sql_filter_parameters_ele = (
            content.find(constants.RULE_DESCRIPTION_TAG)
            .find(constants.RULE_FILTER_TAG)
            .find(constants.RULE_PARAMETERS_TAG)
        )
        if sql_filter_parameters_ele:
            serialize_key_values(
                sql_filter_parameters_ele, rule_descripiton.filter.parameters
            )
        sql_action_parameters_ele = (
            content.find(constants.RULE_DESCRIPTION_TAG)
            .find(constants.RULE_ACTION_TAG)
            .find(constants.RULE_PARAMETERS_TAG)
        )
        if sql_action_parameters_ele:
            serialize_key_values(
                sql_action_parameters_ele, rule_descripiton.action.parameters
            )


# Helper functions for common parameter validation errors in the client.
def _validate_entity_name_type(entity_name, display_name="entity name"):
    # type: (str, str) -> None
    if not isinstance(entity_name, str):
        raise TypeError(
            "{} must be a string, not {}".format(display_name, type(entity_name))
        )


def _validate_topic_and_subscription_types(topic_name, subscription_name):
    # type: (str, str) -> None
    if not isinstance(topic_name, str) or not isinstance(subscription_name, str):
        raise TypeError(
            "topic name and subscription name must be strings, not {} and {}".format(
                type(topic_name), type(subscription_name)
            )
        )


def _validate_topic_subscription_and_rule_types(
    topic_name, subscription_name, rule_name
):
    # type: (str, str, str) -> None
    if (
        not isinstance(topic_name, str)
        or not isinstance(subscription_name, str)
        or not isinstance(rule_name, str)
    ):
        raise TypeError(
            "topic name, subscription name and rule name must be strings, not {} {} and {}".format(
                type(topic_name), type(subscription_name), type(rule_name)
            )
        )


def _normalize_entity_path_to_full_path_if_needed(
    entity_path, fully_qualified_namespace
):
    # type: (Optional[str], str) -> Optional[str]
    if not entity_path:
        return entity_path
    parsed = urlparse.urlparse(entity_path)
    entity_path = (
        ("sb://" + fully_qualified_namespace + "/" + entity_path)
        if not parsed.netloc
        else entity_path
    )
    return entity_path


def create_properties_from_dict_if_needed(properties, sb_resource_type):
    # type: (Union[PropertiesType, Mapping[str, Any]], Type[PropertiesType]) -> PropertiesType
    """
    This method is used to create a properties object given the
    resource properties type and its corresponding dict representation.
    :param properties: A properties object or its dict representation.
    :type properties: Mapping or PropertiesType
    :param type sb_resource_type: The type of properties object.
    :rtype: PropertiesType
    """
    if isinstance(properties, sb_resource_type):
        return properties
    try:
        return sb_resource_type(**cast(Mapping[str, Any], properties))
    except TypeError as e:
        if "required keyword arguments" in str(e):
            raise e
        raise TypeError(
            "Update input must be an instance of {}, or a mapping representing one.".format(
                sb_resource_type.__name__
            )
        )
