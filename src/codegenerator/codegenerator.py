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

# To Run: C:\Python27\python.exe codegenerator.py
# It expects the souce files to live in ..\azure\...

from xml.dom import minidom
import urllib2 

BLOB_SERVICE_HOST_BASE = '.blob.core.windows.net'
QUEUE_SERVICE_HOST_BASE = '.queue.core.windows.net'
TABLE_SERVICE_HOST_BASE = '.table.core.windows.net'
SERVICE_BUS_HOST_BASE = '.servicebus.windows.net'

def to_legalname(name):
    """Converts the name of a header value into a value which is a valid Python
       attribute name."""
    if name == 'IncludeAPIs':
        return 'include_apis'
    if name[0] == '$':
        return name[1:]
    name = name.split('=')[0]
    if ':' in name:
        name = name.split(':')[1]
    name = name.replace('-', '_') 
    legalname = name[0]
    for ch in name[1:]:
        if ch.isupper():
            legalname += '_'
        legalname += ch
    legalname = legalname.replace('__', '_').lower().replace('_m_d5', '_md5')
    return legalname

def normalize_xml(xmlstr):
    if xmlstr:
        xmlstr = '>'.join(xml.strip() for xml in xmlstr.split('>'))
        xmlstr = '<'.join(xml.strip() for xml in xmlstr.split('<'))
    return xmlstr

def to_multilines(statements):
    ret = statements.replace('\n', ' \\\n').strip()
    if ret.endswith(' \\'):
        ret = ret[:-2]
    return ret

def get_output_str(name, value, validate_string):
    name = to_legalname(name)
    if value:
        return ''.join([name, '=\'', value, '\''])
    elif 'required' in validate_string:
        return name
    else:
        return name + '=None'

def get_value_validates_comment(value_string):
    value = ''
    validate_string = ''
    comment = ''
    if ';' in value_string:
        value, value_string = value_string.split(';')[:2]
    if '#' in value_string:
        validate_string, comments = value_string.split('#')[:2]
    else:
        validate_string = value_string
    return value, validate_string, comment


def output_import(output_file, class_name):
    indent = '    '
    output_str = 'import base64\n'
    output_str += 'import os\n'
    output_str += 'import urllib2\n\n'
    
    if 'ServiceBus' in class_name:
        output_str += 'from azure.http.httpclient import _HTTPClient\n'
        output_str += 'from azure.http import HTTPError\n'
        output_str += 'from azure.servicebus import (_update_service_bus_header, _create_message, \n'
        output_str += indent*8 + 'convert_topic_to_xml, _convert_response_to_topic, \n'
        output_str += indent*8 + 'convert_queue_to_xml, _convert_response_to_queue, \n'
        output_str += indent*8 + 'convert_subscription_to_xml, _convert_response_to_subscription, \n'
        output_str += indent*8 + 'convert_rule_to_xml, _convert_response_to_rule, \n'
        output_str += indent*8 + '_convert_xml_to_queue, _convert_xml_to_topic, \n'
        output_str += indent*8 + '_convert_xml_to_subscription, _convert_xml_to_rule,\n'
        output_str += indent*8 + '_service_bus_error_handler, AZURE_SERVICEBUS_NAMESPACE, \n'
        output_str += indent*8 + 'AZURE_SERVICEBUS_ACCESS_KEY, AZURE_SERVICEBUS_ISSUER)\n'
    else:
        output_str += 'from azure.storage import *\n'
        output_str += 'from azure.storage.storageclient import _StorageClient\n'
        if 'Blob' in class_name:
            output_str += 'from azure.storage import (_update_storage_blob_header, _create_blob_result,\n'
            output_str += indent*8 + 'convert_block_list_to_xml, convert_response_to_block_list) \n'
        elif 'Queue' in class_name:
            output_str += 'from azure.storage import (_update_storage_queue_header)\n'            
        else:
            output_str += 'from azure.storage import (_update_storage_table_header, \n'
            output_str += indent*8 + 'convert_table_to_xml,  _convert_xml_to_table,\n'
            output_str += indent*8 + 'convert_entity_to_xml, _convert_response_to_entity, \n'
            output_str += indent*8 + '_convert_xml_to_entity, _sign_storage_table_request)\n'

    if 'Table' in class_name:
        output_str += 'from azure.http.batchclient import _BatchClient\n'
    output_str += 'from azure.http import HTTPRequest\n'
    output_str += 'from azure import (_validate_not_none, Feed,\n'
    output_str += indent*8 + '_convert_response_to_feeds, _str_or_none, _int_or_none,\n'
    output_str += indent*8 + '_get_request_body, _update_request_uri_query, \n'
    output_str += indent*8 + '_dont_fail_on_exist, _dont_fail_not_exist, WindowsAzureConflictError, \n'
    output_str += indent*8 + 'WindowsAzureError, _parse_response, _convert_class_to_xml, \n' 
    output_str += indent*8 + '_parse_response_for_dict, _parse_response_for_dict_prefix, \n'
    output_str += indent*8 + '_parse_response_for_dict_filter,  \n'
    output_str += indent*8 + '_parse_enum_results_list, _update_request_uri_query_local_storage, \n'
    output_str += indent*8 + '_get_table_host, _get_queue_host, _get_blob_host, \n'
    output_str += indent*8 + '_parse_simple_list, SERVICE_BUS_HOST_BASE, xml_escape)  \n\n'

    output_file.write(output_str)


def output_class(output_file, class_name, class_comment, class_init_params, x_ms_version):
    indent = '    '

    if 'ServiceBus' in class_name:
        output_str = ''.join(['class ', class_name, ':\n'])
    else:
        output_str = ''.join(['class ', class_name, '(_StorageClient):\n'])
    if class_comment.strip():
        output_str += ''.join([indent, '\'\'\'\n', indent, class_comment.strip(), '\n', indent, '\'\'\'\n\n'])
    else:
        output_str += '\n'

    if 'Table' in class_name:
        output_str += ''.join([indent, 'def begin_batch(self):\n'])
        output_str += indent*2 + 'if self._batchclient is None:\n'
        output_str += indent*3 + 'self._batchclient = _BatchClient(service_instance=self, account_key=self.account_key, account_name=self.account_name)\n'
        output_str += ''.join([indent*2, 'return self._batchclient.begin_batch()\n\n'])
        output_str += ''.join([indent, 'def commit_batch(self):\n'])
        output_str += ''.join([indent*2, 'try:\n'])
        output_str += ''.join([indent*3, 'ret = self._batchclient.commit_batch()\n'])
        output_str += ''.join([indent*2, 'finally:\n'])
        output_str += indent*3 + 'self._batchclient = None\n'
        output_str += ''.join([indent*2, 'return ret\n\n'])
        output_str += ''.join([indent, 'def cancel_batch(self):\n'])
        output_str += indent*2 + 'self._batchclient = None\n\n'

    if not 'ServiceBus' in class_name:
        output_file.write(output_str)
        return 
    
    if not 'service_namespace' in class_init_params:
        output_str += ''.join([indent, 'def begin_batch(self):\n'])
        output_str += ''.join([indent*2, 'self._httpclient.begin_batch()\n\n'])
        output_str += ''.join([indent, 'def commit_batch(self):\n'])
        output_str += ''.join([indent*2, 'self._httpclient.commit_batch()\n\n'])
        output_str += ''.join([indent, 'def cancel_batch(self):\n'])
        output_str += ''.join([indent*2, 'self._httpclient.cancel_batch()\n\n'])

    output_file.write(output_str)


def output_method_def(method_name, method_params, uri_param, req_param, req_query, req_header):
    indent = '    '
    output_def = ''.join([indent, 'def ', method_name, '(self, '])
    for param in uri_param:
        output_def += param.build_sig()

    params = req_param + req_query + req_header
    ordered_params = []
    for name, value, validate_string, comment in params:
        if 'required' in validate_string:
            ordered_params.append((name, value, validate_string, comment))
    for name, value, validate_string, comment in params:
        if 'required' not in validate_string:
            ordered_params.append((name, value, validate_string, comment))
    output_def += ', '.join(get_output_str(name, value, validate_string) for name, value, validate_string, comment in ordered_params)
    if output_def.endswith(', '):
        output_def = output_def[:-2]
    for name, value in method_params:
        output_def += ''.join([', ', name, '=', value])
    output_def += '):\n'

    return output_def


def output_method_comments(method_comment, req_param, req_query, req_header):
    indent = '    '
    output_comments = ''
    if method_comment.strip():
        output_comments += method_comment
    for name, value, validate_string, comment in (req_param + req_query + req_header):
        if comment:
            output_comments += ''.join([indent*2, name, ': ', comment.rstrip(), '\n'])
    if output_comments.strip():
        output_comments = ''.join([indent*2, '\'\'\'\n', output_comments.rstrip(), '\n', indent*2, '\'\'\'\n'])
    return output_comments


def output_method_validates(uri_param, req_param, req_query, req_header):
    indent = '    '
    output_validates = ''
    for param in uri_param:
        output_validates += param.get_validation(indent)
    
    for name, value, validate_string, comment in (req_param + req_query + req_header):
        if not validate_string.strip():
            continue
        validates = validate_string.split(':')
        for validate in validates:
            if 'required' in validate:
                output_validates += ''.join([indent*2, '_validate_not_none(\'', to_legalname(name), '\', ', to_legalname(name), ')\n'])
    return output_validates


HEADER_CONVERSION = {'x-ms-meta-name-values': '%s',
                     }
QUERY_CONVERSION = {'maxresults' : '_int_or_none(%s)', 
                    'timeout' : '_int_or_none(%s)',
                    '$top': '_int_or_none(%s)',}

def output_headers(list_name, request_list):
    return output_list(list_name, request_list, HEADER_CONVERSION)
    
def output_query(list_name, request_list):
    return output_list(list_name, request_list, QUERY_CONVERSION)
    
def output_list(list_name, request_list, validate_conversions):
    indent = '    '
    output_list_str = ''

    if len(request_list) == 1:
        output_list_str += ''.join([indent*2, list_name, ' = [('])
        for name, value, validate_string, comment in request_list:
            validated = validate_conversions.get(name, '_str_or_none(%s)') % (to_legalname(name), )

            if 'base64' in validate_string:
                output_list_str += ''.join(['\'', name, '\', base64.b64encode(', validated, '), '])
            else:
                output_list_str += ''.join(['\'', name, '\', ', validated, ', '])
        output_list_str = ''.join([output_list_str[:-2], ')]\n'])
    elif len(request_list) > 1:
        output_list_str += ''.join([indent*2, list_name, ' = [\n'])
        for name, value, validate_string, comment in request_list:
            validated = validate_conversions.get(name, '_str_or_none(%s)') % (to_legalname(name), )
            
            if 'base64' in validate_string:
                output_list_str += ''.join([indent*3, '(\'', name, '\', base64.b64encode(', validated, ')),\n'])
            else:
                output_list_str += ''.join([indent*3, '(\'', name, '\', ', validated, '),\n'])
        output_list_str = ''.join([output_list_str[:-2], '\n', indent*3, ']\n'])

    return output_list_str


def output_method_body(method_name, return_type, method_params, uri_param, req_protocol, req_host, host_param, req_method, req_uri, req_query, req_header, req_body, req_param):
    indent = '    '
    output_body = ''.join([indent*2, 'request = HTTPRequest()\n'])

    output_body += ''.join([indent*2, 'request.method = \'', req_method, '\'\n'])

    if BLOB_SERVICE_HOST_BASE in req_host:
        output_body += indent*2 + 'request.host = _get_blob_host(self.account_name, self.use_local_storage)\n'
    elif QUEUE_SERVICE_HOST_BASE in req_host:
        output_body += indent*2 + 'request.host = _get_queue_host(self.account_name, self.use_local_storage)\n'
    elif TABLE_SERVICE_HOST_BASE in req_host:
        output_body += indent*2 + 'request.host = _get_table_host(self.account_name, self.use_local_storage)\n'
    else:
        output_body += indent*2 + 'request.host = self.service_namespace + SERVICE_BUS_HOST_BASE\n'
   
    req_uri = req_uri.replace('<subscription-id>', '\' + self.subscription_id + \'')

    for param in uri_param:
        req_uri, extra = param.build_uri(req_uri, 2)
    
        if extra:
            output_body += extra
        
    output_body += ''.join([indent*2, 'request.path = \'', req_uri, '\'\n'])

    output_body += output_headers('request.headers', req_header)
    output_body += output_query('request.query', req_query)

    for name, value, validate_string, comment in req_param:
        if name.startswith('feed:'):
            type = name.split(':')[1]
            output_body += ''.join([indent*2, 'request.body = _get_request_body(convert_' + type + '_to_xml(', to_legalname(name), '))\n'])
            break
        elif name.startswith('class:'):
            if 'block_list' in name:
                output_body += ''.join([indent*2, 'request.body = _get_request_body(convert_block_list_to_xml(', to_legalname(name), '))\n'])
            else:
                output_body += ''.join([indent*2, 'request.body = _get_request_body(_convert_class_to_xml(', to_legalname(name), '))\n'])
            break
        elif name.startswith('binary:'):            
            if 'message' in name:
                output_body += indent*2 + 'request.headers = message.add_headers(request)\n'
                output_body += ''.join([indent*2, 'request.body = _get_request_body(', to_legalname(name), '.body)\n'])
            else:
                output_body += ''.join([indent*2, 'request.body = _get_request_body(', to_legalname(name), ')\n'])
            break
        else:

            fromstr = ''.join([validate_string, '</', name, '>'])
            if value and comment:
                fromstr = ''.join([value, ';', validate_string, '#', comment])
            elif value:
                fromstr = ''.join([value, ';', validate_string])
            elif comment:
                fromstr = ''.join([validate_string, '#', comment])

            tostr = ''.join(['\'', ' + xml_escape(str(', to_legalname(name), ')) + ', '\'</', name, '>'])

            req_body = req_body.replace(fromstr, tostr)

            if len(req_body.strip()) > 80:
                output_body += ''.join([indent*2, 'request.body = _get_request_body(\'', to_multilines(req_body.strip()), '\')\n'])
            elif req_body.strip():
                output_body += ''.join([indent*2, 'request.body = _get_request_body(\'', req_body.strip(), '\')\n'])
    if SERVICE_BUS_HOST_BASE in req_host:
        output_body += indent*2 + 'request.path, request.query = _update_request_uri_query(request)\n'
    else:
        output_body += indent*2 + 'request.path, request.query = _update_request_uri_query_local_storage(request, self.use_local_storage)\n'


    if 'servicebus' in req_host:
        output_body += indent*2 + 'request.headers = _update_service_bus_header(request, self.account_key, self.issuer)\n'
    elif 'table.core.windows.net' in req_host:
        output_body += indent*2 + 'request.headers = _update_storage_table_header(request)\n'
    elif 'blob.core.windows.net' in req_host:
        output_body += indent*2 + 'request.headers = _update_storage_blob_header(request, self.account_name, self.account_key)\n'
    elif 'queue.core.windows.net' in req_host:
        output_body += indent*2 + 'request.headers = _update_storage_queue_header(request, self.account_name, self.account_key)\n'

    for name, value in method_params:
        if 'fail_on_exist' in name:
            if method_name == 'create_queue' and 'queue.core' in req_host:  #QueueService create_queue
                output_body += indent*2 + 'if not ' + name + ':\n'
                output_body += indent*3 + 'try:\n'
                output_body += ''.join([indent*4, 'response = self._perform_request(request)\n'])     
                output_body += ''.join([indent*4, 'if response.status == 204:\n'])
                output_body += ''.join([indent*5, 'return False\n']) 
                output_body += ''.join([indent*4, 'return True\n'])         
                output_body += indent*3 + 'except WindowsAzureError as e:\n'
                output_body += indent*4 + '_dont_fail_on_exist(e)\n'
                output_body += indent*4 + 'return False\n'
                output_body += indent*2 + 'else:\n'
                output_body += ''.join([indent*3, 'response = self._perform_request(request)\n'])
                output_body += ''.join([indent*3, 'if response.status == 204:\n'])
                output_body += ''.join([indent*4, 'raise WindowsAzureConflictError(azure._ERROR_CONFLICT)\n'])
                output_body += ''.join([indent*3, 'return True\n\n'])
            else:
                output_body += indent*2 + 'if not ' + name + ':\n'
                output_body += indent*3 + 'try:\n'
                output_body += ''.join([indent*4, 'self._perform_request(request)\n'])     
                output_body += ''.join([indent*4, 'return True\n'])         
                output_body += indent*3 + 'except WindowsAzureError as e:\n'
                output_body += indent*4 + '_dont_fail_on_exist(e)\n'
                output_body += indent*4 + 'return False\n'
                output_body += indent*2 + 'else:\n'
                output_body += ''.join([indent*3, 'self._perform_request(request)\n'])
                output_body += ''.join([indent*3, 'return True\n\n'])
            break
        elif 'fail_not_exist' in name:
            output_body += indent*2 + 'if not ' + name + ':\n'
            output_body += indent*3 + 'try:\n'
            output_body += ''.join([indent*4, 'self._perform_request(request)\n'])  
            output_body += ''.join([indent*4, 'return True\n'])            
            output_body += indent*3 + 'except WindowsAzureError as e:\n'
            output_body += indent*4 + '_dont_fail_not_exist(e)\n'
            output_body += indent*4 + 'return False\n'
            output_body += indent*2 + 'else:\n'
            output_body += ''.join([indent*3, 'self._perform_request(request)\n'])
            output_body += ''.join([indent*3, 'return True\n\n'])
            break
    else:
        output_body += ''.join([indent*2, 'response = self._perform_request(request)\n\n'])

    if return_type and return_type != 'None':
        if return_type.startswith('dict'):
            return_params = return_type.split('\n')
            if len(return_params) == 1:
                output_body += indent*2 + 'return _parse_response_for_dict(response)\n\n'
            elif len(return_params) == 2:
                value = return_params[1].split('=')[1]
                if return_params[1].startswith('prefix'):
                    output_body += indent*2 + 'return _parse_response_for_dict_prefix(response, prefix=' + value +')\n\n'
                elif return_params[1].startswith('filter'):
                    output_body += indent*2 + 'return _parse_response_for_dict_filter(response, filter=' + value + ')\n\n'
        elif return_type.endswith('EnumResults'):
            output_body += indent*2 + 'return _parse_enum_results_list(response, ' + return_type + ', "' + return_type[:-11] + 's", ' + return_type[:-11] + ')\n\n'
        elif return_type == 'PageList':
            output_body += indent*2 + 'return _parse_simple_list(response, PageList, PageRange, "page_ranges")'
        else:
            if return_type == 'BlobResult':
                output_body += indent*2 + 'return _create_blob_result(response)\n\n'
            elif return_type == 'Message':
                output_body += indent*2 + 'return _create_message(response, self)\n\n'
            elif return_type == 'str':
                output_body += indent*2 + 'return response.body\n\n'
            elif return_type == 'BlobBlockList':
                output_body += indent*2 + 'return convert_response_to_block_list(response)\n\n'
            elif 'Feed' in return_type:           
                for name in ['table', 'entity', 'topic', 'subscription', 'queue', 'rule']:
                    if name +'\'),' in return_type:
                        convert_func = '_convert_xml_to_' + name
                        output_body += indent*2 + 'return _convert_response_to_feeds(response, ' + convert_func + ')\n\n'
                        break
                    elif name in return_type:
                        convert_func = '_convert_response_to_' + name
                        output_body += indent*2 + 'return ' + convert_func + '(response)\n\n'
                        break
            else:
                output_body += indent*2 + 'return _parse_response(response, ' + return_type + ')\n\n'


    return output_body


def output_method(output_file, method_name, method_params, method_comment, return_type, uri_param, req_protocol, req_host, host_param, req_method, req_uri, req_query, req_header, req_body, req_param):
    indent='    '
    output_str = ''
    output_str += output_method_def(method_name, method_params, uri_param, req_param, req_query, req_header)
    output_str += output_method_comments(method_comment, req_param, req_query, req_header)
    output_str += output_method_validates(uri_param, req_param, req_query, req_header)
    output_str += output_method_body(method_name, return_type, method_params, uri_param, req_protocol, req_host, host_param, req_method, req_uri, req_query, req_header, req_body, req_param)    
    output_file.write(output_str)


class UriBuilder(object):
    def __init__(self, value):
        self.uri_str = value
        
    def build_sig(self):
        name = self.uri_str
        if to_legalname(name) != 'subscription_id':
            if '=' in name:
                name, value = name.split('=')
                return ''.join([to_legalname(name), '=', value, ', '])
            else:
                return ''.join([to_legalname(name), ', '])
        return ''
        

    def build_uri(self, req_uri, indent):
        name = self.uri_str
        return req_uri.replace('<' + name + '>', '\' + str(' + to_legalname(name) + ') + \''), ''

    def get_validation(self, indent):
        name = self.uri_str.split('=')[0]
        if to_legalname(name) != 'subscription_id':
            return ''.join([indent*2, '_validate_not_none(\'', to_legalname(name), '\', ', to_legalname(name), ')\n'])
        
        return ''
    
class OptionalUriBuilder(object):
    def __init__(self, value):
        self.value = value
        colon = self.value.find(':')
        self.name = self.value[1:colon]
        self.replacement = self.value[colon+1:].replace('[' + self.name + ']', '" + ' + self.name + ' + "')
        
    def build_sig(self):
        return self.name + ' = None, '
    
    def get_validation(self, indent):
        return ''

    def build_uri(self, req_uri, indent):
        extra = (('    ' * indent) + 'if {name} is not None:\n' +
                ('    ' * (indent+1)) + 'uri_part_{name} = "{replacement}"\n' +
                ('    ' * indent) + 'else:\n' +
                ('    ' * (indent+1)) + 'uri_part_{name} = ""\n').format(name=self.name, replacement=self.replacement)
                
        return req_uri.replace('<' + self.value + '>', "' + uri_part_" + self.name + " + '"), extra
        
def auto_codegen(source_filename, output_filename='output.py'):
    source_file = open(source_filename,'r')
    output_file = open(output_filename,'w')
    return_type = None
    indent = '    '
    method_name = ''
    req_host = ''
    req_method = ''
    req_uri = ''
    req_body = ''
    req_query = []
    req_header = []
    req_param = []
    uri_param = []
    host_param = ''
    class_init_params = []
    class_name = ''
    x_ms_version = ''
    class_comment = ''
    method_comment = ''
    req_protocol = ''
    method_params = []
    methods_code = ''

    line = source_file.readline().strip().lower()
    while True:
        if line == '[end]':
            break
        elif line == '[class]':
            if method_name != '':
                output_method(output_file, method_name, method_params, method_comment, return_type, uri_param, req_protocol, req_host, host_param, req_method, req_uri, req_query, req_header, req_body, req_param)
                method_name = ''
            class_name = source_file.readline().strip()
        elif line == '[x-ms-version]':
            x_ms_version = source_file.readline().strip()
        elif line == '[class-comment]':
            while True:
                line = source_file.readline().strip()
                if line.startswith('['):
                    break
                else:
                    class_comment += ''.join([indent, line, '\n'])
            continue
        elif line == '[init]':  
            while True:
                param_name = source_file.readline().strip()
                if param_name.startswith('['):
                    line = param_name.strip()
                    break
                elif param_name.strip():
                    class_init_params.append(param_name.strip())                                 
            output_import(output_file, class_name)
            output_class(output_file, class_name, class_comment, class_init_params, x_ms_version)
            class_name = ''
            x_ms_version = ''
            class_init_params = []
            class_comment = ''
            continue
        elif line == '[methods_code]':
            while True:
                line = source_file.readline()
                if line.startswith('['):
                    line = line.strip()
                    break
                else:
                    methods_code += ''.join([indent, line])
            continue
        elif line == '[method]':
            if method_name != '':
                output_method(output_file, method_name, method_params, method_comment, return_type, uri_param, req_protocol, req_host, host_param, req_method, req_uri, req_query, req_header, req_body, req_param)
                req_query = []
                req_header = []
                req_param = []
                req_body = ''
                return_type = None
                method_comment = ''
                method_params = []
            method_name = source_file.readline().strip()
        elif line == '[params]':
            method_params = []
            while True:
                param = source_file.readline().strip()
                if param.startswith('['):
                    line = param.strip()
                    break
                elif param.strip():
                    name, value = param.split('=')
                    method_params.append((name, value))
            continue
        elif line == '[comment]':
            while True:
                line = source_file.readline()
                if line.startswith('['):
                    line = line.strip()
                    break
                else:
                    method_comment += ''.join([indent*2, line])
            continue
        elif line == '[return]':
            return_type = ''
            while True:
                line = source_file.readline()
                if line.startswith('['):
                    line = line.strip()
                    break
                else:
                    return_type += line
            return_type = return_type.strip()
            continue
        elif line == '[url]':
            url = source_file.readline().strip()
            if 'https://' in url:
                req_protocol = 'https'
            else:
                req_protocol = 'http'
            req_host = url.split(' ')[1].split('//')[1].split('/')[0]
            host_param = ''
            if '<' in req_host:
                pos1 = req_host.find('<')
                pos2 = req_host.find('>')
                host_param = req_host[pos1+1:pos2] 

            req_method = url.split(' ')[0]
            req_uri = url[url.find('//')+2:].replace(req_host, '')

            uri_param = []
            uri_path = req_uri
            while '<' in uri_path:
                pos1 = uri_path.find('<')
                pos2 = uri_path.find('>')
                uri_param_name = uri_path[pos1+1:pos2]
                
                if uri_param_name.startswith('?'):
                    builder = OptionalUriBuilder(uri_param_name)
                else:
                    builder = UriBuilder(uri_param_name)
                    
                uri_param.append(builder)
                if pos2 < (len(uri_path)-1):
                    uri_path = uri_path[pos2+1:]
                else:
                    break
        elif line == '[query]':
            req_query = []
            while True:
                query = source_file.readline().strip()
                if query.startswith('['):
                    line = query.strip()
                    break
                elif query.strip():
                    name, value = query.split('=')
                    validate_string = ''
                    comment = ''
                    if '#' in value:
                        pos = value.rfind('#')
                        comment = value[pos+1:]
                        value = value[:pos]
                    if ';' in value:
                        value, validate_string = value.split(';')
                    req_query.append((name, value, validate_string, comment))
            continue
        elif line == '[requestheader]':
            req_header = []
            while True:
                header = source_file.readline().strip()
                if header.startswith('['):
                    line = header.strip()
                    break
                elif header.strip():
                    name, value = header.split('=')
                    validate_string = ''
                    comment = ''
                    if '#' in value:
                        pos = value.rfind('#')
                        comment = value[pos+1:]
                        value = value[:pos]
                    if ';' in value:
                        value, validate_string = value.split(';')
                    req_header.append((name, value, validate_string, comment))
            continue
        elif line == '[requestbody]':
            req_body = ''
            req_param = []
            while True:
                body = source_file.readline()
                if body.startswith('['):
                    line = body.strip()
                    break
                elif body.strip():
                    req_body += body

            if req_body.startswith('class:') or req_body.startswith('binary:') or req_body.startswith('feed:'):
                name_value_string = req_body.strip()
                name = ''
                value_string = ''
                if ';' in name_value_string:
                    name, value_string = name_value_string.split(';')
                else:
                    name = name_value_string
                value, validate_string, comment = get_value_validates_comment(value_string)
                req_param.append((name, value, validate_string, comment))
            elif req_body.strip():
                newbody = normalize_xml(req_body)
                xmldoc = minidom.parseString(newbody)
                for xmlelement in xmldoc.childNodes[0].childNodes:
                    value_string = xmlelement.firstChild.nodeValue
                    value, validate_string, comment = get_value_validates_comment(value_string)
                    req_param.append((xmlelement.nodeName, value, validate_string, comment))
            continue
        line = source_file.readline().strip().lower()
        
    output_method(output_file, method_name, method_params, method_comment, return_type, uri_param, req_protocol, req_host, host_param, req_method, req_uri, req_query, req_header, req_body, req_param)
    
    output_file.write('\n' + methods_code)
    source_file.close()
    output_file.close()

if __name__ == '__main__':
    auto_codegen('blob_input.txt', '../azure/storage/blobservice.py')
    auto_codegen('table_input.txt', '../azure/storage/tableservice.py')
    auto_codegen('queue_input.txt', '../azure/storage/queueservice.py')
    auto_codegen('servicebus_input.txt', '../azure/servicebus/servicebusservice.py')

    def add_license(license_str, output_file_name):
        output_file = open(output_file_name, 'r')
        content = output_file.read()
        output_file.close()
        output_file = open(output_file_name, 'w')
        output_file.write(license_str)
        output_file.write(content)
        output_file.close()

    license_str = '''#-------------------------------------------------------------------------
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
'''

    add_license(license_str, '../azure/storage/blobservice.py')
    add_license(license_str, '../azure/storage/tableservice.py')
    add_license(license_str, '../azure/storage/queueservice.py')
    add_license(license_str, '../azure/servicebus/servicebusservice.py')