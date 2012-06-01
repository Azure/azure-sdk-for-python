#-------------------------------------------------------------------------
# Copyright 2011 Microsoft Corporation
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
import sys
import time
import urllib2
from xml.dom import minidom
import ast
import httplib
from datetime import datetime


from azure.http import HTTPError
from azure import (WindowsAzureError, WindowsAzureData, 
                          _create_entry, _get_entry_properties, _html_encode,
                          _get_child_nodes, WindowsAzureMissingResourceError,
                          WindowsAzureConflictError, _get_serialization_name, 
                          _get_children_from_path)
import azure

#default rule name for subscription
DEFAULT_RULE_NAME='$Default'

#-----------------------------------------------------------------------------
# Constants for Azure app environment settings. 
AZURE_SERVICEBUS_NAMESPACE = 'AZURE_SERVICEBUS_NAMESPACE'
AZURE_SERVICEBUS_ACCESS_KEY = 'AZURE_SERVICEBUS_ACCESS_KEY'
AZURE_SERVICEBUS_ISSUER = 'AZURE_SERVICEBUS_ISSUER'

#token cache for Authentication
_tokens = {}

# namespace used for converting rules to objects
XML_SCHEMA_NAMESPACE = 'http://www.w3.org/2001/XMLSchema-instance'

class Queue(WindowsAzureData):
    ''' Queue class corresponding to Queue Description: http://msdn.microsoft.com/en-us/library/windowsazure/hh780773'''

    def __init__(self):
        self.lock_duration = ''
        self.max_size_in_megabytes = ''
        self.duplicate_detection = ''
        self.requires_duplicate_detection = ''
        self.requires_session = ''
        self.default_message_time_to_live = ''
        self.enable_dead_lettering_on_message_expiration = ''
        self.duplicate_detection_history_time_window = ''
        self.max_delivery_count = ''
        self.enable_batched_operations = ''
        self.size_in_bytes = ''
        self.message_count = ''

class Topic(WindowsAzureData):
    ''' Topic class corresponding to Topic Description: http://msdn.microsoft.com/en-us/library/windowsazure/hh780749. '''

    def __init__(self):
        self.default_message_time_to_live = ''
        self.max_size_in_mega_bytes = ''
        self.requires_duplicate_detection = ''
        self.duplicate_detection_history_time_window = ''
        self.enable_batched_operations = ''
        self.size_in_bytes = ''

class Subscription(WindowsAzureData):
    ''' Subscription class corresponding to Subscription Description: http://msdn.microsoft.com/en-us/library/windowsazure/hh780763. '''

    def __init__(self):
        self.lock_duration = ''
        self.requires_session = ''
        self.default_message_time_to_live = ''
        self.dead_lettering_on_message_expiration = ''
        self.dead_lettering_on_filter_evaluation_exceptions = ''
        self.enable_batched_operations = ''
        self.max_delivery_count = ''
        self.message_count = ''

class Rule(WindowsAzureData):
    ''' Rule class corresponding to Rule Description: http://msdn.microsoft.com/en-us/library/windowsazure/hh780753. '''

    def __init__(self):
        self.filter_type = ''
        self.filter_expression = ''
        self.action_type = ''
        self.action_expression = ''

class Message(WindowsAzureData):
    ''' Message class that used in send message/get mesage apis. '''

    def __init__(self, body=None, service_bus_service=None, location=None, custom_properties=None, 
                 type='application/atom+xml;type=entry;charset=utf-8', broker_properties=None):
        self.body = body
        self.location = location
        self.broker_properties = broker_properties
        self.custom_properties = custom_properties
        self.type = type
        self.service_bus_service = service_bus_service
        self._topic_name = None
        self._subscription_name = None
        self._queue_name = None

        if not service_bus_service:
            return 

        # if location is set, then extracts the queue name for queue message and 
        # extracts the topic and subscriptions name if it is topic message.
        if location:
            if '/subscriptions/' in location:
                pos = location.find('/subscriptions/')
                pos1 = location.rfind('/', 0, pos-1)
                self._topic_name = location[pos1+1:pos]
                pos += len('/subscriptions/')
                pos1 = location.find('/', pos)
                self._subscription_name = location[pos:pos1]
            elif '/messages/' in location:
                pos = location.find('/messages/')
                pos1 = location.rfind('/', 0, pos-1)
                self._queue_name = location[pos1+1:pos]
                    
    def delete(self):
        ''' Deletes itself if find queue name or topic name and subscription name. ''' 
        if self._queue_name:
            self.service_bus_service.delete_queue_message(self._queue_name, self.broker_properties['SequenceNumber'], self.broker_properties['LockToken'])
        elif self._topic_name and self._subscription_name:
            self.service_bus_service.delete_subscription_message(self._topic_name, self._subscription_name, self.broker_properties['SequenceNumber'], self.broker_properties['LockToken'])
        else:
            raise WindowsAzureError(azure._ERROR_MESSAGE_NOT_PEEK_LOCKED_ON_DELETE)

    def unlock(self):
        ''' Unlocks itself if find queue name or topic name and subscription name. ''' 
        if self._queue_name:
            self.service_bus_service.unlock_queue_message(self._queue_name, self.broker_properties['SequenceNumber'], self.broker_properties['LockToken'])
        elif self._topic_name and self._subscription_name:
            self.service_bus_service.unlock_subscription_message(self._topic_name, self._subscription_name, self.broker_properties['SequenceNumber'], self.broker_properties['LockToken'])
        else:
            raise WindowsAzureError(azure._ERROR_MESSAGE_NOT_PEEK_LOCKED_ON_UNLOCK)

    def add_headers(self, request):
        ''' add addtional headers to request for message request.'''

        # Adds custom properties
        if self.custom_properties:
            for name, value in self.custom_properties.iteritems():
                if isinstance(value, str):
                    request.headers.append((name, '"' + str(value) + '"'))
                elif isinstance(value, datetime):
                    request.headers.append((name, '"' + value.strftime('%a, %d %b %Y %H:%M:%S GMT') + '"'))
                else:
                    request.headers.append((name, str(value)))
        
        # Adds content-type
        request.headers.append(('Content-Type', self.type))

        # Adds BrokerProperties
        if self.broker_properties:
            request.headers.append(('BrokerProperties', str(self.broker_properties)))

        return request.headers

def _update_service_bus_header(request, account_key, issuer): 
    ''' Add additional headers for service bus. '''

    if request.method in ['PUT', 'POST', 'MERGE', 'DELETE']:
        request.headers.append(('Content-Length', str(len(request.body))))  
        
    # if it is not GET or HEAD request, must set content-type.            
    if not request.method in ['GET', 'HEAD']:
        for name, value in request.headers:
            if 'content-type' == name.lower():
                break
        else:
            request.headers.append(('Content-Type', 'application/atom+xml;type=entry;charset=utf-8')) 

    # Adds authoriaztion header for authentication.
    request.headers.append(('Authorization', _sign_service_bus_request(request, account_key, issuer)))

    return request.headers

def _sign_service_bus_request(request, account_key, issuer):
    ''' return the signed string with token. '''

    return 'WRAP access_token="' + _get_token(request, account_key, issuer) + '"'

def _token_is_expired(token):
    ''' Check if token expires or not. '''
    time_pos_begin = token.find('ExpiresOn=') + len('ExpiresOn=')
    time_pos_end = token.find('&', time_pos_begin)
    token_expire_time = int(token[time_pos_begin:time_pos_end])
    time_now = time.mktime(time.localtime())

    #Adding 30 seconds so the token wouldn't be expired when we send the token to server.
    return (token_expire_time - time_now) < 30

def _get_token(request, account_key, issuer):   
    ''' 
    Returns token for the request. 
    
    request: the service bus service request.
    account_key: service bus access key
    issuer: service bus issuer
    '''
    wrap_scope = 'http://' + request.host + request.uri
       
    # Check whether has unexpired cache, return cached token if it is still usable. 
    if _tokens.has_key(wrap_scope):
        token = _tokens[wrap_scope]
        if not _token_is_expired(token):
            return token

    #get token from accessconstrol server
    request_body = ('wrap_name=' + urllib2.quote(issuer) + '&wrap_password=' +
                    urllib2.quote(account_key) + '&wrap_scope=' + 
                    urllib2.quote('http://' + request.host + request.uri))
    host = request.host.replace('.servicebus.', '-sb.accesscontrol.')
    if sys.platform.lower().startswith('win'):
        import azure.http.winhttp
        connection = azure.http.winhttp._HTTPConnection(host, protocol='https')
    else:
        connection = httplib.HTTPSConnection(host)
    connection.putrequest('POST', '/WRAPv0.9')
    connection.putheader('Content-Length', len(request_body))
    connection.endheaders()
    connection.send(request_body)
    resp = connection.getresponse()
    token = ''
    if int(resp.status) >= 200 and int(resp.status) < 300:
        if resp.length:
            token = resp.read(resp.length)
        else:
            raise HTTPError(resp.status, resp.reason, resp.getheaders(), None)
    else:
        raise HTTPError(resp.status, resp.reason, resp.getheaders(), None)
        
    token = urllib2.unquote(token[token.find('=')+1:token.rfind('&')])
    _tokens[wrap_scope] = token

    return token

def _create_message(response, service_instance):
    ''' Create message from response. 
    
    response: response from service bus cloud server.
    service_instance: the service bus client.
    '''
    respbody = response.body
    custom_properties = {}
    broker_properties = None
    message_type = None
    message_location = None

    #gets all information from respheaders.
    for name, value in response.headers:
        if name.lower() == 'brokerproperties':
            broker_properties = ast.literal_eval(value)
        elif name.lower() == 'content-type':
            message_type = value
        elif name.lower() == 'location':
            message_location = value
        elif name.lower() not in ['content-type', 'brokerproperties', 'transfer-encoding', 'server', 'location', 'date']:
            if '"' in value:
                custom_properties[name] = value[1:-1]
            else:
                custom_properties[name] = value
    if message_type == None:
        message = Message(respbody, service_instance, message_location, custom_properties, broker_properties)
    else:
        message = Message(respbody, service_instance, message_location, custom_properties, message_type, broker_properties)
    return message

#convert functions
def _convert_response_to_rule(response):
    return _convert_xml_to_rule(response.body)

def _convert_xml_to_rule(xmlstr):
    ''' Converts response xml to rule object.  

    The format of xml for rule:
    <entry xmlns='http://www.w3.org/2005/Atom'>  
    <content type='application/xml'>    
    <RuleDescription xmlns:i="http://www.w3.org/2001/XMLSchema-instance" xmlns="http://schemas.microsoft.com/netservices/2010/10/servicebus/connect">
     <Filter i:type="SqlFilterExpression">
      <SqlExpression>MyProperty='XYZ'</SqlExpression>
     </Filter>
     <Action i:type="SqlFilterAction">
      <SqlExpression>set MyProperty2 = 'ABC'</SqlExpression>
     </Action>
    </RuleDescription>
    </content>
    </entry>
    '''
    xmldoc = minidom.parseString(xmlstr)
    rule = Rule()
        
    for rule_desc in _get_children_from_path(xmldoc, 'entry', 'content', 'RuleDescription'):
        for xml_filter in _get_child_nodes(rule_desc, 'Filter'):
            filter_type = xml_filter.getAttributeNS(XML_SCHEMA_NAMESPACE, 'type')
            setattr(rule, 'filter_type', str(filter_type))
            if xml_filter.childNodes:

                for expr in _get_child_nodes(xml_filter, 'SqlExpression'):
                    setattr(rule, 'filter_expression', expr.firstChild.nodeValue)
                
        for xml_action in _get_child_nodes(rule_desc, 'Action'):
            action_type = xml_action.getAttributeNS(XML_SCHEMA_NAMESPACE, 'type')
            setattr(rule, 'action_type', str(action_type))
            if xml_action.childNodes:
                action_expression = xml_action.childNodes[0].firstChild
                if action_expression:
                    setattr(rule, 'action_expression', action_expression.nodeValue)
   
    #extract id, updated and name value from feed entry and set them of rule.
    for name, value in _get_entry_properties(xmlstr, True).iteritems():
        setattr(rule, name, value)

    return rule

def _convert_response_to_queue(response):
    return _convert_xml_to_queue(response.body)

def _convert_xml_to_queue(xmlstr):
    ''' Converts xml response to queue object.
    
    The format of xml response for queue:
    <QueueDescription xmlns=\"http://schemas.microsoft.com/netservices/2010/10/servicebus/connect\">
    <MaxSizeInBytes>10000</MaxSizeInBytes>
    <DefaultMessageTimeToLive>PT5M</DefaultMessageTimeToLive>
    <LockDuration>PT2M</LockDuration>
    <RequiresGroupedReceives>False</RequiresGroupedReceives>
    <SupportsDuplicateDetection>False</SupportsDuplicateDetection>
    ...
    </QueueDescription>

    '''
    xmldoc = minidom.parseString(xmlstr)
    queue = Queue()

    invalid_queue = True
    #get node for each attribute in Queue class, if nothing found then the response is not valid xml for Queue.
    for queue_desc in _get_children_from_path(xmldoc, 'entry', 'content', 'QueueDescription'):
        for attr_name, attr_value in vars(queue).iteritems():
            xml_attrs = _get_child_nodes(queue_desc, _get_serialization_name(attr_name))
            if xml_attrs:
                xml_attr = xml_attrs[0]
                if xml_attr.firstChild:
                    setattr(queue, attr_name, 
                            xml_attr.firstChild.nodeValue)
                    invalid_queue = False

    if invalid_queue:
        raise WindowsAzureError(azure._ERROR_QUEUE_NOT_FOUND)

    #extract id, updated and name value from feed entry and set them of queue.
    for name, value in _get_entry_properties(xmlstr, True).iteritems():
        setattr(queue, name, value)

    return queue

def _convert_response_to_topic(response):
    return _convert_xml_to_topic(response.body)

def _convert_xml_to_topic(xmlstr):
    '''Converts xml response to topic

    The xml format for topic:
    <entry xmlns='http://www.w3.org/2005/Atom'>  
    <content type='application/xml'>    
    <TopicDescription xmlns:i="http://www.w3.org/2001/XMLSchema-instance" xmlns="http://schemas.microsoft.com/netservices/2010/10/servicebus/connect">
       <DefaultMessageTimeToLive>P10675199DT2H48M5.4775807S</DefaultMessageTimeToLive>
       <MaxSizeInMegaBytes>1024</MaxSizeInMegaBytes>
       <RequiresDuplicateDetection>false</RequiresDuplicateDetection>
       <DuplicateDetectionHistoryTimeWindow>P7D</DuplicateDetectionHistoryTimeWindow>
       <DeadLetteringOnFilterEvaluationExceptions>true</DeadLetteringOnFilterEvaluationExceptions>
    </TopicDescription>  
    </content>
    </entry>
    '''
    xmldoc = minidom.parseString(xmlstr)
    topic = Topic()

    invalid_topic = True
    #get node for each attribute in Topic class, if nothing found then the response is not valid xml for Topic.
    for desc in _get_children_from_path(xmldoc, 'entry', 'content', 'TopicDescription'):
        invalid_topic = True
        for attr_name, attr_value in vars(topic).iteritems():
            xml_attrs = _get_child_nodes(desc, _get_serialization_name(attr_name))
            if xml_attrs:
                xml_attr = xml_attrs[0]
                if xml_attr.firstChild:
                    setattr(topic, attr_name, 
                            xml_attr.firstChild.nodeValue)
                    invalid_topic = False

    if invalid_topic:
        raise WindowsAzureError(azure._ERROR_TOPIC_NOT_FOUND)

    #extract id, updated and name value from feed entry and set them of topic.
    for name, value in _get_entry_properties(xmlstr, True).iteritems():
        setattr(topic, name, value)
    return topic

def _convert_response_to_subscription(response):
    return _convert_xml_to_subscription(response.body)

def _convert_xml_to_subscription(xmlstr):
    '''Converts xml response to subscription

    The xml format for subscription:
    <entry xmlns='http://www.w3.org/2005/Atom'>  
    <content type='application/xml'>    
    <SubscriptionDescription xmlns:i="http://www.w3.org/2001/XMLSchema-instance" xmlns="http://schemas.microsoft.com/netservices/2010/10/servicebus/connect">
       <LockDuration>PT5M</LockDuration>
       <RequiresSession>false</RequiresSession>
       <DefaultMessageTimeToLive>P10675199DT2H48M5.4775807S</DefaultMessageTimeToLive>
       <DeadLetteringOnMessageExpiration>false</DeadLetteringOnMessageExpiration>   <DeadLetteringOnFilterEvaluationExceptions>true</DeadLetteringOnFilterEvaluationExceptions>
    </SubscriptionDescription>  
    </content>
    </entry>
    '''
    xmldoc = minidom.parseString(xmlstr)
    subscription = Subscription()

    for desc in _get_children_from_path(xmldoc, 'entry', 'content', 'subscriptiondescription'):
        for attr_name, attr_value in vars(subscription).iteritems():
            tag_name = attr_name.replace('_', '')
            xml_attrs = _get_child_nodes(desc, tag_name)
            if xml_attrs:
                xml_attr = xml_attrs[0]
                if xml_attr.firstChild:
                    setattr(subscription, attr_name, xml_attr.firstChild.nodeValue)

    for name, value in _get_entry_properties(xmlstr, True).iteritems():
        setattr(subscription, name, value)

    return subscription

def convert_subscription_to_xml(subscription):
    ''' 
    Converts a subscription object to xml to send.  The order of each field of subscription 
    in xml is very important so we cann't simple call convert_class_to_xml. 

    subscription: the subsciption object to be converted.
    '''

    subscription_body = '<SubscriptionDescription xmlns:i="http://www.w3.org/2001/XMLSchema-instance" xmlns="http://schemas.microsoft.com/netservices/2010/10/servicebus/connect">'
    if subscription:
        if subscription.lock_duration:
            subscription_body += ''.join(['<LockDuration>', subscription.lock_duration, '</LockDuration>'])
        if subscription.requires_session:
            subscription_body += ''.join(['<RequiresSession>', subscription.requires_session, '</RequiresSession>'])    
        if subscription.default_message_time_to_live:
            subscription_body += ''.join(['<DefaultMessageTimeToLive>', subscription.default_message_time_to_live, '</DefaultMessageTimeToLive>'])
        if subscription.dead_lettering_on_message_expiration:
            subscription_body += ''.join(['<DeadLetteringOnMessageExpiration>', subscription.dead_lettering_on_message_expiration, '</DeadLetteringOnMessageExpiration>'])    
        if subscription.dead_lettering_on_filter_evaluation_exceptions:
            subscription_body += ''.join(['<DeadLetteringOnFilterEvaluationExceptions>', subscription.dead_lettering_on_filter_evaluation_exceptions, '</DeadLetteringOnFilterEvaluationExceptions>'])    
        if subscription.enable_batched_operations:
            subscription_body += ''.join(['<EnableBatchedOperations>', subscription.enable_batched_operations, '</EnableBatchedOperations>'])    
        if subscription.max_delivery_count:
            subscription_body += ''.join(['<MaxDeliveryCount>', subscription.max_delivery_count, '</MaxDeliveryCount>'])
        if subscription.message_count:
            subscription_body += ''.join(['<MessageCount>', subscription.message_count, '</MessageCount>'])  
         
    subscription_body += '</SubscriptionDescription>'    
    return _create_entry(subscription_body)

def convert_rule_to_xml(rule):
    ''' 
    Converts a rule object to xml to send.  The order of each field of rule 
    in xml is very important so we cann't simple call convert_class_to_xml. 

    rule: the rule object to be converted.
    '''
    rule_body = '<RuleDescription xmlns:i="http://www.w3.org/2001/XMLSchema-instance" xmlns="http://schemas.microsoft.com/netservices/2010/10/servicebus/connect">'
    if rule:
        if rule.filter_type:
            rule_body += ''.join(['<Filter i:type="', _html_encode(rule.filter_type), '">'])
            if rule.filter_type == 'CorrelationFilter':
                rule_body += ''.join(['<CorrelationId>', _html_encode(rule.filter_expression), '</CorrelationId>'])
            else:
                rule_body += ''.join(['<SqlExpression>', _html_encode(rule.filter_expression), '</SqlExpression>'])
                rule_body += '<CompatibilityLevel>20</CompatibilityLevel>'
            rule_body += '</Filter>'
        if rule.action_type:
            rule_body += ''.join(['<Action i:type="', _html_encode(rule.action_type), '">'])
            if rule.action_type == 'SqlFilterAction':
                rule_body += ''.join(['<SqlExpression>', _html_encode(rule.action_expression), '</SqlExpression>'])
            rule_body += '</Action>'
    rule_body += '</RuleDescription>'    

    return _create_entry(rule_body)

def convert_topic_to_xml(topic):    
    ''' 
    Converts a topic object to xml to send.  The order of each field of topic 
    in xml is very important so we cann't simple call convert_class_to_xml. 

    topic: the topic object to be converted.
    '''

    topic_body = '<TopicDescription xmlns:i="http://www.w3.org/2001/XMLSchema-instance" xmlns="http://schemas.microsoft.com/netservices/2010/10/servicebus/connect">'
    if topic:
        if topic.default_message_time_to_live:
            topic_body += ''.join(['<DefaultMessageTimeToLive>', topic.default_message_time_to_live, '</DefaultMessageTimeToLive>'])
        if topic.max_size_in_mega_bytes:
            topic_body += ''.join(['<MaxSizeInMegabytes>', topic.default_message_time_to_live, '</MaxSizeInMegabytes>'])
        if topic.requires_duplicate_detection:
            topic_body += ''.join(['<RequiresDuplicateDetection>', topic.default_message_time_to_live, '</RequiresDuplicateDetection>'])
        if topic.duplicate_detection_history_time_window:
            topic_body += ''.join(['<DuplicateDetectionHistoryTimeWindow>', topic.default_message_time_to_live, '</DuplicateDetectionHistoryTimeWindow>'])    
        if topic.enable_batched_operations:
            topic_body += ''.join(['<EnableBatchedOperations>', topic.default_message_time_to_live, '</EnableBatchedOperations>'])
        if topic.size_in_bytes:
            topic_body += ''.join(['<SizeinBytes>', topic.default_message_time_to_live, '</SizeinBytes>'])    
    topic_body += '</TopicDescription>'

    return _create_entry(topic_body)

def convert_queue_to_xml(queue):
    ''' 
    Converts a queue object to xml to send.  The order of each field of queue 
    in xml is very important so we cann't simple call convert_class_to_xml. 

    queue: the queue object to be converted.
    '''
    queue_body = '<QueueDescription xmlns:i="http://www.w3.org/2001/XMLSchema-instance" xmlns="http://schemas.microsoft.com/netservices/2010/10/servicebus/connect">'
    if queue:
        if queue.lock_duration:
            queue_body += ''.join(['<LockDuration>', queue.lock_duration, '</LockDuration>'])
        if queue.max_size_in_megabytes:
            queue_body += ''.join(['<MaxSizeInMegabytes>', queue.max_size_in_megabytes, '</MaxSizeInMegabytes>'])
        if queue.requires_duplicate_detection:
            queue_body += ''.join(['<RequiresDuplicateDetection>', queue.requires_duplicate_detection, '</RequiresDuplicateDetection>'])
        if queue.requires_session:
            queue_body += ''.join(['<RequiresSession>', queue.requires_session, '</RequiresSession>'])    
        if queue.default_message_time_to_live:
            queue_body += ''.join(['<DefaultMessageTimeToLive>', queue.default_message_time_to_live, '</DefaultMessageTimeToLive>'])
        if queue.enable_dead_lettering_on_message_expiration:
            queue_body += ''.join(['<EnableDeadLetteringOnMessageExpiration>', queue.enable_dead_lettering_on_message_expiration, '</EnableDeadLetteringOnMessageExpiration>'])    
        if queue.duplicate_detection_history_time_window:
            queue_body += ''.join(['<DuplicateDetectionHistoryTimeWindow>', queue.duplicate_detection_history_time_window, '</DuplicateDetectionHistoryTimeWindow>'])    
        if queue.max_delivery_count:
            queue_body += ''.join(['<MaxDeliveryCount>', queue.max_delivery_count, '</MaxDeliveryCount>'])
        if queue.enable_batched_operations:
            queue_body += ''.join(['<EnableBatchedOperations>', queue.enable_batched_operations, '</EnableBatchedOperations>'])    
        if queue.size_in_bytes:
            queue_body += ''.join(['<SizeinBytes>', queue.size_in_bytes, '</SizeinBytes>'])
        if queue.message_count:
            queue_body += ''.join(['<MessageCount>', queue.message_count, '</MessageCount>'])  
         
    queue_body += '</QueueDescription>'
    return _create_entry(queue_body)

def _service_bus_error_handler(http_error):
    ''' Simple error handler for service bus service. Will add more specific cases '''

    if http_error.status == 409:
        raise WindowsAzureConflictError(azure._ERROR_CONFLICT)
    elif http_error.status == 404:
        raise WindowsAzureMissingResourceError(azure._ERROR_NOT_FOUND)
    else:
        raise WindowsAzureError(azure._ERROR_UNKNOWN % http_error.message)

from azure.servicebus.servicebusservice import ServiceBusService
