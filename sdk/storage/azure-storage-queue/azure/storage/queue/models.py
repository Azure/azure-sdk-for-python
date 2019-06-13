# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
# pylint: disable=too-few-public-methods, too-many-instance-attributes

from ._generated.models import StorageServiceProperties
from ._generated.models import StorageErrorException


class SignedIdentifier(object):
    '''
    Signed Identifier class used by the set and get acl methods in each service.
    A stored access policy can specify the start time, expiry time, and 
    permissions for the Shared Access Signatures with which it's associated. 
    Depending on how you want to control access to your resource, you can
    specify all of these parameters within the stored access policy, and omit 
    them from the URL for the Shared Access Signature. Doing so permits you to 
    modify the associated signature's behavior at any time, as well as to revoke 
    it. Or you can specify one or more of the access policy parameters within 
    the stored access policy, and the others on the URL. Finally, you can 
    specify all of the parameters on the URL. In this case, you can use the 
    stored access policy to revoke the signature, but not to modify its behavior.
    Together the Shared Access Signature and the stored access policy must 
    include all fields required to authenticate the signature. If any required 
    fields are missing, the request will fail. Likewise, if a field is specified 
    both in the Shared Access Signature URL and in the stored access policy, the 
    request will fail with status code 400 (Bad Request).
    '''

    def __init__(self, id=None, permission=None, expiry=None, start=None):
        '''
        :param str permission:
            The permissions associated with the shared access signature. The 
            user is restricted to operations allowed by the permissions. 
            Required unless an id is given referencing a stored access policy 
            which contains this field. This field must be omitted if it has been 
            specified in an associated stored access policy.
        :param expiry:
            The time at which the shared access signature becomes invalid. 
            Required unless an id is given referencing a stored access policy 
            which contains this field. This field must be omitted if it has 
            been specified in an associated stored access policy. Azure will always 
            convert values to UTC. If a date is passed in without timezone info, it 
            is assumed to be UTC.
        :type expiry: datetime or str
        :param start:
            The time at which the shared access signature becomes valid. If 
            omitted, start time for this call is assumed to be the time when the 
            storage service receives the request. Azure will always convert values 
            to UTC. If a date is passed in without timezone info, it is assumed to 
            be UTC.
        :type start: datetime or str
        '''
        self.id = id
        self.start = start
        self.expiry = expiry
        self.permission = permission


class QueueMessage(object):
    ''' 
    Queue message class. 
    :param str id: 
        A GUID value assigned to the message by the Queue service that 
        identifies the message in the queue. This value may be used together 
        with the value of pop_receipt to delete a message from the queue after 
        it has been retrieved with the get messages operation. 
    :param date insertion_time: 
        A UTC date value representing the time the messages was inserted.
    :param date expiration_time: 
        A UTC date value representing the time the message expires.
    :param int dequeue_count: 
        Begins with a value of 1 the first time the message is dequeued. This 
        value is incremented each time the message is subsequently dequeued.
    :param obj content: 
        The message content. Type is determined by the decode_function set on 
        the service. Default is str.
    :param str pop_receipt: 
        A receipt str which can be used together with the message_id element to 
        delete a message from the queue after it has been retrieved with the get 
        messages operation. Only returned by get messages operations. Set to 
        None for peek messages.
    :param date time_next_visible: 
        A UTC date value representing the time the message will next be visible. 
        Only returned by get messages operations. Set to None for peek messages.
    '''

    def __init__(self, content=None):
        self.id = None
        self.insertion_time = None
        self.expiration_time = None
        self.dequeue_count = None
        self.content = content
        self.pop_receipt = None
        self.time_next_visible = None

class QueueMessageFormat:
    ''' 
    Encoding and decoding methods which can be used to modify how the queue service 
    encodes and decodes queue messages. Set these to queueservice.encode_function 
    and queueservice.decode_function to modify the behavior. The defaults are 
    text_xmlencode and text_xmldecode, respectively.
    '''

    @staticmethod
    def text_base64encode(data):
        '''
        Base64 encode unicode text.
        
        :param str data: String to encode.
        :return: Base64 encoded string.
        :rtype: str
        '''
        _validate_message_type_text(data)
        return b64encode(data.encode('utf-8')).decode('utf-8')

    @staticmethod
    def text_base64decode(data):
        '''
        Base64 decode to unicode text.
        
        :param str data: String data to decode to unicode.
        :return: Base64 decoded string.
        :rtype: str
        '''
        try:
            return b64decode(data.encode('utf-8')).decode('utf-8')
        except (ValueError, TypeError):
            # ValueError for Python 3, TypeError for Python 2
            raise ValueError(_ERROR_MESSAGE_NOT_BASE64)

    @staticmethod
    def binary_base64encode(data):
        '''
        Base64 encode byte strings.
        
        :param str data: Binary string to encode.
        :return: Base64 encoded data.
        :rtype: str
        '''
        _validate_message_type_bytes(data)
        return b64encode(data).decode('utf-8')

    @staticmethod
    def binary_base64decode(data):
        '''
        Base64 decode to byte string.
        
        :param str data: Data to decode to a byte string.
        :return: Base64 decoded data.
        :rtype: str
        '''
        try:
            return b64decode(data.encode('utf-8'))
        except (ValueError, TypeError):
            # ValueError for Python 3, TypeError for Python 2
            raise ValueError(_ERROR_MESSAGE_NOT_BASE64)

    @staticmethod
    def text_xmlencode(data):
        ''' 
        XML encode unicode text.
        :param str data: Unicode string to encode
        :return: XML encoded data.
        :rtype: str
        '''
        _validate_message_type_text(data)
        return xml_escape(data)

    @staticmethod
    def text_xmldecode(data):
        ''' 
        XML decode to unicode text.
        :param str data: Data to decode to unicode.
        :return: XML decoded data.
        :rtype: str
        '''
        return xml_unescape(data)

    @staticmethod
    def noencode(data):
        ''' 
        Do no encoding. 
        :param str data: Data.
        :return: The data passed in is returned unmodified.
        :rtype: str
        '''
        return data

    @staticmethod
    def nodecode(data):
        '''
        Do no decoding.
        
        :param str data: Data.
        :return: The data passed in is returned unmodified.
        :rtype: str        
        '''
        return data


class QueuePermissions(object):
    '''
    QueuePermissions class to be used with :func:`~azure.storage.queue.queueservice.QueueService.generate_queue_shared_access_signature`
    method and for the AccessPolicies used with :func:`~azure.storage.queue.queueservice.QueueService.set_queue_acl`. 
    :ivar QueuePermissions QueuePermissions.READ: 
        Read metadata and properties, including message count. Peek at messages. 
    :ivar QueuePermissions QueuePermissions.ADD: 
        Add messages to the queue.
    :ivar QueuePermissions QueuePermissions.UPDATE:
        Update messages in the queue. Note: Use the Process permission with 
        Update so you can first get the message you want to update.
    :ivar QueuePermissions QueuePermissions.PROCESS: Delete entities.
        Get and delete messages from the queue. 
    '''

    def __init__(self, read=False, add=False, update=False, process=False, _str=None):
        '''
        :param bool read:
            Read metadata and properties, including message count. Peek at messages.
        :param bool add:
            Add messages to the queue.
        :param bool update:
            Update messages in the queue. Note: Use the Process permission with 
            Update so you can first get the message you want to update.
        :param bool process: 
            Get and delete messages from the queue.
        :param str _str: 
            A string representing the permissions.
        '''
        if not _str:
            _str = ''
        self.read = read or ('r' in _str)
        self.add = add or ('a' in _str)
        self.update = update or ('u' in _str)
        self.process = process or ('p' in _str)

    def __or__(self, other):
        return QueuePermissions(_str=str(self) + str(other))

    def __add__(self, other):
        return QueuePermissions(_str=str(self) + str(other))

    def __str__(self):
        return (('r' if self.read else '') +
                ('a' if self.add else '') +
                ('u' if self.update else '') +
                ('p' if self.process else ''))


QueuePermissions.READ = QueuePermissions(read=True)
QueuePermissions.ADD = QueuePermissions(add=True)
QueuePermissions.UPDATE = QueuePermissions(update=True)
QueuePermissions.PROCESS = QueuePermissions(process=True)
