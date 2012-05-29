#------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. 
#
# This source code is subject to terms and conditions of the Apache License, 
# Version 2.0. A copy of the license can be found in the License.html file at 
# the root of this distribution. If you cannot locate the Apache License, 
# Version 2.0, please send an email to vspython@microsoft.com. By using this 
# source code in any fashion, you are agreeing to be bound by the terms of the 
# Apache License, Version 2.0.
#
# You must not remove this notice, or any other, from this software.
#------------------------------------------------------------------------------
import types
from datetime import datetime
from xml.dom import minidom
import base64
import urllib2
import ast

BLOB_SERVICE = 'blob'
QUEUE_SERVICE = 'queue'
TABLE_SERVICE = 'table'
SERVICE_BUS_SERVICE = 'service_bus'

BLOB_SERVICE_HOST_BASE = '.blob.core.windows.net'
QUEUE_SERVICE_HOST_BASE = '.queue.core.windows.net'
TABLE_SERVICE_HOST_BASE = '.table.core.windows.net'
SERVICE_BUS_HOST_BASE = '.servicebus.windows.net'

DEV_BLOB_HOST = '127.0.0.1:10000'
DEV_QUEUE_HOST = '127.0.0.1:10001'
DEV_TABLE_HOST = '127.0.0.1:10002'

DEV_ACCOUNT_NAME = 'devstoreaccount1'
DEV_ACCOUNT_KEY = 'Eby8vdM02xNOcqFlqUwJPLlmEtlCDXJ1OUzFT50uSRZ6IFsuFq2UVErCz4I6tq/K1SZFPTOtr/KBHBeksoGMGw=='

class WindowsAzureData(object):
    pass

class ResponseHeader:
    pass

class ResponseError:
    def __init__(self):
        self.code = ''
        self.message = ''

class _Request:
    def __init__(self):
        self.host = ''
        self.method = ''
        self.uri = ''
        self.query = []
        self.header = []
        self.body = ''
        self.fail_on_exist = True  
        self.fail_not_exist = True 

class HTTPError(Exception):
    def __init__(self, status, message, respheader, respbody):
        self.message = message
        self.status = status
        self.respheader = respheader
        self.respbody = respbody

class WindowsAzureError(Exception):
    def __init__(self, message):
        self.message = message

class Feed:
    def __init__(self, type):
        self.type = type

class _Base64String(str):
    pass
   
def get_entry_properties(xmlstr, properties_name):
    xmldoc = minidom.parseString(xmlstr)
    properties = {}
    for property_name in properties_name:
        xml_properties = xmldoc.getElementsByTagName(property_name)
        if xml_properties:
            xml_property = xml_properties[0]
            if xml_property.firstChild:
                if property_name == 'name':
                    properties['author'] = xml_property.firstChild.nodeValue
                elif property_name == 'id':
                    pos = xml_property.firstChild.nodeValue.rfind('/')
                    if pos != -1:
                        properties['name'] = xml_property.firstChild.nodeValue[pos+1:]
                    else:
                        properties['name'] = xml_property.firstChild.nodeValue
                else:
                    properties[xml_property.nodeName] = xml_property.firstChild.nodeValue
    return properties

def create_entry(entry_body):
    updated_str = datetime.utcnow().isoformat()    
    if datetime.utcnow().utcoffset() is None:
        updated_str += '+00:00'
    
    entry_start = '''
<?xml version="1.0" encoding="utf-8" standalone="yes"?>   
<entry xmlns:d="http://schemas.microsoft.com/ado/2007/08/dataservices" xmlns:m="http://schemas.microsoft.com/ado/2007/08/dataservices/metadata" xmlns="http://www.w3.org/2005/Atom">
<title /><updated>{updated}</updated><author><name /></author><id />
<content type="application/xml">
    '''
    entry_start = entry_start.format(updated=updated_str)
    entry_end = '</content></entry>'

    return entry_start + entry_body + entry_end

def to_datetime(strtime):
    values = strtime.split('T')
    return datetime().strptime(values[0] + ' ' + values[1].split(' ')[1], '%Y-%m-%d %H:%M:%S.%f')

def capitalize_words(element_name):
    if element_name == 'include_apis':
        return 'IncludeAPIs'
    if element_name == 'message_id':
        return 'MessageId'
    if element_name == 'content_md5':
        return 'Content-MD5'
    elif element_name.startswith('x_ms_'):
        return element_name.replace('_', '-')
    if element_name.endswith('_id'):
        element_name = element_name.replace('_id', 'ID')
    for name in ['content_', 'last_modified', 'if_', 'cache_control']:
        if element_name.startswith(name): 
            element_name = element_name.replace('_', '-_')    
    return ''.join(name.capitalize() for name in element_name.split('_'))

def to_right_type(value):
    if value is None or isinstance(value, dict):
        return value
    return str(value)

def to_legalname(name):
    if name == 'IncludeAPIs':
        return 'include_apis'
    name = name.split('=')[0]
    if ':' in name:
        name = name.split(':')[1]
    name = name.replace('-', '_') 
    legalname = name[0]
    for ch in name[1:]:
        if ch.isupper():
            legalname += '_'
        legalname += ch
    legalname = legalname.replace('__', '_').replace('_m_d5', '_md5')
    return legalname.lower()

def normalize_xml(xmlstr):
    if xmlstr:
        xmlstr = '>'.join(string.strip() for string in xmlstr.split('>'))
        xmlstr = '<'.join(string.strip() for string in xmlstr.split('<'))
    return xmlstr

def remove_tag_namespace(name, to_lower=False):
    new_name = name
    if new_name.startswith('m:') or new_name.startswith('d:') or new_name.startswith('i:'):
        new_name = new_name[2:]
    elif new_name.startswith('<m:') or new_name.startswith('<d:'):
        new_name = '<' + new_name[3:]
    elif new_name.startswith('</m:') or new_name.startswith('</d:'):
        new_name = '</' + new_name[4:]

    if to_lower:
        new_name = new_name.lower()
    return new_name

def remove_xmltag_namespace(xmlstr, to_lower=False):
    lower_xmlstr = ''
    non_tag_str = ''
    while '<' in xmlstr:        
        pos1 = xmlstr.find('<')
        pos2 = xmlstr.find('>')
        tag_str = xmlstr[pos1:pos2+1]
        non_tag_str = xmlstr[:pos1]
        xmlstr = xmlstr[pos2+1:]      
        lower_xmlstr += non_tag_str
        tag_items = tag_str.strip().split(' ')
        new_tag = ''
        for tag_item in tag_items:
            if tag_item:
                if '=' in tag_item:
                    pos3 = tag_item.find('=')
                    name = tag_item[:pos3]
                    value = tag_item[pos3+1]
                    new_name = remove_tag_namespace(name, to_lower)
                    tag_item = tag_item.replace(name + '=', new_name + '=')
                else:
                    tag_item = remove_tag_namespace(tag_item, to_lower)
                new_tag += tag_item + ' '
        lower_xmlstr += new_tag.strip()

    if not lower_xmlstr:
        return xmlstr

    return lower_xmlstr

def convert_class_to_xml(source):
    xmlstr = ''
    if isinstance(source, list):
        for value in source:
            xmlstr += convert_class_to_xml(value)
    elif type(source) is types.InstanceType or isinstance(source, WindowsAzureData):
        class_name = source.__class__.__name__
        xmlstr += '<' + class_name
        if 'attributes' in dir(source):
            attributes = getattr(source, 'attributes')
            for name, value in attributes:
                xmlstr += ' ' + name + '="' + value + '"'
        xmlstr += '>'
        for name, value in vars(source).iteritems():
            if value is not None:
                if isinstance(value, list) or type(value) is types.InstanceType or isinstance(value, WindowsAzureData):
                    xmlstr += convert_class_to_xml(value)
                else:
                    xmlstr += '<' + capitalize_words(name) + '>' + str(value) + '</' + capitalize_words(name) + '>'
        xmlstr += '</' + class_name + '>'
    return xmlstr

def convert_xml_to_feeds(xmlstr, convert_func):
        feeds = []
        xmldoc = minidom.parseString(xmlstr)
        xml_entries = xmldoc.getElementsByTagName('entry')
        for xml_entry in xml_entries:
            feeds.append(convert_func(xml_entry.toxml()))
        return feeds

def validate_not_none(param_name, param):
    if param is None:
        raise ValueError('invalid_value: ', '%s should not be None.' % (param_name))

def validate_length(param_name, param, valid_range):
    valid_range = str(valid_range)
    left = valid_range[0]
    right = valid_range[-1]

    if left not in ('[','(') or right not in (']',')'):
        #raise ValueError('invalid_value_range_format: ', ''.join([param_name, ' has invalid range format:', valid_range, '. Length format should be like [1,3] or (1, 3).']))
        raise ValueError('invalid_value_range_format: ', '% has invalid range format: %s. Length format should be like [1,3] or (1, 3).' % (param_name, valid_range))
    try:
        valid_range = valid_range[1:-1]
        left_value, right_value = valid_range.split(',')
        left_value = int(left_value.strip())
        right_value = int(right_value.strip())
        if left == '[' and len(param) < left_value or left == '(' and len(param) <= left_value or right == ']' and len(param) > right_value or right == ')' and len(param) > right_value:
            #raise ValueError('invalid_value: ', ''.join([param_name, ' should be in range ', valid_range]))
            raise ValueError('invalid_value: ', '%s should be in range %s.' % (param_name, valid_range))
    except:
        raise ValueError('invalid_value_range_format: ', '%s has invalid length range. The length should be integer.' % (param_name))

def validate_values(param_name, param, valid_values):
    valid_values = str(valid_values)
    if not param in valid_values:
        raise ValueError('invalid_value: ', '%s has invalid value. Allowed values are:' % (param_name, valid_values))

def html_encode(html):
    ch_map = (('&', '&amp;'), ('<', '&lt;'), ('>', '&gt;'), ('"', '&quot'), ('\'', '&apos'))
    for name, value in ch_map:
        html = html.replace(name, value)
    return html



    #move to some class
def fill_list(xmlstr, parent_node_name, module_name):
    '''
    Extract values of child Nodes of parentNodeName from xmlstr and add all the values to the list, and return the list
    the elementName is the parent and the way we search the child node is using following rules:
    (1) remove the last 's': deployments->deployment
    (2) change the last 'ies' to 'y':  properties->property
    (3) remove the last 'list': InputEndpointList->InputEndpoint
    (4) use elementName as child node name
    moduleName is used to extract the predefined class name to check whether this is instance list or base type list
    '''

    xmldoc = minidom.parseString(xmlstr)
        
    child_node_name = parent_node_name

    xmlelements = None
    if parent_node_name.endswith('s'):
        child_node_name = parent_node_name[:-1]
        xmlelements = xmldoc.getElementsByTagName(capitalize_words(child_node_name))
    elif parent_node_name.endswith('ies'):
        child_node_name = parent_node_name[:-3] + 'y'
        xmlelements = xmldoc.getElementsByTagName(capitalize_words(child_node_name))
    elif parent_node_name.endswith('List'):
        child_node_name = parent_node_name.replace('List','')
        xmlelements = xmldoc.getElementsByTagName(capitalize_words(child_node_name))
    else:
        child_node_name = parent_node_name
        xmlelements = xmldoc.getElementsByTagName(capitalize_words(child_node_name))
       
    if not xmlelements:
        return []

    return_list = []
    for xmlelement in xmlelements:
        from_list = '.'.join(module_name.split('.')[:-1])
        _module = __import__(module_name, fromlist=from_list)
        new_child_node_name = capitalize_words(child_node_name)
        if new_child_node_name in dir(_module):
            return_list.append(_parse_response(xmlelement.toxml(), getattr(_module, new_child_node_name)))
        else:
            return_list.append(xmlelement.nodeValue)

    return return_list

def fill_instance(xmlstr, element_name, return_type):
    '''
    Extract the value of elementName and put it into corresponding class instance. return the instance.
    moduleName is used to get class structure.
    '''
    xmldoc = minidom.parseString(xmlstr)
    xmlelements = xmldoc.getElementsByTagName(capitalize_words(element_name))

    if not xmlelements:
        return None

    xmlelement = xmlelements[0]

    return _parse_response(xmlelement.toxml(), return_type)

def fill_data(xmlstr, element_name, data_member):
    xmldoc = minidom.parseString(xmlstr)
    xmlelements = xmldoc.getElementsByTagName(capitalize_words(element_name))

    if not xmlelements or not xmlelements[0].childNodes:
        return None

    value = xmlelements[0].firstChild.nodeValue

    if data_member is None:
        return value
    elif isinstance(data_member, datetime):
        return to_datetime(value)
    elif isinstance(data_member, _Base64String):
        return base64.b64decode(value)
    elif type(data_member) is types.BooleanType:
        return value.lower() != 'false'
    else:
        return type(data_member)(value)

def _get_request_body(request_body):
        
    if request_body == None:
        return ''

    if type(request_body) is types.InstanceType or isinstance(request_body, WindowsAzureData):
        request_body = '<?xml version="1.0" encoding="utf-8"?>' + convert_class_to_xml(request_body)

    if not request_body.strip().startswith('<'):
        return request_body

    updated_str = datetime.utcnow().isoformat()    
    if datetime.utcnow().utcoffset() is None:
        updated_str += '+00:00'

    if request_body:
        request_body = normalize_xml(request_body).strip()

    return request_body

def _get_response_header(service_instance):
    return_obj = ResponseHeader()
    if service_instance.respheader:
        for name, value in service_instance.respheader:
            setattr(return_obj, to_legalname(name), value)
    return_obj.status = service_instance.status
    return_obj.message = service_instance.message
    return return_obj        

def _parse_response(respbody, return_type):  
    '''
    parse the xml response and fill all the data into a class of return_type
    '''
    normalize_xml(respbody)

    return_obj = return_type()
    for name, value in vars(return_obj).iteritems():
        if isinstance(value, list):
            setattr(return_obj, name, fill_list(respbody, name, return_obj.__module__))
        elif type(value) is types.InstanceType  or isinstance(value, WindowsAzureData):
            setattr(return_obj, name, fill_instance(respbody, name, value.__class__))
        else:
            value = fill_data(respbody, name, value)
            if value is not None:
                setattr(return_obj, name, value)

    return return_obj

def _update_request_uri_query(request, use_local_storage=False):
    if '?' in request.uri:
        pos = request.uri.find('?')
        query_string = request.uri[pos+1:]
        request.uri = request.uri[:pos]           
        if query_string:
            query_params = query_string.split('&')
            for query in query_params:
                if '=' in query:
                    pos = query.find('=')
                    name = query[:pos]
                    value = query[pos+1:]
                    request.query.append((name, value))

    request.uri = urllib2.quote(request.uri, '/()$=\',')
    if request.query:
        request.uri += '?' 
        for name, value in request.query:
            if value is not None:
                request.uri += name + '=' + urllib2.quote(value, '/()$=\',') + '&'
        request.uri = request.uri[:-1]
        if use_local_storage:
            request.uri = '/' + DEV_ACCOUNT_NAME + request.uri
        return request.uri, request.query
    else:
        if use_local_storage:
            request.uri = '/' + DEV_ACCOUNT_NAME + request.uri
        return request.uri, request.query

def _dont_fail_on_exist(error):
    if error.message.lower() == 'conflict':
        return False
    else:
        raise error

def _dont_fail_not_exist(error):
    if error.message.lower() == 'not found':
        return False
    else:
        raise error
    
def _parse_response_for_dict(service_instance):
    http_headers = ['server', 'date', 'location', 'host', 
                    'via', 'proxy-connection', 'x-ms-version', 'connection',
                    'content-length', 'x-ms-request-id']
    if service_instance.respheader:
        return_dict = {}
        for name, value in service_instance.respheader:
            if not name.lower() in http_headers:
                return_dict[name] = value
    return return_dict

def _parse_response_for_dict_prefix(service_instance, prefix):
    return_dict = {}    
    orig_dict = _parse_response_for_dict(service_instance)
    if orig_dict:
        for name, value in orig_dict.iteritems():
            for prefix_value in prefix:
                if name.lower().startswith(prefix_value.lower()):
                    return_dict[name] = value
                    break
        return return_dict
    else:
        return None

def _parse_response_for_dict_filter(service_instance, filter):
    return_dict = {}    
    orig_dict = _parse_response_for_dict(service_instance)
    if orig_dict:
        for name, value in orig_dict.iteritems():
            if name.lower() in filter:
                return_dict[name] = value
        return return_dict
    else:
        return None

def _parse_response_for_dict_special(service_instance, prefix, filter):
    return_dict = {}    
    orig_dict = _parse_response_for_dict(service_instance)
    if orig_dict:
        for name, value in orig_dict.iteritems():
            if name.lower() in filter:
                return_dict[name] = value
            else:
                for prefix_value in prefix:
                    if name.lower().startswith(prefix_value.lower()):
                        return_dict[name] = value
                        break
        return return_dict
    else:
        return None

def get_host(service_type, account_name, use_local_storage=False):
    if use_local_storage:
        if service_type == BLOB_SERVICE:
            return DEV_BLOB_HOST
        elif service_type == QUEUE_SERVICE:
            return DEV_QUEUE_HOST
        elif service_type == TABLE_SERVICE:
            return DEV_TABLE_HOST
        elif service_type == SERVICE_BUS_SERVICE:
            return account_name + SERVICE_BUS_HOST_BASE
    else:
        if service_type == BLOB_SERVICE:
            return account_name + BLOB_SERVICE_HOST_BASE
        elif service_type == QUEUE_SERVICE:
            return account_name + QUEUE_SERVICE_HOST_BASE
        elif service_type == TABLE_SERVICE:
            return account_name + TABLE_SERVICE_HOST_BASE
        else:
            return account_name + SERVICE_BUS_HOST_BASE

