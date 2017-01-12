#-------------------------------------------------------------------------
# Copyright (c) Microsoft.  All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#--------------------------------------------------------------------------
import ast
import base64
import sys
import types
import warnings

if sys.version_info < (3,):
    from cStringIO import StringIO
    from urllib2 import quote as url_quote
    from urllib2 import unquote as url_unquote
else:
    from io import StringIO
    from urllib.parse import quote as url_quote
    from urllib.parse import unquote as url_unquote

from datetime import datetime
from xml.sax.saxutils import escape as xml_escape

try:
    from xml.etree import cElementTree as ETree
except ImportError:
    from xml.etree import ElementTree as ETree

from ._common_conversion import (
    _str,
)
from ._common_error import (
    _ERROR_VALUE_SHOULD_BE_BYTES,
    _WARNING_VALUE_SHOULD_BE_BYTES,
)
from ._common_models import (
    Feed,
    HeaderDict,
    WindowsAzureData,
    _Base64String,
    _dict_of,
    _list_of,
    _scalar_list_of,
    _unicode_type,
    _xml_attribute,
)


_etree_entity_feed_namespaces = {
    'atom': 'http://www.w3.org/2005/Atom',
    'm': 'http://schemas.microsoft.com/ado/2007/08/dataservices/metadata',
    'd': 'http://schemas.microsoft.com/ado/2007/08/dataservices',
}


def _make_etree_ns_attr_name(ns, name):
    return '{' + ns + '}' + name


def _get_etree_tag_name_without_ns(tag):
    val = tag.partition('}')[2]
    return val


def _get_etree_text(element):
    text = element.text
    return text if text is not None else ''


def _get_readable_id(id_name, id_prefix_to_skip):
    """simplified an id to be more friendly for us people"""
    # id_name is in the form 'https://namespace.host.suffix/name'
    # where name may contain a forward slash!
    pos = id_name.find('//')
    if pos != -1:
        pos += 2
        if id_prefix_to_skip:
            pos = id_name.find(id_prefix_to_skip, pos)
            if pos != -1:
                pos += len(id_prefix_to_skip)
        pos = id_name.find('/', pos)
        if pos != -1:
            return id_name[pos + 1:]
    return id_name


def _to_datetime(strtime):
    return datetime.strptime(strtime, "%Y-%m-%dT%H:%M:%S.%f")

_KNOWN_SERIALIZATION_XFORMS = {
    'last_modified': 'Last-Modified',
    'cache_control': 'Cache-Control',
}


def _get_serialization_name(element_name):
    """converts a Python name into a serializable name"""
    known = _KNOWN_SERIALIZATION_XFORMS.get(element_name)
    if known is not None:
        return known

    if element_name.startswith('x_ms_'):
        return element_name.replace('_', '-')
    if element_name.endswith('_id'):
        element_name = element_name.replace('_id', 'ID')
    for name in ['content_', 'last_modified', 'if_', 'cache_control']:
        if element_name.startswith(name):
            element_name = element_name.replace('_', '-_')

    return ''.join(name.capitalize() for name in element_name.split('_'))


def _convert_class_to_xml(source, xml_prefix=True):
    if source is None:
        return ''

    xmlstr = ''
    if xml_prefix:
        xmlstr = '<?xml version="1.0" encoding="utf-8"?>'

    if isinstance(source, list):
        for value in source:
            xmlstr += _convert_class_to_xml(value, False)
    elif isinstance(source, WindowsAzureData):
        class_name = source.__class__.__name__
        xmlstr += '<' + class_name + '>'
        for name, value in vars(source).items():
            if value is not None:
                if isinstance(value, list) or \
                    isinstance(value, WindowsAzureData):
                    xmlstr += _convert_class_to_xml(value, False)
                else:
                    xmlstr += ('<' + _get_serialization_name(name) + '>' +
                               xml_escape(str(value)) + '</' +
                               _get_serialization_name(name) + '>')
        xmlstr += '</' + class_name + '>'
    return xmlstr


def _set_continuation_from_response_headers(feeds, response):
    x_ms_continuation = HeaderDict()
    for name, value in response.headers:
        if 'x-ms-continuation' in name:
            x_ms_continuation[name[len('x-ms-continuation') + 1:]] = value
    if x_ms_continuation:
        setattr(feeds, 'x_ms_continuation', x_ms_continuation)


def _get_request_body(request_body):
    '''Converts an object into a request body.  If it's None
    we'll return an empty string, if it's one of our objects it'll
    convert it to XML and return it.  Otherwise we just use the object
    directly'''
    if request_body is None:
        return b''

    if isinstance(request_body, WindowsAzureData):
        request_body = _convert_class_to_xml(request_body)

    if isinstance(request_body, bytes):
        return request_body

    if isinstance(request_body, _unicode_type):
        return request_body.encode('utf-8')

    request_body = str(request_body)
    if isinstance(request_body, _unicode_type):
        return request_body.encode('utf-8')

    return request_body


class _ETreeXmlToObject(object):
    @staticmethod
    def parse_response(response, return_type):
        '''
        Parse the HTTPResponse's body and fill all the data into a class of
        return_type.
        '''
        root = ETree.fromstring(response.body)
        xml_name = getattr(return_type, '_xml_name', return_type.__name__) 
        if root.tag == xml_name:
            return _ETreeXmlToObject._parse_response_body_from_xml_node(root, return_type)

        return None


    @staticmethod
    def parse_enum_results_list(response, return_type, resp_type, item_type):
        """resp_body is the XML we received
        resp_type is a string, such as Containers,
        return_type is the type we're constructing, such as ContainerEnumResults
        item_type is the type object of the item to be created, such as Container

        This function then returns a ContainerEnumResults object with the
        containers member populated with the results.
        """

        # parsing something like:
        # <EnumerationResults ... >
        #   <Queues>
        #       <Queue>
        #           <Something />
        #           <SomethingElse />
        #       </Queue>
        #   </Queues>
        # </EnumerationResults>
        return_obj = return_type()
        root = ETree.fromstring(response.body)

        items = []

        for container_element in root.findall(resp_type):
            for item_element in container_element.findall(resp_type[:-1]):
                items.append(_ETreeXmlToObject.fill_instance_element(item_element, item_type))

        for name, value in vars(return_obj).items():
            # queues, Queues, this is the list its self which we populated
            # above
            if name == resp_type.lower():
                # the list its self.
                continue
            value = _ETreeXmlToObject.fill_data_member(root, name, value)
            if value is not None:
                setattr(return_obj, name, value)

        setattr(return_obj, resp_type.lower(), items)
        return return_obj


    @staticmethod
    def parse_simple_list(response, return_type, item_type, list_name):
        respbody = response.body
        res = return_type()
        res_items = []
        root = ETree.fromstring(respbody)
        type_name = type.__name__
        item_name = item_type.__name__
        for item in root.findall(item_name):
            res_items.append(_ETreeXmlToObject.fill_instance_element(item, item_type))

        setattr(res, list_name, res_items)
        return res


    @staticmethod
    def convert_response_to_feeds(response, convert_func):

        if response is None:
            return None

        feeds = _list_of(Feed)

        _set_continuation_from_response_headers(feeds, response)

        root = ETree.fromstring(response.body)

        # some feeds won't have the 'feed' element, just a single 'entry' element
        root_name = _get_etree_tag_name_without_ns(root.tag)
        if root_name == 'feed':
            entries = root.findall("./atom:entry", _etree_entity_feed_namespaces)
        elif root_name == 'entry':
            entries = [root]
        else:
            raise NotImplementedError()

        for entry in entries:
            feeds.append(convert_func(entry))

        return feeds


    @staticmethod
    def get_entry_properties_from_element(element, include_id, id_prefix_to_skip=None, use_title_as_id=False):
        ''' get properties from element tree element '''
        properties = {}

        etag = element.attrib.get(_make_etree_ns_attr_name(_etree_entity_feed_namespaces['m'], 'etag'), None)
        if etag is not None:
            properties['etag'] = etag

        updated = element.findtext('./atom:updated', '', _etree_entity_feed_namespaces)
        if updated:
            properties['updated'] = updated

        author_name = element.findtext('./atom:author/atom:name', '', _etree_entity_feed_namespaces)
        if author_name:
            properties['author'] = author_name

        if include_id:
            if use_title_as_id:
                title = element.findtext('./atom:title', '', _etree_entity_feed_namespaces)
                if title:
                    properties['name'] = title
            else:
                id = element.findtext('./atom:id', '', _etree_entity_feed_namespaces)
                if id:
                    properties['name'] = _get_readable_id(id, id_prefix_to_skip)

        return properties


    @staticmethod
    def fill_instance_element(element, return_type):
        """Converts a DOM element into the specified object"""
        return _ETreeXmlToObject._parse_response_body_from_xml_node(element, return_type)


    @staticmethod
    def fill_data_member(xmldoc, element_name, data_member):
        element = xmldoc.find(_get_serialization_name(element_name))
        if element is None:
            return None

        value = _get_etree_text(element)

        if data_member is None:
            return value
        elif isinstance(data_member, datetime):
            return _to_datetime(value)
        elif type(data_member) is bool:
            return value.lower() != 'false'
        else:
            return type(data_member)(value)


    @staticmethod
    def _parse_response_body_from_xml_node(node, return_type):
        '''
        parse the xml and fill all the data into a class of return_type
        '''
        return_obj = return_type()
        _ETreeXmlToObject._fill_data_to_return_object(node, return_obj)

        return return_obj


    @staticmethod
    def _fill_instance_child(xmldoc, element_name, return_type):
        '''Converts a child of the current dom element to the specified type.
        '''
        element = xmldoc.find(_get_serialization_name(element_name))
        if element is None:
            return None

        return_obj = return_type()
        _ETreeXmlToObject._fill_data_to_return_object(element, return_obj)

        return return_obj


    @staticmethod
    def _fill_data_to_return_object(node, return_obj):
        members = dict(vars(return_obj))
        for name, value in members.items():
            if isinstance(value, _list_of):
                setattr(return_obj,
                        name,
                        _ETreeXmlToObject._fill_list_of(node,
                                      value.list_type,
                                      value.xml_element_name))
            elif isinstance(value, _scalar_list_of):
                setattr(return_obj,
                        name,
                        _ETreeXmlToObject._fill_scalar_list_of(node,
                                             value.list_type,
                                             _get_serialization_name(name),
                                             value.xml_element_name))
            elif isinstance(value, _dict_of):
                setattr(return_obj,
                        name,
                        _ETreeXmlToObject._fill_dict_of(node,
                                      _get_serialization_name(name),
                                      value.pair_xml_element_name,
                                      value.key_xml_element_name,
                                      value.value_xml_element_name))
            elif isinstance(value, _xml_attribute):
                real_value = node.attrib.get(value.xml_element_name, None)
                if real_value is not None:
                    setattr(return_obj, name, real_value)
            elif isinstance(value, WindowsAzureData):
                setattr(return_obj,
                        name,
                        _ETreeXmlToObject._fill_instance_child(node, name, value.__class__))
            elif isinstance(value, dict):
                setattr(return_obj,
                        name,
                        _ETreeXmlToObject._fill_dict(node, _get_serialization_name(name)))
            elif isinstance(value, _Base64String):
                value = _ETreeXmlToObject.fill_data_member(node, name, '')
                if value is not None:
                    value = _decode_base64_to_text(value)
                # always set the attribute, so we don't end up returning an object
                # with type _Base64String
                setattr(return_obj, name, value)
            else:
                value = _ETreeXmlToObject.fill_data_member(node, name, value)
                if value is not None:
                    setattr(return_obj, name, value)


    @staticmethod
    def _fill_list_of(xmldoc, element_type, xml_element_name):
        return [_ETreeXmlToObject._parse_response_body_from_xml_node(xmlelement, element_type) \
            for xmlelement in xmldoc.findall(xml_element_name)]


    @staticmethod
    def _fill_scalar_list_of(xmldoc, element_type, parent_xml_element_name,
                             xml_element_name):
        '''Converts an xml fragment into a list of scalar types.  The parent xml
        element contains a flat list of xml elements which are converted into the
        specified scalar type and added to the list.
        Example:
        xmldoc=
    <Endpoints>
        <Endpoint>http://{storage-service-name}.blob.core.windows.net/</Endpoint>
        <Endpoint>http://{storage-service-name}.queue.core.windows.net/</Endpoint>
        <Endpoint>http://{storage-service-name}.table.core.windows.net/</Endpoint>
    </Endpoints>
        element_type=str
        parent_xml_element_name='Endpoints'
        xml_element_name='Endpoint'
        '''
        raise NotImplementedError('_scalar_list_of not supported')


    @staticmethod
    def _fill_dict(xmldoc, element_name):
        container_element = xmldoc.find(element_name)
        if container_element is not None:
            return_obj = {}
            for item_element in container_element.getchildren():
                return_obj[item_element.tag] = _get_etree_text(item_element)
            return return_obj
        return None


    @staticmethod
    def _fill_dict_of(xmldoc, parent_xml_element_name, pair_xml_element_name,
                      key_xml_element_name, value_xml_element_name):
        '''Converts an xml fragment into a dictionary. The parent xml element
        contains a list of xml elements where each element has a child element for
        the key, and another for the value.
        Example:
        xmldoc=
    <ExtendedProperties>
        <ExtendedProperty>
            <Name>Ext1</Name>
            <Value>Val1</Value>
        </ExtendedProperty>
        <ExtendedProperty>
            <Name>Ext2</Name>
            <Value>Val2</Value>
        </ExtendedProperty>
    </ExtendedProperties>
        element_type=str
        parent_xml_element_name='ExtendedProperties'
        pair_xml_element_name='ExtendedProperty'
        key_xml_element_name='Name'
        value_xml_element_name='Value'
        '''
        raise NotImplementedError('_dict_of not supported')


class _XmlWriter(object):

    def __init__(self, indent_string=None):
        self.file = StringIO()
        self.indent_level = 0
        self.indent_string = indent_string

    def _before_element(self, indent_change):
        if self.indent_string:
            self.indent_level += indent_change
            self.file.write(self.indent_string * self.indent_level)

    def _after_element(self, indent_change):
        if self.indent_string:
            self.file.write('\n')
            self.indent_level += indent_change

    def _write_attrs(self, attrs):
        for attr_name, attr_val, attr_conv in attrs:
            if attr_val is not None:
                self.file.write(' ')
                self.file.write(attr_name)
                self.file.write('="')
                val = attr_conv(_str(attr_val)) if attr_conv else _str(attr_val)
                val = xml_escape(val)
                self.file.write(val)
                self.file.write('"')

    def element(self, name, val, val_conv=None, attrs=None):
        self._before_element(0)
        self.file.write('<')
        self.file.write(name)
        if attrs:
            self._write_attrs(attrs)
        self.file.write('>')
        val = val_conv(_str(val)) if val_conv else _str(val)
        val = xml_escape(val)
        self.file.write(val)
        self.file.write('</')
        self.file.write(name)
        self.file.write('>')
        self._after_element(0)

    def elements(self, name_val_convs):
        for name, val, conv in name_val_convs:
            if val is not None:
                self.element(name, val, conv)

    def preprocessor(self, text):
        self._before_element(0)
        self.file.write(text)
        self._after_element(0)

    def start(self, name, attrs=None):
        self._before_element(0)
        self.file.write('<')
        self.file.write(name)
        if attrs:
            self._write_attrs(attrs)
        self.file.write('>')
        self._after_element(1)

    def end(self, name):
        self._before_element(-1)
        self.file.write('</')
        self.file.write(name)
        self.file.write('>')
        self._after_element(0)

    def xml(self):
        return self.file.getvalue()

    def close(self):
        self.file.close()
