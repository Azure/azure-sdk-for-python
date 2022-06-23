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

@pytest.mark.skip
def test_message_pickle():
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
    
    pickle_list = []
    pickle_list.append(message)

    # pickled = pickle.loads(pickle.dumps(pickle_list))
    # assert list(message.get_data()) == [b"test"]
    # assert message.footer == pickled.footer
    # assert message.state == pickled.state
    # assert message.application_properties == pickled.application_properties
    # assert message.annotations == pickled.annotations
    # assert message.delivery_annotations == pickled.delivery_annotations
    # assert message.settled == pickled.settled
    # assert message.properties.message_id == pickled.properties.message_id
    # assert message.properties.user_id == pickled.properties.user_id
    # assert message.properties.to == pickled.properties.to
    # assert message.properties.subject == pickled.properties.subject
    # assert message.properties.reply_to == pickled.properties.reply_to
    # assert message.properties.correlation_id == pickled.properties.correlation_id
    # assert message.properties.content_type == pickled.properties.content_type
    # assert message.properties.content_encoding == pickled.properties.content_encoding
    # assert message.properties.absolute_expiry_time == pickled.properties.absolute_expiry_time
    # assert message.properties.creation_time == pickled.properties.creation_time
    # assert message.properties.group_id == pickled.properties.group_id
    # assert message.properties.group_sequence == pickled.properties.group_sequence
    # assert message.properties.reply_to_group_id == pickled.properties.reply_to_group_id
    # assert message.header.delivery_count == pickled.header.delivery_count
    # assert message.header.time_to_live == pickled.header.time_to_live
    # assert message.header.first_acquirer == pickled.header.first_acquirer
    # assert message.header.durable == pickled.header.durable
    # assert message.header.priority == pickled.header.priority

    # send with message param
    # settler = errors.MessageAlreadySettled
    internal_message = Message()
    internal_message._replace(data=b"hi")
    message_w_message_param = Message(
        internal_message,
    )
    pickled = pickle.loads(pickle.dumps(message_w_message_param))
    message_data = str(message_w_message_param.get_data())
    pickled_data = str(pickled.get_data())

    assert message_data == pickled_data
    assert message_w_message_param.footer == pickled.footer
    # assert message_w_message_param.state == pickled.state
    assert message_w_message_param.application_properties == pickled.application_properties
    assert message_w_message_param.annotations == pickled.annotations
    assert message_w_message_param.delivery_annotations == pickled.delivery_annotations
    assert pickled.delivery_no == 1

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

@pytest.mark.skip
def test_message_auto_body_type():
    single_data = b'!@#$%^&*()_+1234567890'
    single_data_message = Message(body=single_data)
    check_list = [data for data in single_data_message.get_data()]
    assert isinstance(single_data_message._body, DataBody)
    assert len(check_list) == 1
    assert check_list[0] == single_data
    assert(str(single_data_message))

    multiple_data = [b'!@#$%^&*()_+1234567890', 'abcdefg~123']
    multiple_data_message = Message(body=multiple_data)
    check_list = [data for data in multiple_data_message.get_data()]
    assert isinstance(multiple_data_message._body, DataBody)
    assert len(check_list) == 2
    assert check_list[0] == multiple_data[0]
    assert check_list[1] == multiple_data[1].encode("UTF-8")
    assert (str(multiple_data_message))

    list_mixed_body = [b'!@#$%^&*()_+1234567890', 'abcdefg~123', False, 1.23]
    list_mixed_body_message = Message(body=list_mixed_body)
    check_data = list_mixed_body_message.get_data()
    assert isinstance(list_mixed_body_message._body, ValueBody)
    assert isinstance(check_data, list)
    assert len(check_data) == 4
    assert check_data[0] == list_mixed_body[0]
    assert check_data[1] == list_mixed_body[1].encode("UTF-8")
    assert check_data[2] == list_mixed_body[2]
    assert check_data[3] == list_mixed_body[3]
    assert (str(list_mixed_body_message))

    dic_mixed_body = {b'key1': b'value', b'key2': False, b'key3': -1.23}
    dic_mixed_body_message = Message(body=dic_mixed_body)
    check_data = dic_mixed_body_message.get_data()
    assert isinstance(dic_mixed_body_message._body, ValueBody)
    assert isinstance(check_data, dict)
    assert len(check_data) == 3
    assert check_data == dic_mixed_body
    assert (str(dic_mixed_body_message))


@pytest.mark.skip
def test_message_body_data_type():
    single_data = b'!@#$%^&*()_+1234567890'
    single_data_message = Message(body=single_data, body_type=MessageBodyType.Data)
    check_list = [data for data in single_data_message.get_data()]
    assert isinstance(single_data_message._body, DataBody)
    assert len(check_list) == 1
    assert check_list[0] == single_data
    assert str(single_data_message)

    multiple_data = [b'!@#$%^&*()_+1234567890', 'abcdefg~123',]
    multiple_data_message = Message(body=multiple_data, body_type=MessageBodyType.Data)
    check_list = [data for data in multiple_data_message.get_data()]
    assert isinstance(multiple_data_message._body, DataBody)
    assert len(check_list) == 2
    assert check_list[0] == multiple_data[0]
    assert check_list[1] == multiple_data[1].encode("UTF-8")
    assert str(multiple_data_message)

    with pytest.raises(TypeError):
        Message(body={"key": "value"}, body_type=MessageBodyType.Data)

    with pytest.raises(TypeError):
        Message(body=1, body_type=MessageBodyType.Data)

    with pytest.raises(TypeError):
        Message(body=['abc', True], body_type=MessageBodyType.Data)

    with pytest.raises(TypeError):
        Message(body=True, body_type=MessageBodyType.Data)

@pytest.mark.skip
def test_message_body_value_type():
    string_value = b'!@#$%^&*()_+1234567890'
    string_value_message = Message(body=string_value, body_type=MessageBodyType.Value)
    assert string_value_message.get_data() == string_value
    assert isinstance(string_value_message._body, ValueBody)
    assert str(string_value_message)

    float_value = 1.23
    float_value_message = Message(body=float_value, body_type=MessageBodyType.Value)
    assert float_value_message.get_data() == float_value
    assert isinstance(string_value_message._body, ValueBody)
    assert str(float_value_message)

    dict_value = {b"key1 ": b"value1", b'key2': -1, b'key3': False}
    dict_value_message = Message(body=dict_value, body_type=MessageBodyType.Value)
    assert dict_value_message.get_data() == dict_value
    assert isinstance(string_value_message._body, ValueBody)
    assert str(dict_value_message)

    compound_list_value = [1, b'abc', True, [1.23, b'abc', False], {b"key1 ": b"value1", b'key2': -1}]
    compound_list_value_message = Message(body=compound_list_value, body_type=MessageBodyType.Value)
    assert compound_list_value_message.get_data() == compound_list_value
    assert isinstance(string_value_message._body, ValueBody)
    assert str(compound_list_value_message)

@pytest.mark.skip
def test_message_body_sequence_type():

    single_list = [1, 2, b'aa', b'bb', True, b"abc", {b"key1": b"value", b"key2": -1.23}]
    single_list_message = Message(body=single_list, body_type=MessageBodyType.Sequence)
    check_list = [data for data in single_list_message.get_data()]
    assert isinstance(single_list_message._body, SequenceBody)
    assert len(check_list) == 1
    assert check_list[0] == single_list
    assert str(single_list_message)

    multiple_lists = [[1, 2, 3, 4], [b'aa', b'bb', b'cc', b'dd']]
    multiple_lists_message = Message(body=multiple_lists, body_type=MessageBodyType.Sequence)
    check_list = [data for data in multiple_lists_message.get_data()]
    assert isinstance(multiple_lists_message._body, SequenceBody)
    assert len(check_list) == 2
    assert check_list[0] == multiple_lists[0]
    assert check_list[1] == multiple_lists[1]
    assert str(multiple_lists_message)

    with pytest.raises(TypeError):
        Message(body={"key": "value"}, body_type=MessageBodyType.Sequence)

    with pytest.raises(TypeError):
        Message(body=1, body_type=MessageBodyType.Sequence)

    with pytest.raises(TypeError):
        Message(body='a', body_type=MessageBodyType.Sequence)

    with pytest.raises(TypeError):
        Message(body=True, body_type=MessageBodyType.Sequence)