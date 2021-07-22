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

from base64 import b64decode
from typing import cast
import datetime
import decimal
import email
from enum import Enum
import logging
import re
import os

import isodate
from azure.core.exceptions import DecodeError
from msrest.exceptions import DeserializationError, raise_with_traceback
from msrest.serialization import (
    TZ_UTC,
    _FixedOffset
)

if os.environ.get("AZURE_STORAGE_LXML"):
    try:
        from lxml import etree as ET
    except:  # pylint: disable=bare-except
        import xml.etree.ElementTree as ET
else:
    import xml.etree.ElementTree as ET

try:
    basestring  # pylint: disable=pointless-statement
    unicode_str = unicode  # type: ignore
except NameError:
    basestring = str  # type: ignore
    unicode_str = str  # type: ignore

_LOGGER = logging.getLogger(__name__)
_valid_date = re.compile(
    r'\d{4}[-]\d{2}[-]\d{2}T\d{2}:\d{2}:\d{2}'
    r'\.?\d*Z?[-+]?[\d{2}]?:?[\d{2}]?')

try:
    _long_type = long   # type: ignore
except NameError:
    _long_type = int


def unpack_xml_content(response_data, **kwargs):
    """Extract the correct structure for deserialization.

    If raw_data is a PipelineResponse, try to extract the result of RawDeserializer.
    if we can't, raise. Your Pipeline should have a RawDeserializer.

    If not a pipeline response and raw_data is bytes or string, use content-type
    to decode it. If no content-type, try JSON.

    If raw_data is something else, bypass all logic and return it directly.

    :param raw_data: Data to be processed.
    :param content_type: How to parse if raw_data is a string/bytes.
    :raises UnicodeDecodeError: If bytes is not UTF8
    """
    data_as_str = response_data.text()
    try:
        try:
            if isinstance(raw_data, unicode):  # type: ignore
                # If I'm Python 2.7 and unicode XML will scream if I try a "fromstring" on unicode string
                data_as_str = cast(str, data_as_str.encode(encoding="utf-8"))
        except NameError:
            pass
        return ET.fromstring(data_as_str)   # nosec
    except ET.ParseError:
        _LOGGER.critical("Response body invalid XML")
        raise_with_traceback(DecodeError, message="XML is invalid", response=response_data, **kwargs)


def deserialize_bytearray(attr, *_):
    """Deserialize string into bytearray.

    :param str attr: response string to be deserialized.
    :rtype: bytearray
    :raises: TypeError if string format invalid.
    """
    return bytearray(b64decode(attr))


def deserialize_base64(attr, *_):
    """Deserialize base64 encoded string into string.

    :param str attr: response string to be deserialized.
    :rtype: bytearray
    :raises: TypeError if string format invalid.
    """
    padding = '=' * (3 - (len(attr) + 3) % 4)
    attr = attr + padding
    encoded = attr.replace('-', '+').replace('_', '/')
    return b64decode(encoded)


def deserialize_decimal(attr, *_):
    """Deserialize string into Decimal object.

    :param str attr: response string to be deserialized.
    :rtype: Decimal
    :raises: DeserializationError if string format invalid.
    """
    try:
        return decimal.Decimal(attr)
    except decimal.DecimalException as err:
        msg = "Invalid decimal {}".format(attr)
        raise_with_traceback(DeserializationError, msg, err)


def deserialize_bool(attr, *args):
    """Deserialize string into bool.

    :param str attr: response string to be deserialized.
    :rtype: bool
    :raises: TypeError if string format is not valid.
    """
    if attr in [True, False, 1, 0]:
        return bool(attr)
    if isinstance(attr, basestring):
        if attr.lower() in ['true', '1']:
            return True
        if attr.lower() in ['false', '0']:
            return False
    raise TypeError("Invalid boolean value: {}".format(attr))


def deserialize_int(attr, *_):
    """Deserialize string into int.

    :param str attr: response string to be deserialized.
    :rtype: int
    :raises: ValueError or TypeError if string format invalid.
    """
    return int(attr)


def deserialize_float(attr, *_):
    """Deserialize string into float.

    :param str attr: response string to be deserialized.
    :rtype: float
    :raises: ValueError if string format invalid.
    """
    return float(attr)


def deserialize_long(attr, *_):
    """Deserialize string into long (Py2) or int (Py3).

    :param str attr: response string to be deserialized.
    :rtype: long or int
    :raises: ValueError if string format invalid.
    """
    return _long_type(attr)


def deserialize_duration(attr, *_):
    """Deserialize ISO-8601 formatted string into TimeDelta object.

    :param str attr: response string to be deserialized.
    :rtype: TimeDelta
    :raises: DeserializationError if string format invalid.
    """
    try:
        duration = isodate.parse_duration(attr)
    except(ValueError, OverflowError, AttributeError) as err:
        msg = "Cannot deserialize duration object."
        raise_with_traceback(DeserializationError, msg, err)
    else:
        return duration


def deserialize_date(attr, *_):
    """Deserialize ISO-8601 formatted string into Date object.

    :param str attr: response string to be deserialized.
    :rtype: Date
    :raises: DeserializationError if string format invalid.
    """
    if re.search(r"[^\W\d_]", attr, re.I + re.U):
        raise DeserializationError("Date must have only digits and -. Received: %s" % attr)
    # This must NOT use defaultmonth/defaultday. Using None ensure this raises an exception.
    return isodate.parse_date(attr, defaultmonth=None, defaultday=None)


def deserialize_time(attr, *_):
    """Deserialize ISO-8601 formatted string into time object.

    :param str attr: response string to be deserialized.
    :rtype: datetime.time
    :raises: DeserializationError if string format invalid.
    """
    if re.search(r"[^\W\d_]", attr, re.I + re.U):
        raise DeserializationError("Date must have only digits and -. Received: %s" % attr)
    return isodate.parse_time(attr)


def deserialize_rfc(attr, *_):
    """Deserialize RFC-1123 formatted string into Datetime object.

    :param str attr: response string to be deserialized.
    :rtype: Datetime
    :raises: DeserializationError if string format invalid.
    """
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


def deserialize_iso(attr, *_):
    """Deserialize ISO-8601 formatted string into Datetime object.

    :param str attr: response string to be deserialized.
    :rtype: Datetime
    :raises: DeserializationError if string format invalid.
    """
    try:
        attr = attr.upper()
        match = _valid_date.match(attr)
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


def deserialize_object(attr, *_):
    """Deserialize a generic object.
    This will be handled as a dictionary.

    :param dict attr: Dictionary to be deserialized.
    :rtype: dict
    :raises: TypeError if non-builtin datatype encountered.
    """
    # Do no recurse on XML, just return the tree as-is
    # TODO: This probably needs work
    return attr


def deserialize_unix(attr, *_):
    """Serialize Datetime object into IntTime format.
    This is represented as seconds.

    :param int attr: Object to be serialized.
    :rtype: Datetime
    :raises: DeserializationError if format invalid
    """
    try:
        date_obj = datetime.datetime.fromtimestamp(int(attr), TZ_UTC)
    except ValueError as err:
        msg = "Cannot deserialize to unix datetime object."
        raise_with_traceback(DeserializationError, msg, err)
    else:
        return date_obj


def deserialize_unicode(data, *_):
    """Preserve unicode objects in Python 2, otherwise return data
    as a string.

    :param str data: response string to be deserialized.
    :rtype: str or unicode
    """
    if data is None:
        return ""
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
        return deserialize_unicode(data)


def instantiate_model(response, attrs, additional_properties=None):
    """Instantiate a response model passing in deserialized args.

    :param response: The response model class.
    :param d_attrs: The deserialized response attributes.
    """
    try:
        readonly = [k for k, v in response._validation.items() if v.get('readonly')]  # pylint:disable=protected-access
        const = [k for k, v in response._validation.items() if v.get('constant')]  # pylint:disable=protected-access
        kwargs = {k: v for k, v in attrs.items() if k not in readonly + const}
        response_obj = response(**kwargs)
        for attr in readonly:
            setattr(response_obj, attr, attrs.get(attr))
        if additional_properties:
            response_obj.additional_properties = additional_properties
        return response_obj
    except Exception as err:
        msg = "Unable to deserialize {} into model {}. ".format(
            kwargs, response)
        raise DeserializationError(msg + str(err))


def multi_xml_key_extractor(attr_desc, data, subtype):
    xml_desc = attr_desc.get('xml', {})
    xml_name = xml_desc.get('name', attr_desc['key'])
    is_wrapped = xml_desc.get("wrapped", False)
    subtype_xml_map = getattr(subtype, "_xml_map", {})
    if is_wrapped:
        items_name = xml_name
    elif subtype:
        items_name = subtype_xml_map.get('name', xml_name)
    else:
        items_name = xml_desc.get("itemsName", xml_name)
    children = data.findall(items_name)
    if is_wrapped:
        if len(children) == 0:
            return None
        return list(children[0])
    return children

def xml_key_extractor(attr_desc, data, subtype):
    xml_desc = attr_desc.get('xml', {})
    xml_name = xml_desc.get('name', attr_desc['key'])

    # If it's an attribute, that's simple
    if xml_desc.get("attr", False):
        return data.get(xml_name)

    # If it's x-ms-text, that's simple too
    if xml_desc.get("text", False):
        return data.text

    subtype_xml_map = getattr(subtype, "_xml_map", {})
    xml_name = subtype_xml_map.get('name', xml_name)
    return data.find(xml_name)


class Deserializer(object):
    """Response object model deserializer.

    :param dict classes: Class type dictionary for deserializing complex types.
    """
    def __init__(self, classes=None):
        self.deserialize_type = {
            'str': deserialize_unicode,
            'int': deserialize_int,
            'bool': deserialize_bool,
            'float': deserialize_float,
            'iso-8601': deserialize_iso,
            'rfc-1123': deserialize_rfc,
            'unix-time': deserialize_unix,
            'duration': deserialize_duration,
            'date': deserialize_date,
            'time': deserialize_time,
            'decimal': deserialize_decimal,
            'long': deserialize_long,
            'bytearray': deserialize_bytearray,
            'base64': deserialize_base64,
            'object': deserialize_object,
            '[]': self.deserialize_iter,
            '{}': self.deserialize_dict
            }

        self.dependencies = dict(classes) if classes else {}

    def __call__(self, target_obj, response_data, **kwargs):
        """Call the deserializer to process a REST response.

        :param str target_obj: Target data type to deserialize to.
        :param requests.Response response_data: REST response object.
        :param str content_type: Swagger "produces" if available.
        :raises: DeserializationError if deserialization fails.
        :return: Deserialized object.
        """
        try:
            # First, unpack the response if we have one.
            response_data = unpack_xml_content(response_data.http_response, **kwargs)
        except AttributeError:
            pass
        if response_data is None:
            # No data. Moving on.
            return None
        #return self._deserialize(target_obj, response_data)
        return self.deserialize_data(response_data, target_obj)

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
        except:  # pylint: disable=bare-except
            _LOGGER.warning(
                "Ran into a deserialization error. Ignoring since this is failsafe deserialization",
				exc_info=True
            )
            return None

    def _deserialize(self, target_obj, data):
        """Call the deserializer on a model.

        Data needs to be already deserialized as JSON or XML ElementTree

        :param str target_obj: Target data type to deserialize to.
        :param object data: Object to deserialize.
        :raises: DeserializationError if deserialization fails.
        :return: Deserialized object.
        """
        try:
            model_type = self.dependencies[target_obj]
            if issubclass(model_type, Enum):
                return deserialize_enum(data.text, model_type)
        except KeyError:
            return self.deserialize_data(data, target_obj)

        if data is None:
            return data
        try:
            attributes = model_type._attribute_map  # pylint:disable=protected-access
            d_attrs = {}
            include_extra_props = False
            for attr, attr_desc in attributes.items():
                # Check empty string. If it's not empty, someone has a real "additionalProperties"...
                if attr == "additional_properties" and attr_desc["key"] == '':
                    include_extra_props = True
                    continue
                attr_type = attr_desc["type"]
                try:
                    # TODO: Validate this subtype logic
                    subtype = self.dependencies[attr_type.strip('[]{}')]
                except KeyError:
                    subtype = None
                if attr_type[0] == '[':
                    raw_value = multi_xml_key_extractor(attr_desc, data, subtype)
                else:
                    raw_value = xml_key_extractor(attr_desc, data, subtype)
                value = self.deserialize_data(raw_value, attr_type)
                d_attrs[attr] = value
        except (AttributeError, TypeError, KeyError) as err:
            msg = "Unable to deserialize to object: " + str(target_obj)
            raise_with_traceback(DeserializationError, msg, err)
        else:
            if include_extra_props:
                extra = {el.tag: el.text for el in data if el.tag not in d_attrs}
                return instantiate_model(model_type, d_attrs, extra)
            return instantiate_model(model_type, d_attrs)

    def deserialize_data(self, data, data_type):
        """Process data for deserialization according to data type.

        :param str data: The response string to be deserialized.
        :param str data_type: The type to deserialize to.
        :raises: DeserializationError if deserialization fails.
        :return: Deserialized object.
        """
        if not data_type or data is None:
            return None
        try:
            xml_data = data.text
        except AttributeError:
            xml_data = data

        try:
            basic_deserialize = self.deserialize_type[data_type]
            if not xml_data and data_type != 'str':
                return None
            return basic_deserialize(xml_data, data_type)
        except KeyError:
            pass
        except (ValueError, TypeError, AttributeError) as err:
            msg = "Unable to deserialize response data."
            msg += " Data: {}, {}".format(data, data_type)
            raise_with_traceback(DeserializationError, msg, err)

        try:
            iter_type = data_type[0] + data_type[-1]
            if iter_type in self.deserialize_type:
                return self.deserialize_type[iter_type](data, data_type[1:-1])
        except (ValueError, TypeError, AttributeError) as err:
            msg = "Unable to deserialize response data."
            msg += " Data: {}, {}".format(data, data_type)
            raise_with_traceback(DeserializationError, msg, err)
        else:
            return self._deserialize(data_type, data)

    def deserialize_iter(self, attr, iter_type):
        """Deserialize an iterable.

        :param list attr: Iterable to be deserialized.
        :param str iter_type: The type of object in the iterable.
        :rtype: list
        """
        return [self.deserialize_data(a, iter_type) for a in list(attr)]

    def deserialize_dict(self, attr, dict_type):
        """Deserialize a dictionary.

        :param dict/list attr: Dictionary to be deserialized. Also accepts
         a list of key, value pairs.
        :param str dict_type: The object type of the items in the dictionary.
        :rtype: dict
        """
        # Transform <Key>value</Key> into {"Key": "value"}
        attr = {el.tag: el.text for el in attr}
        return {k: self.deserialize_data(v, dict_type) for k, v in attr.items()}
