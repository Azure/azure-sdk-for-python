# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
from datetime import datetime, timedelta
from typing import cast, Union
from xml.etree.ElementTree import ElementTree, SubElement, Element, QName
import isodate

# Refer to the async version of this module under ..\aio\management\_utils.py for detailed explanation.

try:
    import urllib.parse as urlparse
except ImportError:
    import urlparse  # type: ignore  # for python 2.7

from azure.servicebus.management import _constants as constants
from ._handle_response_error import _handle_response_error


def extract_rule_data_template(feed_class, convert, feed_element):
    deserialized = feed_class.deserialize(feed_element)

    list_of_entities = [convert(*x) if convert else x for x in zip(feed_element.findall(constants.ENTRY_TAG), deserialized.entry)]
    next_link = None
    if deserialized.link and len(deserialized.link) == 2:
        next_link = deserialized.link[1].href
    return next_link, iter(list_of_entities)


def extract_data_template(feed_class, convert, feed_element):
    deserialized = feed_class.deserialize(feed_element)
    list_of_entities = [convert(x) if convert else x for x in deserialized.entry]
    next_link = None
    if deserialized.link and len(deserialized.link) == 2:
        next_link = deserialized.link[1].href
    return next_link, iter(list_of_entities)


def get_next_template(list_func, *args, **kwargs):
    start_index = kwargs.pop("start_index", 0)
    max_page_size = kwargs.pop("max_page_size", 100)
    api_version = constants.API_VERSION
    if args[0]:
        queries = urlparse.parse_qs(urlparse.urlparse(args[0]).query)
        start_index = int(queries[constants.LIST_OP_SKIP][0])
        max_page_size = int(queries[constants.LIST_OP_TOP][0])
        api_version = queries[constants.API_VERSION_PARAM_NAME][0]
    with _handle_response_error():
        feed_element = cast(
            ElementTree,
            list_func(
                skip=start_index, top=max_page_size,
                api_version=api_version,
                **kwargs
            )
        )
    return feed_element


def deserialize_value(value, value_type):
    if value_type in ("int", "long"):
        value = int(value)
    elif value_type == "boolean":
        value = True if value.lower() == "true" else False
    elif value_type == "double":
        value = float(value)
    elif value_type == "datetime":
        value = isodate.parse_datetime(value)
    elif value == "duration":
        value = isodate.parse_duration(value)
    return value


def serialize_value_type(value):
    value_type = type(value)
    if value_type == str:
        return "string", value
    if value_type == int:
        return "int" if value <= constants.INT_MAX_VALUE_CSHARP else "long", str(value)
    if value_type == float:
        return "double", str(value)
    if value_type == datetime:
        return "datetime", isodate.datetime_isoformat(value)
    if value_type == timedelta:
        return "duration", isodate.duration_isoformat(value)
    raise ValueError("value {} of type {} is wrong for the key value".format(value, value_type))


def deserialize_key_values(root, parameters):
    key_values_ele = root.findall("{http://schemas.microsoft.com/netservices/2010/10/servicebus/connect}KeyValueOfstringanyType")
    for key_value_ele in key_values_ele:
        key_ele = key_value_ele.find("{http://schemas.microsoft.com/netservices/2010/10/servicebus/connect}Key")
        value_ele = key_value_ele.find("{http://schemas.microsoft.com/netservices/2010/10/servicebus/connect}Value")
        key = key_ele.text
        value = value_ele.text
        value_type = value_ele.attrib["{http://www.w3.org/2001/XMLSchema-instance}type"]
        value_type = value_type.split(":")[1]
        value = deserialize_value(value, value_type)
        parameters[key] = value


def deserialize_rule_key_values(entry_ele, rule_description):
    content = entry_ele.find(constants.CONTENT_TAG)
    if content:
        correlation_filter_properties_ele = content.find(
            "{http://schemas.microsoft.com/netservices/2010/10/servicebus/connect}RuleDescription") \
            .find("{http://schemas.microsoft.com/netservices/2010/10/servicebus/connect}Filter") \
            .find("{http://schemas.microsoft.com/netservices/2010/10/servicebus/connect}Properties")
        if correlation_filter_properties_ele:
            deserialize_key_values(correlation_filter_properties_ele, rule_description.filter.properties)
        sql_filter_parameters_ele = content.find(
            "{http://schemas.microsoft.com/netservices/2010/10/servicebus/connect}RuleDescription") \
            .find("{http://schemas.microsoft.com/netservices/2010/10/servicebus/connect}Filter") \
            .find("{http://schemas.microsoft.com/netservices/2010/10/servicebus/connect}Parameters")
        if sql_filter_parameters_ele:
            deserialize_key_values(sql_filter_parameters_ele, rule_description.filter.parameters)
        sql_action_parameters_ele = content.find(
            "{http://schemas.microsoft.com/netservices/2010/10/servicebus/connect}RuleDescription") \
            .find("{http://schemas.microsoft.com/netservices/2010/10/servicebus/connect}Action") \
            .find("{http://schemas.microsoft.com/netservices/2010/10/servicebus/connect}Parameters")
        if sql_action_parameters_ele:
            deserialize_key_values(sql_action_parameters_ele, rule_description.action.parameters)


def serialize_key_values(root, kvs):
    root.clear()
    if kvs:
        for key, value in kvs.items():
            value_type, value_in_str = serialize_value_type(value)
            key_value_ele = SubElement(root, QName("http://schemas.microsoft.com/netservices/2010/10/servicebus/connect", "KeyValueOfstringanyType"))
            key_ele = SubElement(key_value_ele, QName("http://schemas.microsoft.com/netservices/2010/10/servicebus/connect", "Key"))
            key_ele.text = key
            type_qname = QName("http://www.w3.org/2001/XMLSchema-instance", "type")
            value_ele = SubElement(key_value_ele, QName("http://schemas.microsoft.com/netservices/2010/10/servicebus/connect", "Value"), {type_qname: "d6p1:" + value_type})
            value_ele.text = value_in_str
            value_ele.attrib["xmlns:d6p1"] = "http://www.w3.org/2001/XMLSchema"


def serialize_rule_key_values(entry_ele, rule_descrpiton):
    content = entry_ele.find(constants.CONTENT_TAG)
    if content:
        correlation_filter_parameters_ele = content.find(
            "{http://schemas.microsoft.com/netservices/2010/10/servicebus/connect}RuleDescription") \
            .find("{http://schemas.microsoft.com/netservices/2010/10/servicebus/connect}Filter") \
            .find("{http://schemas.microsoft.com/netservices/2010/10/servicebus/connect}Properties")
        if correlation_filter_parameters_ele:
            serialize_key_values(correlation_filter_parameters_ele, rule_descrpiton.filter.properties)
        sql_filter_parameters_ele = content.find(
            "{http://schemas.microsoft.com/netservices/2010/10/servicebus/connect}RuleDescription") \
            .find("{http://schemas.microsoft.com/netservices/2010/10/servicebus/connect}Filter") \
            .find("{http://schemas.microsoft.com/netservices/2010/10/servicebus/connect}Parameters")
        if sql_filter_parameters_ele:
            serialize_key_values(sql_filter_parameters_ele, rule_descrpiton.filter.parameters)
        sql_action_parameters_ele = content.find(
            "{http://schemas.microsoft.com/netservices/2010/10/servicebus/connect}RuleDescription") \
            .find("{http://schemas.microsoft.com/netservices/2010/10/servicebus/connect}Action") \
            .find("{http://schemas.microsoft.com/netservices/2010/10/servicebus/connect}Parameters")
        if sql_action_parameters_ele:
            serialize_key_values(sql_action_parameters_ele, rule_descrpiton.action.parameters)
