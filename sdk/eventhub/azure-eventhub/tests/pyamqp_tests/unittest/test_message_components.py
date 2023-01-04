#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------
import copy
import pickle
import pytest

from azure.eventhub._pyamqp.message import (
    Properties,
    Header,
    BatchMessage,
    Message
)

def test_message_properties():

    properties = Properties()
    assert properties.user_id is None

    properties = Properties()
    properties = properties._replace(user_id=b'')
    assert properties.user_id == b''

    properties = Properties()
    properties = properties._replace(user_id=b'1')
    assert properties.user_id == b'1'

    properties = Properties()
    properties = properties._replace(user_id=b'short')
    assert properties.user_id == b'short'

    properties = Properties()
    properties = properties._replace(user_id=b'longuseridstring')
    assert properties.user_id == b'longuseridstring'

    properties = Properties()
    properties = properties._replace(user_id=b'!@#$%^&*()_+1234567890')
    assert properties.user_id == b'!@#$%^&*()_+1234567890'

    properties = Properties()
    properties = properties._replace(user_id=b'werid/0\0\1\t\n')
    assert properties.user_id == b'werid/0\0\1\t\n'

def test_deepcopy_batch_message():
    ## DEEPCOPY WITH MESSAGES IN BATCH THAT HAVE HEADER/PROPERTIES
    properties = Properties()
    properties = properties._replace(message_id = '2')
    properties = properties._replace(user_id = '1')
    properties = properties._replace(to = 'dkfj')
    properties = properties._replace(subject = 'dsljv')
    properties = properties._replace(reply_to = "kdjfk")
    properties = properties._replace(correlation_id = 'ienag')
    properties = properties._replace(content_type = 'b')
    properties = properties._replace(content_encoding = '39ru')
    properties = properties._replace(absolute_expiry_time = 24)
    properties = properties._replace(creation_time = 10)
    properties = properties._replace(group_id = '3irow')
    properties = properties._replace(group_sequence = 39)
    properties = properties._replace(reply_to_group_id = '39rud')

    header = Header()
    header = header._replace(delivery_count = 3)
    header = header._replace(ttl = 5)
    header = header._replace(first_acquirer = 'dkfj')
    header = header._replace(durable = True)
    header = header._replace(priority = 4)

    message = Message(value="test", properties=properties, header=header)
    message = message._replace(footer = {'a':2})
    # message = message._replace(state = constants.MessageState.ReceivedSettled)

    message_batch = BatchMessage(message)
    message_batch_copy = copy.deepcopy(message_batch)
    batch_message = list(message_batch)[0]
    batch_copy_message = list(message_batch_copy)[0]
    assert len(list(message_batch)) == len(list(message_batch_copy))

    # check message attributes are equal to deepcopied message attributes
    assert batch_message.footer == batch_copy_message.footer
    assert batch_message.application_properties == batch_copy_message.application_properties
    assert batch_message.delivery_annotations == batch_copy_message.delivery_annotations
    # assert batch_message.settled == batch_copy_message.settled
    assert batch_message.properties.message_id == batch_copy_message.properties.message_id
    assert batch_message.properties.user_id == batch_copy_message.properties.user_id
    assert batch_message.properties.to == batch_copy_message.properties.to
    assert batch_message.properties.subject == batch_copy_message.properties.subject
    assert batch_message.properties.reply_to == batch_copy_message.properties.reply_to
    assert batch_message.properties.correlation_id == batch_copy_message.properties.correlation_id
    assert batch_message.properties.content_type == batch_copy_message.properties.content_type
    assert batch_message.properties.content_encoding == batch_copy_message.properties.content_encoding
    assert batch_message.properties.absolute_expiry_time == batch_copy_message.properties.absolute_expiry_time
    assert batch_message.properties.creation_time == batch_copy_message.properties.creation_time
    assert batch_message.properties.group_id == batch_copy_message.properties.group_id
    assert batch_message.properties.group_sequence == batch_copy_message.properties.group_sequence
    assert batch_message.properties.reply_to_group_id == batch_copy_message.properties.reply_to_group_id
    assert batch_message.header.delivery_count == batch_copy_message.header.delivery_count
    assert batch_message.header.ttl == batch_copy_message.header.ttl
    assert batch_message.header.first_acquirer == batch_copy_message.header.first_acquirer
    assert batch_message.header.durable == batch_copy_message.header.durable
    assert batch_message.header.priority == batch_copy_message.header.priority

def test_message_auto_body_type():
    single_data = b'!@#$%^&*()_+1234567890'
    single_data_message = Message(data=single_data)
    check_list = [data for data in single_data_message.data]
    assert len(check_list) == 22
    assert(str(single_data_message))

    multiple_data = [b'!@#$%^&*()_+1234567890', 'abcdefg~123']
    multiple_data_message = Message(data=multiple_data)
    check_list = [data for data in multiple_data_message.data]
    assert len(check_list) == 2
    assert check_list[0] == multiple_data[0]
    assert check_list[1] == multiple_data[1]
    assert (str(multiple_data_message))

    list_mixed_body = [b'!@#$%^&*()_+1234567890', 'abcdefg~123', False, 1.23]
    list_mixed_body_message = Message(data=list_mixed_body)
    check_data = list_mixed_body_message.data
    assert isinstance(check_data, list)
    assert len(check_data) == 4
    assert check_data[0] == list_mixed_body[0]
    assert check_data[1] == list_mixed_body[1]
    assert check_data[2] == list_mixed_body[2]
    assert check_data[3] == list_mixed_body[3]
    assert (str(list_mixed_body_message))

    dic_mixed_body = {b'key1': b'value', b'key2': False, b'key3': -1.23}
    dic_mixed_body_message = Message(data=dic_mixed_body)
    check_data = dic_mixed_body_message.data
    assert isinstance(check_data, dict)
    assert len(check_data) == 3
    assert check_data == dic_mixed_body
    assert (str(dic_mixed_body_message))
