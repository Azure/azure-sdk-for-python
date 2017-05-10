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
import sys
import time
import urllib2
from xml.dom import minidom
import ast
import httplib
from datetime import datetime


from windowsazure import (WindowsAzureError, remove_xmltag_namespace, WindowsAzureData, 
                          create_entry, normalize_xml, get_entry_properties, html_encode,
                          HTTPError)

DEFAULT_RULE_NAME='$Default'
AZURE_SERVICEBUS_NAMESPACE = 'AZURE_SERVICEBUS_NAMESPACE'
AZURE_SERVICEBUS_ACCESS_KEY = 'AZURE_SERVICEBUS_ACCESS_KEY'
AZURE_SERVICEBUS_ISSUER = 'AZURE_SERVICEBUS_ISSUER'

class Queue(WindowsAzureData):
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
    def __init__(self):
        self.default_message_time_to_live = ''
        self.max_size_in_mega_bytes = ''
        self.requires_duplicate_detection = ''
        self.duplicate_detection_history_time_window = ''
        self.enable_batched_operations = ''
        self.size_in_bytes = ''

class Subscription(WindowsAzureData):
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
    def __init__(self):
        self.filter_type = ''
        self.filter_expression = ''
        self.action_type = ''
        self.action_expression = ''

class Message(WindowsAzureData):
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
        if self._queue_name:
            self.service_bus_service.delete_queue_message(self._queue_name, self.broker_properties['SequenceNumber'], self.broker_properties['LockToken'])
        elif self._topic_name and self._subscription_name:
            self.service_bus_service.delete_subscription_message(self._topic_name, self._subscription_name, self.broker_properties['SequenceNumber'], self.broker_properties['LockToken'])
        else:
            raise WindowsAzureError('Message is not peek locked and cannot be deleted.')

    def unlock(self):
        if self._queue_name:
            self.service_bus_service.unlock_queue_message(self._queue_name, self.broker_properties['SequenceNumber'], self.broker_properties['LockToken'])
        elif self._topic_name and self._subscription_name:
            self.service_bus_service.unlock_subscription_message(self._topic_name, self._subscription_name, self.broker_properties['SequenceNumber'], self.broker_properties['LockToken'])
        else:
            raise WindowsAzureError('Message is not peek locked and cannot be unlocked.')

    def add_headers(self, request):
        if self.custom_properties:
            for name, value in self.custom_properties.iteritems():
                if isinstance(value, str):
                    request.header.append((name, '"' + str(value) + '"'))
                elif isinstance(value, datetime):
                    request.header.append((name, '"' + value.strftime('%a, %d %b %Y %H:%M:%S GMT') + '"'))
                else:
                    request.header.append((name, str(value)))
        request.header.append(('Content-Type', self.type))
        if self.broker_properties:
            request.header.append(('BrokerProperties', str(self.broker_properties)))
        return request.header       

def _update_service_bus_header(request, account_key, issuer): 
    if request.method in ['PUT', 'POST', 'MERGE', 'DELETE']:
        request.header.append(('Content-Length', str(len(request.body))))              
    if not request.method in ['GET', 'HEAD']:
        for name, value in request.header:
            if 'content-type' == name.lower():
                break
        else:
            request.header.append(('Content-Type', 'application/atom+xml;type=entry;charset=utf-8')) 
    request.header.append(('Authorization', _sign_service_bus_request(request, account_key, issuer)))
    return request.header

_tokens = {}

def _sign_service_bus_request(request, account_key, issuer):
        return 'WRAP access_token="' + _get_token(request, account_key, issuer) + '"'

def _token_is_expired(token):
        time_pos_begin = token.find('ExpiresOn=') + len('ExpiresOn=')
        time_pos_end = token.find('&', time_pos_begin)
        token_expire_time = int(token[time_pos_begin:time_pos_end])
        time_now = time.mktime(time.localtime())
        return (token_expire_time - time_now) < 30

def _get_token(request, account_key, issuer):     
    wrap_scope = 'http://' + request.host + request.uri
        
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
        import windowsazure.http.winhttp
        connection = windowsazure.http.winhttp._HTTPConnection(host, protocol='https')
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

def _create_message(service_instance, respbody):
    custom_properties = {}
    broker_properties = None
    message_type = None
    message_location = None
    for name, value in service_instance.respheader:
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
def convert_xml_to_rule(xmlstr):
    xmlstr = normalize_xml(xmlstr)
    xmlstr = remove_xmltag_namespace(xmlstr, to_lower=True)
    xmldoc = minidom.parseString(xmlstr)
    rule = Rule()
        
    xml_filters = xmldoc.getElementsByTagName('filter')
    if xml_filters:
        xml_filter = xml_filters[0]
        filter_type = xml_filter.getAttribute('type')
        setattr(rule, 'filter_type', str(filter_type))
        if xml_filter.childNodes:
            filter_expression = xml_filter.childNodes[0].firstChild
            if filter_expression:
                setattr(rule, 'filter_expression', filter_expression.nodeValue)
    
    xml_actions = xmldoc.getElementsByTagName('action')
    if xml_actions:
        xml_action = xml_actions[0]
        action_type = xml_action.getAttribute('type')
        setattr(rule, 'action_type', str(action_type))
        if xml_action.childNodes:
            action_expression = xml_action.childNodes[0].firstChild
            if action_expression:
                setattr(rule, 'filter_expression', action_expression.nodeValue)
   
    for name, value in get_entry_properties(xmlstr, ['id', 'updated', 'name']).iteritems():
        setattr(rule, name, value)

    return rule

def convert_xml_to_queue(xmlstr):
    xmlstr = normalize_xml(xmlstr)
    xmlstr = remove_xmltag_namespace(xmlstr, to_lower=True)
    xmldoc = minidom.parseString(xmlstr)
    queue = Queue()

    invalid_queue = True
    for attr_name, attr_value in vars(queue).iteritems():
        tag_name = attr_name.replace('_', '')
        xml_attrs = xmldoc.getElementsByTagName(tag_name)
        if xml_attrs:
            xml_attr = xml_attrs[0]
            if xml_attr.firstChild:
                setattr(queue, attr_name, xml_attr.firstChild.nodeValue)
                invalid_queue = False

    if invalid_queue:
        raise WindowsAzureError('Queue is not Found')

    for name, value in get_entry_properties(xmlstr, ['id', 'updated', 'name']).iteritems():
        setattr(queue, name, value)

    return queue

def convert_xml_to_topic(xmlstr):
    xmlstr = normalize_xml(xmlstr)
    xmlstr = remove_xmltag_namespace(xmlstr, to_lower=True)
    xmldoc = minidom.parseString(xmlstr)
    topic = Topic()

    invalid_topic = True
    for attr_name, attr_value in vars(topic).iteritems():
        tag_name = attr_name.replace('_', '')
        xml_attrs = xmldoc.getElementsByTagName(tag_name)
        if xml_attrs:
            xml_attr = xml_attrs[0]
            if xml_attr.firstChild:
                setattr(topic, attr_name, xml_attr.firstChild.nodeValue)
                invalid_topic = False

    if invalid_topic:
        raise WindowsAzureError('Topic is not Found')

    for name, value in get_entry_properties(xmlstr, ['id', 'updated', 'name']).iteritems():
        setattr(topic, name, value)
    return topic

def convert_xml_to_subscription(xmlstr):
    xmlstr = normalize_xml(xmlstr)
    xmlstr = remove_xmltag_namespace(xmlstr, to_lower=True)
    xmldoc = minidom.parseString(xmlstr)
    subscription = Subscription()
    for attr_name, attr_value in vars(subscription).iteritems():
        tag_name = attr_name.replace('_', '')
        xml_attrs = xmldoc.getElementsByTagName(tag_name)
        if xml_attrs:
            xml_attr = xml_attrs[0]
            if xml_attr.firstChild:
                setattr(subscription, attr_name, xml_attr.firstChild.nodeValue)
    for name, value in get_entry_properties(xmlstr, ['id', 'updated', 'name']).iteritems():
        setattr(subscription, name, value)
    return subscription

def convert_subscription_to_xml(subscription):
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
    return create_entry(subscription_body)

def convert_rule_to_xml(rule):
    rule_body = '<RuleDescription xmlns:i="http://www.w3.org/2001/XMLSchema-instance" xmlns="http://schemas.microsoft.com/netservices/2010/10/servicebus/connect">'
    if rule:
        if rule.filter_type:
            rule_body += ''.join(['<Filter i:type="', html_encode(rule.filter_type), '">'])
            if rule.filter_type == 'CorrelationFilter':
                rule_body += ''.join(['<CorrelationId>', html_encode(rule.filter_expression), '</CorrelationId>'])
            else:
                rule_body += ''.join(['<SqlExpression>', html_encode(rule.filter_expression), '</SqlExpression>'])
                rule_body += '<CompatibilityLevel>20</CompatibilityLevel>'
            rule_body += '</Filter>'
        if rule.action_type:
            rule_body += ''.join(['<Action i:type="', html_encode(rule.action_type), '">'])
            if rule.action_type == 'SqlFilterAction':
                rule_body += ''.join(['<SqlExpression>', html_encode(rule.action_expression), '</SqlExpression>'])
            rule_body += '</Action>'
    rule_body += '</RuleDescription>'    

    return create_entry(rule_body)

def convert_topic_to_xml(topic):    
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

    return create_entry(topic_body)

def convert_queue_to_xml(queue):
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
    return create_entry(queue_body)

def _service_bus_error_handler(http_error):
    if http_error.status == 409:
        raise WindowsAzureError('Conflict')
    elif http_error.status == 404:
        raise WindowsAzureError('Not Found')
    else:
        raise WindowsAzureError('Unknown Error')

from windowsazure.servicebus.servicebusservice import ServiceBusService

