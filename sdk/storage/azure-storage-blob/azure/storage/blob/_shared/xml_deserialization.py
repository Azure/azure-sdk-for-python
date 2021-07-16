# --------------------------------------------------------------------------
#
# Copyright (c) Microsoft Corporation. All rights reserved.
#
# The MIT License (MIT)
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the ""Software""), to
# deal in the Software without restriction, including without limitation the
# rights to use, copy, modify, merge, publish, distribute, sublicense, and/or
# sell copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED *AS IS*, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS
# IN THE SOFTWARE.
#
# --------------------------------------------------------------------------

from base64 import b64decode, b64encode
import calendar
import datetime
import decimal
import email
from enum import Enum
import json
import logging
import re
import sys
import os
try:
    from urllib import quote  # type: ignore
except ImportError:
    from urllib.parse import quote  # type: ignore

if os.environ.get("AZURE_STORAGE_LXML"):
    try:
        from lxml import etree as ET
    except:
        import xml.etree.ElementTree as ET
else:
    import xml.etree.ElementTree as ET

import isodate

from typing import Dict, Any


try:
    basestring  # type: ignore
    unicode_str = unicode  # type: ignore
except NameError:
    basestring = str  # type: ignore
    unicode_str = str  # type: ignore

_LOGGER = logging.getLogger(__name__)

try:
    _long_type = long   # type: ignore
except NameError:
    _long_type = int


from msrest.exceptions import DeserializationError, raise_with_traceback
from msrest.serialization import (
    TZ_UTC,
    _FixedOffset,
    _FLATTEN
)

def full_restapi_key_transformer(key, attr_desc, value):
    """A key transformer that returns the full RestAPI key path.

    :param str _: The attribute name
    :param dict attr_desc: The attribute metadata
    :param object value: The value
    :returns: A list of keys using RestAPI syntax.
    """
    keys = _FLATTEN.split(attr_desc['key'])
    return ([_decode_attribute_map_key(k) for k in keys], value)

def last_restapi_key_transformer(key, attr_desc, value):
    """A key transformer that returns the last RestAPI key.

    :param str key: The attribute name
    :param dict attr_desc: The attribute metadata
    :param object value: The value
    :returns: The last RestAPI key.
    """
    key, value = full_restapi_key_transformer(key, attr_desc, value)
    return (key[-1], value)


def _decode_attribute_map_key(key):
    """This decode a key in an _attribute_map to the actual key we want to look at
       inside the received data.

       :param str key: A key string from the generated code
    """
    return key.replace('\\.', '.')


def rest_key_extractor(attr, attr_desc, data):
    key = attr_desc['key']
    working_data = data

    while '.' in key:
        dict_keys = _FLATTEN.split(key)
        if len(dict_keys) == 1:
            key = _decode_attribute_map_key(dict_keys[0])
            break
        working_key = _decode_attribute_map_key(dict_keys[0])
        working_data = working_data.get(working_key, data)
        if working_data is None:
            # If at any point while following flatten JSON path see None, it means
            # that all properties under are None as well
            # https://github.com/Azure/msrest-for-python/issues/197
            return None
        key = '.'.join(dict_keys[1:])

    return working_data.get(key)

def rest_key_case_insensitive_extractor(attr, attr_desc, data):
    key = attr_desc['key']
    working_data = data

    while '.' in key:
        dict_keys = _FLATTEN.split(key)
        if len(dict_keys) == 1:
            key = _decode_attribute_map_key(dict_keys[0])
            break
        working_key = _decode_attribute_map_key(dict_keys[0])
        working_data = attribute_key_case_insensitive_extractor(working_key, None, working_data)
        if working_data is None:
            # If at any point while following flatten JSON path see None, it means
            # that all properties under are None as well
            # https://github.com/Azure/msrest-for-python/issues/197
            return None
        key = '.'.join(dict_keys[1:])

    if working_data:
        return attribute_key_case_insensitive_extractor(key, None, working_data)

def last_rest_key_extractor(attr, attr_desc, data):
    """Extract the attribute in "data" based on the last part of the JSON path key.
    """
    key = attr_desc['key']
    dict_keys = _FLATTEN.split(key)
    return attribute_key_extractor(dict_keys[-1], None, data)

def last_rest_key_case_insensitive_extractor(attr, attr_desc, data):
    """Extract the attribute in "data" based on the last part of the JSON path key.

    This is the case insensitive version of "last_rest_key_extractor"
    """
    key = attr_desc['key']
    dict_keys = _FLATTEN.split(key)
    return attribute_key_case_insensitive_extractor(dict_keys[-1], None, data)

def attribute_key_extractor(attr, _, data):
    return data.get(attr)

def attribute_key_case_insensitive_extractor(attr, _, data):
    found_key = None
    lower_attr = attr.lower()
    for key in data:
        if lower_attr == key.lower():
            found_key = key
            break

    return data.get(found_key)

def _extract_name_from_internal_type(internal_type):
    """Given an internal type XML description, extract correct XML name with namespace.

    :param dict internal_type: An model type
    :rtype: tuple
    :returns: A tuple XML name + namespace dict
    """
    internal_type_xml_map = getattr(internal_type, "_xml_map", {})
    xml_name = internal_type_xml_map.get('name', internal_type.__name__)
    xml_ns = internal_type_xml_map.get("ns", None)
    if xml_ns:
        xml_name = "{{{}}}{}".format(xml_ns, xml_name)
    return xml_name


def xml_key_extractor(attr, attr_desc, data):
    if isinstance(data, dict):
        return None

    # Test if this model is XML ready first
    if not isinstance(data, ET.Element):
        return None

    xml_desc = attr_desc.get('xml', {})
    xml_name = xml_desc.get('name', attr_desc['key'])

    # Look for a children
    is_iter_type = attr_desc['type'].startswith("[")
    is_wrapped = xml_desc.get("wrapped", False)
    internal_type = attr_desc.get("internalType", None)
    internal_type_xml_map = getattr(internal_type, "_xml_map", {})

    # Integrate namespace if necessary
    xml_ns = xml_desc.get('ns', internal_type_xml_map.get("ns", None))
    if xml_ns:
        xml_name = "{{{}}}{}".format(xml_ns, xml_name)

    # If it's an attribute, that's simple
    if xml_desc.get("attr", False):
        return data.get(xml_name)

    # If it's x-ms-text, that's simple too
    if xml_desc.get("text", False):
        return data.text

    # Scenario where I take the local name:
    # - Wrapped node
    # - Internal type is an enum (considered basic types)
    # - Internal type has no XML/Name node
    if is_wrapped or (internal_type and (issubclass(internal_type, Enum) or 'name' not in internal_type_xml_map)):
        children = data.findall(xml_name)
    # If internal type has a local name and it's not a list, I use that name
    elif not is_iter_type and internal_type and 'name' in internal_type_xml_map:
        xml_name = _extract_name_from_internal_type(internal_type)
        children = data.findall(xml_name)
    # That's an array
    else:
        if internal_type: # Complex type, ignore itemsName and use the complex type name
            items_name = _extract_name_from_internal_type(internal_type)
        else:
            items_name = xml_desc.get("itemsName", xml_name)
        children = data.findall(items_name)

    if len(children) == 0:
        if is_iter_type:
            if is_wrapped:
                return None # is_wrapped no node, we want None
            else:
                return [] # not wrapped, assume empty list
        return None  # Assume it's not there, maybe an optional node.

    # If is_iter_type and not wrapped, return all found children
    if is_iter_type:
        if not is_wrapped:
            return children
        else: # Iter and wrapped, should have found one node only (the wrap one)
            if len(children) != 1:
                raise DeserializationError(
                    "Tried to deserialize an array not wrapped, and found several nodes '{}'. Maybe you should declare this array as wrapped?".format(
                        xml_name
                    ))
            return list(children[0])  # Might be empty list and that's ok.

    # Here it's not a itertype, we should have found one element only or empty
    if len(children) > 1:
        raise DeserializationError("Find several XML '{}' where it was not expected".format(xml_name))
    return children[0]

class Deserializer(object):
    """Response object model deserializer.

    :param dict classes: Class type dictionary for deserializing complex types.
    :ivar list key_extractors: Ordered list of extractors to be used by this deserializer.
    """

    basic_types = {str: 'str', int: 'int', bool: 'bool', float: 'float'}

    valid_date = re.compile(
        r'\d{4}[-]\d{2}[-]\d{2}T\d{2}:\d{2}:\d{2}'
        r'\.?\d*Z?[-+]?[\d{2}]?:?[\d{2}]?')

    def __init__(self, classes=None):
        self.deserialize_type = {
            'iso-8601': Deserializer.deserialize_iso,
            'rfc-1123': Deserializer.deserialize_rfc,
            'unix-time': Deserializer.deserialize_unix,
            'duration': Deserializer.deserialize_duration,
            'date': Deserializer.deserialize_date,
            'time': Deserializer.deserialize_time,
            'decimal': Deserializer.deserialize_decimal,
            'long': Deserializer.deserialize_long,
            'bytearray': Deserializer.deserialize_bytearray,
            'base64': Deserializer.deserialize_base64,
            'object': self.deserialize_object,
            '[]': self.deserialize_iter,
            '{}': self.deserialize_dict
            }
        self.deserialize_expected_types = {
            'duration': (isodate.Duration, datetime.timedelta),
            'iso-8601': (datetime.datetime)
        }
        self.dependencies = dict(classes) if classes else {}
        self.key_extractors = [
            rest_key_extractor,
            xml_key_extractor
        ]
        # Additional properties only works if the "rest_key_extractor" is used to
        # extract the keys. Making it to work whatever the key extractor is too much
        # complicated, with no real scenario for now.
        # So adding a flag to disable additional properties detection. This flag should be
        # used if your expect the deserialization to NOT come from a JSON REST syntax.
        # Otherwise, result are unexpected
        self.additional_properties_detection = True

    def __call__(self, target_obj, response_data, content_type=None):
        """Call the deserializer to process a REST response.

        :param str target_obj: Target data type to deserialize to.
        :param requests.Response response_data: REST response object.
        :param str content_type: Swagger "produces" if available.
        :raises: DeserializationError if deserialization fails.
        :return: Deserialized object.
        """
        data = self._unpack_content(response_data, content_type)
        return self._deserialize(target_obj, data)

    def _deserialize(self, target_obj, data):
        """Call the deserializer on a model.

        Data needs to be already deserialized as JSON or XML ElementTree

        :param str target_obj: Target data type to deserialize to.
        :param object data: Object to deserialize.
        :raises: DeserializationError if deserialization fails.
        :return: Deserialized object.
        """
        # This is already a model, go recursive just in case
        if hasattr(data, "_attribute_map"):
            constants = [name for name, config in getattr(data, '_validation', {}).items()
                         if config.get('constant')]
            try:
                for attr, mapconfig in data._attribute_map.items():
                    if attr in constants:
                        continue
                    value = getattr(data, attr)
                    if value is None:
                        continue
                    local_type = mapconfig['type']
                    internal_data_type = local_type.strip('[]{}')
                    if internal_data_type not in self.dependencies or isinstance(internal_data_type, Enum):
                        continue
                    setattr(
                        data,
                        attr,
                        self._deserialize(local_type, value)
                    )
                return data
            except AttributeError:
                return

        response, class_name = self._classify_target(target_obj, data)

        if isinstance(response, basestring):
            return self.deserialize_data(data, response)
        elif isinstance(response, type) and issubclass(response, Enum):
            return self.deserialize_enum(data, response)

        if data is None:
            return data
        try:
            attributes = response._attribute_map
            d_attrs = {}
            for attr, attr_desc in attributes.items():
                # Check empty string. If it's not empty, someone has a real "additionalProperties"...
                if attr == "additional_properties" and attr_desc["key"] == '':
                    continue
                raw_value = None
                # Enhance attr_desc with some dynamic data
                attr_desc = attr_desc.copy() # Do a copy, do not change the real one
                internal_data_type = attr_desc["type"].strip('[]{}')
                if internal_data_type in self.dependencies:
                    attr_desc["internalType"] = self.dependencies[internal_data_type]

                for key_extractor in self.key_extractors:
                    found_value = key_extractor(attr, attr_desc, data)
                    if found_value is not None:
                        if raw_value is not None and raw_value != found_value:
                            msg = ("Ignoring extracted value '%s' from %s for key '%s'"
                                   " (duplicate extraction, follow extractors order)" )
                            _LOGGER.warning(
                                msg,
                                found_value,
                                key_extractor,
                                attr
                            )
                            continue
                        raw_value = found_value

                value = self.deserialize_data(raw_value, attr_desc['type'])
                d_attrs[attr] = value
        except (AttributeError, TypeError, KeyError) as err:
            msg = "Unable to deserialize to object: " + class_name
            raise_with_traceback(DeserializationError, msg, err)
        else:
            additional_properties = self._build_additional_properties(attributes, data)
            return self._instantiate_model(response, d_attrs, additional_properties)

    def _build_additional_properties(self, attribute_map, data):
        if not self.additional_properties_detection:
            return None
        if "additional_properties" in attribute_map and attribute_map.get("additional_properties", {}).get("key") != '':
            # Check empty string. If it's not empty, someone has a real "additionalProperties"
            return None
        if isinstance(data, ET.Element):
            data = {el.tag: el.text for el in data}

        known_keys = {_decode_attribute_map_key(_FLATTEN.split(desc['key'])[0])
                      for desc in attribute_map.values() if desc['key'] != ''}
        present_keys = set(data.keys())
        missing_keys = present_keys - known_keys
        return {key: data[key] for key in missing_keys}

    def _classify_target(self, target, data):
        """Check to see whether the deserialization target object can
        be classified into a subclass.
        Once classification has been determined, initialize object.

        :param str target: The target object type to deserialize to.
        :param str/dict data: The response data to deseralize.
        """
        if target is None:
            return None, None

        if isinstance(target, basestring):
            try:
                target = self.dependencies[target]
            except KeyError:
                return target, target

        try:
            target = target._classify(data, self.dependencies)
        except AttributeError:
            pass  # Target is not a Model, no classify
        return target, target.__class__.__name__

    def failsafe_deserialize(self, target_obj, data, content_type=None):
        """Ignores any errors encountered in deserialization,
        and falls back to not deserializing the object. Recommended
        for use in error deserialization, as we want to return the
        HttpResponseError to users, and not have them deal with
        a deserialization error.

        :param str target_obj: The target object type to deserialize to.
        :param str/dict data: The response data to deseralize.
        :param str content_type: Swagger "produces" if available.
        """
        try:
            return self(target_obj, data, content_type=content_type)
        except:
            _LOGGER.warning(
                "Ran into a deserialization error. Ignoring since this is failsafe deserialization",
				exc_info=True
            )
            return None

    @staticmethod
    def _unpack_content(raw_data, content_type=None):
        """Extract the correct structure for deserialization.

        If raw_data is a PipelineResponse, try to extract the result of RawDeserializer.
        if we can't, raise. Your Pipeline should have a RawDeserializer.

        If not a pipeline response and raw_data is bytes or string, use content-type
        to decode it. If no content-type, try JSON.

        If raw_data is something else, bypass all logic and return it directly.

        :param raw_data: Data to be processed.
        :param content_type: How to parse if raw_data is a string/bytes.
        :raises JSONDecodeError: If JSON is requested and parsing is impossible.
        :raises UnicodeDecodeError: If bytes is not UTF8
        """
        # This avoids a circular dependency. We might want to consider RawDesializer is more generic
        # than the pipeline concept, and put it in a toolbox, used both here and in pipeline. TBD.
        from .pipeline.universal import RawDeserializer

        # Assume this is enough to detect a Pipeline Response without importing it
        context = getattr(raw_data, "context", {})
        if context:
            if RawDeserializer.CONTEXT_NAME in context:
                return context[RawDeserializer.CONTEXT_NAME]
            raise ValueError("This pipeline didn't have the RawDeserializer policy; can't deserialize")

        #Assume this is enough to recognize universal_http.ClientResponse without importing it
        if hasattr(raw_data, "body"):
            return RawDeserializer.deserialize_from_http_generics(
                raw_data.text(),
                raw_data.headers
            )

        # Assume this enough to recognize requests.Response without importing it.
        if hasattr(raw_data, '_content_consumed'):
            return RawDeserializer.deserialize_from_http_generics(
                raw_data.text,
                raw_data.headers
            )

        if isinstance(raw_data, (basestring, bytes)) or hasattr(raw_data, 'read'):
            return RawDeserializer.deserialize_from_text(raw_data, content_type)
        return raw_data

    def _instantiate_model(self, response, attrs, additional_properties=None):
        """Instantiate a response model passing in deserialized args.

        :param response: The response model class.
        :param d_attrs: The deserialized response attributes.
        """
        if callable(response):
            subtype = getattr(response, '_subtype_map', {})
            try:
                readonly = [k for k, v in response._validation.items()
                            if v.get('readonly')]
                const = [k for k, v in response._validation.items()
                         if v.get('constant')]
                kwargs = {k: v for k, v in attrs.items()
                          if k not in subtype and k not in readonly + const}
                response_obj = response(**kwargs)
                for attr in readonly:
                    setattr(response_obj, attr, attrs.get(attr))
                if additional_properties:
                    response_obj.additional_properties = additional_properties
                return response_obj
            except TypeError as err:
                msg = "Unable to deserialize {} into model {}. ".format(
                    kwargs, response)
                raise DeserializationError(msg + str(err))
        else:
            try:
                for attr, value in attrs.items():
                    setattr(response, attr, value)
                return response
            except Exception as exp:
                msg = "Unable to populate response model. "
                msg += "Type: {}, Error: {}".format(type(response), exp)
                raise DeserializationError(msg)

    def deserialize_data(self, data, data_type):
        """Process data for deserialization according to data type.

        :param str data: The response string to be deserialized.
        :param str data_type: The type to deserialize to.
        :raises: DeserializationError if deserialization fails.
        :return: Deserialized object.
        """
        if data is None:
            return data

        try:
            if not data_type:
                return data
            if data_type in self.basic_types.values():
                return self.deserialize_basic(data, data_type)
            if data_type in self.deserialize_type:
                if isinstance(data, self.deserialize_expected_types.get(data_type, tuple())):
                    return data

                is_a_text_parsing_type = lambda x: x not in ["object", "[]", r"{}"]
                if isinstance(data, ET.Element) and is_a_text_parsing_type(data_type) and not data.text:
                    return None
                data_val = self.deserialize_type[data_type](data)
                return data_val

            iter_type = data_type[0] + data_type[-1]
            if iter_type in self.deserialize_type:
                return self.deserialize_type[iter_type](data, data_type[1:-1])

            obj_type = self.dependencies[data_type]
            if issubclass(obj_type, Enum):
                if isinstance(data, ET.Element):
                    data = data.text
                return self.deserialize_enum(data, obj_type)

        except (ValueError, TypeError, AttributeError) as err:
            msg = "Unable to deserialize response data."
            msg += " Data: {}, {}".format(data, data_type)
            raise_with_traceback(DeserializationError, msg, err)
        else:
            return self._deserialize(obj_type, data)

    def deserialize_iter(self, attr, iter_type):
        """Deserialize an iterable.

        :param list attr: Iterable to be deserialized.
        :param str iter_type: The type of object in the iterable.
        :rtype: list
        """
        if attr is None:
            return None
        if isinstance(attr, ET.Element): # If I receive an element here, get the children
            attr = list(attr)
        if not isinstance(attr, (list, set)):
            raise DeserializationError("Cannot deserialize as [{}] an object of type {}".format(
                iter_type,
                type(attr)
            ))
        return [self.deserialize_data(a, iter_type) for a in attr]

    def deserialize_dict(self, attr, dict_type):
        """Deserialize a dictionary.

        :param dict/list attr: Dictionary to be deserialized. Also accepts
         a list of key, value pairs.
        :param str dict_type: The object type of the items in the dictionary.
        :rtype: dict
        """
        if isinstance(attr, list):
            return {x['key']: self.deserialize_data(x['value'], dict_type) for x in attr}

        if isinstance(attr, ET.Element):
            # Transform <Key>value</Key> into {"Key": "value"}
            attr = {el.tag: el.text for el in attr}
        return {k: self.deserialize_data(v, dict_type) for k, v in attr.items()}

    def deserialize_object(self, attr, **kwargs):
        """Deserialize a generic object.
        This will be handled as a dictionary.

        :param dict attr: Dictionary to be deserialized.
        :rtype: dict
        :raises: TypeError if non-builtin datatype encountered.
        """
        if attr is None:
            return None
        if isinstance(attr, ET.Element):
            # Do no recurse on XML, just return the tree as-is
            return attr
        if isinstance(attr, basestring):
            return self.deserialize_basic(attr, 'str')
        obj_type = type(attr)
        if obj_type in self.basic_types:
            return self.deserialize_basic(attr, self.basic_types[obj_type])
        if obj_type is _long_type:
            return self.deserialize_long(attr)

        if obj_type == dict:
            deserialized = {}
            for key, value in attr.items():
                try:
                    deserialized[key] = self.deserialize_object(
                        value, **kwargs)
                except ValueError:
                    deserialized[key] = None
            return deserialized

        if obj_type == list:
            deserialized = []
            for obj in attr:
                try:
                    deserialized.append(self.deserialize_object(
                        obj, **kwargs))
                except ValueError:
                    pass
            return deserialized

        else:
            error = "Cannot deserialize generic object with type: "
            raise TypeError(error + str(obj_type))

    def deserialize_basic(self, attr, data_type):
        """Deserialize baisc builtin data type from string.
        Will attempt to convert to str, int, float and bool.
        This function will also accept '1', '0', 'true' and 'false' as
        valid bool values.

        :param str attr: response string to be deserialized.
        :param str data_type: deserialization data type.
        :rtype: str, int, float or bool
        :raises: TypeError if string format is not valid.
        """
        # If we're here, data is supposed to be a basic type.
        # If it's still an XML node, take the text
        if isinstance(attr, ET.Element):
            attr = attr.text
            if not attr:
                if data_type == "str":
                    # None or '', node <a/> is empty string.
                    return ''
                else:
                    # None or '', node <a/> with a strong type is None.
                    # Don't try to model "empty bool" or "empty int"
                    return None

        if data_type == 'bool':
            if attr in [True, False, 1, 0]:
                return bool(attr)
            elif isinstance(attr, basestring):
                if attr.lower() in ['true', '1']:
                    return True
                elif attr.lower() in ['false', '0']:
                    return False
            raise TypeError("Invalid boolean value: {}".format(attr))

        if data_type == 'str':
            return self.deserialize_unicode(attr)
        return eval(data_type)(attr)

    @staticmethod
    def deserialize_unicode(data):
        """Preserve unicode objects in Python 2, otherwise return data
        as a string.

        :param str data: response string to be deserialized.
        :rtype: str or unicode
        """
        # We might be here because we have an enum modeled as string,
        # and we try to deserialize a partial dict with enum inside
        if isinstance(data, Enum):
            return data

        # Consider this is real string
        try:
            if isinstance(data, unicode):
                return data
        except NameError:
            return str(data)
        else:
            return str(data)

    @staticmethod
    def deserialize_enum(data, enum_obj):
        """Deserialize string into enum object.

        If the string is not a valid enum value it will be returned as-is
        and a warning will be logged.

        :param str data: Response string to be deserialized. If this value is
         None or invalid it will be returned as-is.
        :param Enum enum_obj: Enum object to deserialize to.
        :rtype: Enum
        """
        if isinstance(data, enum_obj) or data is None:
            return data
        if isinstance(data, Enum):
            data = data.value
        if isinstance(data, int):
            # Workaround. We might consider remove it in the future.
            # https://github.com/Azure/azure-rest-api-specs/issues/141
            try:
                return list(enum_obj.__members__.values())[data]
            except IndexError:
                error = "{!r} is not a valid index for enum {!r}"
                raise DeserializationError(error.format(data, enum_obj))
        try:
            return enum_obj(str(data))
        except ValueError:
            for enum_value in enum_obj:
                if enum_value.value.lower() == str(data).lower():
                    return enum_value
            # We don't fail anymore for unknown value, we deserialize as a string
            _LOGGER.warning("Deserializer is not able to find %s as valid enum in %s", data, enum_obj)
            return Deserializer.deserialize_unicode(data)

    @staticmethod
    def deserialize_bytearray(attr):
        """Deserialize string into bytearray.

        :param str attr: response string to be deserialized.
        :rtype: bytearray
        :raises: TypeError if string format invalid.
        """
        if isinstance(attr, ET.Element):
            attr = attr.text
        return bytearray(b64decode(attr))

    @staticmethod
    def deserialize_base64(attr):
        """Deserialize base64 encoded string into string.

        :param str attr: response string to be deserialized.
        :rtype: bytearray
        :raises: TypeError if string format invalid.
        """
        if isinstance(attr, ET.Element):
            attr = attr.text
        padding = '=' * (3 - (len(attr) + 3) % 4)
        attr = attr + padding
        encoded = attr.replace('-', '+').replace('_', '/')
        return b64decode(encoded)

    @staticmethod
    def deserialize_decimal(attr):
        """Deserialize string into Decimal object.

        :param str attr: response string to be deserialized.
        :rtype: Decimal
        :raises: DeserializationError if string format invalid.
        """
        if isinstance(attr, ET.Element):
            attr = attr.text
        try:
            return decimal.Decimal(attr)
        except decimal.DecimalException as err:
            msg = "Invalid decimal {}".format(attr)
            raise_with_traceback(DeserializationError, msg, err)

    @staticmethod
    def deserialize_long(attr):
        """Deserialize string into long (Py2) or int (Py3).

        :param str attr: response string to be deserialized.
        :rtype: long or int
        :raises: ValueError if string format invalid.
        """
        if isinstance(attr, ET.Element):
            attr = attr.text
        return _long_type(attr)

    @staticmethod
    def deserialize_duration(attr):
        """Deserialize ISO-8601 formatted string into TimeDelta object.

        :param str attr: response string to be deserialized.
        :rtype: TimeDelta
        :raises: DeserializationError if string format invalid.
        """
        if isinstance(attr, ET.Element):
            attr = attr.text
        try:
            duration = isodate.parse_duration(attr)
        except(ValueError, OverflowError, AttributeError) as err:
            msg = "Cannot deserialize duration object."
            raise_with_traceback(DeserializationError, msg, err)
        else:
            return duration

    @staticmethod
    def deserialize_date(attr):
        """Deserialize ISO-8601 formatted string into Date object.

        :param str attr: response string to be deserialized.
        :rtype: Date
        :raises: DeserializationError if string format invalid.
        """
        if isinstance(attr, ET.Element):
            attr = attr.text
        if re.search(r"[^\W\d_]", attr, re.I + re.U):
            raise DeserializationError("Date must have only digits and -. Received: %s" % attr)
        # This must NOT use defaultmonth/defaultday. Using None ensure this raises an exception.
        return isodate.parse_date(attr, defaultmonth=None, defaultday=None)

    @staticmethod
    def deserialize_time(attr):
        """Deserialize ISO-8601 formatted string into time object.

        :param str attr: response string to be deserialized.
        :rtype: datetime.time
        :raises: DeserializationError if string format invalid.
        """
        if isinstance(attr, ET.Element):
            attr = attr.text
        if re.search(r"[^\W\d_]", attr, re.I + re.U):
            raise DeserializationError("Date must have only digits and -. Received: %s" % attr)
        return isodate.parse_time(attr)

    @staticmethod
    def deserialize_rfc(attr):
        """Deserialize RFC-1123 formatted string into Datetime object.

        :param str attr: response string to be deserialized.
        :rtype: Datetime
        :raises: DeserializationError if string format invalid.
        """
        if isinstance(attr, ET.Element):
            attr = attr.text
        try:
            parsed_date = email.utils.parsedate_tz(attr)
            date_obj = datetime.datetime(
                *parsed_date[:6],
                tzinfo=_FixedOffset(datetime.timedelta(minutes=(parsed_date[9] or 0)/60))
            )
            if not date_obj.tzinfo:
                date_obj = date_obj.astimezone(tz=TZ_UTC)
        except ValueError as err:
            msg = "Cannot deserialize to rfc datetime object."
            raise_with_traceback(DeserializationError, msg, err)
        else:
            return date_obj

    @staticmethod
    def deserialize_iso(attr):
        """Deserialize ISO-8601 formatted string into Datetime object.

        :param str attr: response string to be deserialized.
        :rtype: Datetime
        :raises: DeserializationError if string format invalid.
        """
        if isinstance(attr, ET.Element):
            attr = attr.text
        try:
            attr = attr.upper()
            match = Deserializer.valid_date.match(attr)
            if not match:
                raise ValueError("Invalid datetime string: " + attr)

            check_decimal = attr.split('.')
            if len(check_decimal) > 1:
                decimal_str = ""
                for digit in check_decimal[1]:
                    if digit.isdigit():
                        decimal_str += digit
                    else:
                        break
                if len(decimal_str) > 6:
                    attr = attr.replace(decimal_str, decimal_str[0:6])

            date_obj = isodate.parse_datetime(attr)
            test_utc = date_obj.utctimetuple()
            if test_utc.tm_year > 9999 or test_utc.tm_year < 1:
                raise OverflowError("Hit max or min date")
        except(ValueError, OverflowError, AttributeError) as err:
            msg = "Cannot deserialize datetime object."
            raise_with_traceback(DeserializationError, msg, err)
        else:
            return date_obj

    @staticmethod
    def deserialize_unix(attr):
        """Serialize Datetime object into IntTime format.
        This is represented as seconds.

        :param int attr: Object to be serialized.
        :rtype: Datetime
        :raises: DeserializationError if format invalid
        """
        if isinstance(attr, ET.Element):
            attr = int(attr.text)
        try:
            date_obj = datetime.datetime.fromtimestamp(attr, TZ_UTC)
        except ValueError as err:
            msg = "Cannot deserialize to unix datetime object."
            raise_with_traceback(DeserializationError, msg, err)
        else:
            return date_obj