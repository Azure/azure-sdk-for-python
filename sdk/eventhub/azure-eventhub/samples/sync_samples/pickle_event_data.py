import pickle
from azure.eventhub import EventData, EventDataBatch, EventHubProducerClient
from multiprocessing import Pool
from typing import List
import uamqp
import os

CONNECTION_STR = os.environ['EVENT_HUB_CONN_STR']
EVENTHUB_NAME = os.environ['EVENT_HUB_NAME']

producer = EventHubProducerClient.from_connection_string(
    conn_str=CONNECTION_STR,
    eventhub_name=EVENTHUB_NAME
)

def build_event_data(i):
    return EventData(body=f'{i}')

def compare_props(before, after):
    for prop, val in vars(before).items():
        after_val = getattr(after, prop)
        if after_val != val:
            print('the following two are not equal')
            print(prop, ":", val)
            print(type(val))
            print(prop, ":", after_val)
            print(type(after_val))
            print()

def compare_message_props(before, after):
    before_m = before.message._body._message
    after_m = after.message._body._message
    before_attributes = [attr for attr in dir(before_m) if not attr.startswith('__')]
    after_attributes = [attr for attr in dir(after_m) if not attr.startswith('__')]
    for attr in before_attributes:
        before_val = getattr(before_m, attr)
        after_val = getattr(after_m, attr)
        if after_val != before_val:
            print('the following two are not equal')
            print(attr, ":", before_val)
            print(type(before_val))
            print(attr, ":", after_val)
            print(type(after_val))
            print()

def pickle_event():
    print('pickle event')
    event = EventData('bye')
    a = pickle.dumps(event)
    b = pickle.loads(a)
    return event, b

def pickle_event_batch():
    print('pickle event batch')
    # try pickling batch
    event = EventData('bye')
    event.properties = {'prop_key': 'val'}
    data_batch = producer.create_batch(partition_key='pkey', partition_id='0')
    data_batch.add(event)
    a = pickle.dumps(data_batch)
    b = pickle.loads(a)
    return data_batch, b

def pickle_event_list():
    print('pickle event batch')
    # try pickling batch
    event = EventData('bye')
    event.properties = {'prop_key': 'val'}
    data_batch = producer.create_batch(partition_key='pkey', partition_id='0')
    data_batch.add(event)
    for prop, val in vars(data_batch.message).items():
        print(prop, ":", val)
    a = pickle.dumps(data_batch)
    b = pickle.loads(a)
    print()
    for prop, val in vars(b.message).items():
        print(prop, ":", val)
    print()

def pickle_event_with_props():
    print('pickle event with props\n')
    a = 'dkfhahg9w342ashgkaht1 3t9hgadihgiaw htgasjhdfkwytahgaury9ryh3jadhga9syf3hrfhafd'
    event = EventData(a)
    event.properties = {'prop_key': 'val'}
    a = pickle.dumps(event)
    b = pickle.loads(a)
    return event, b

if __name__ == "__main__":
    with Pool() as p:
        eventdata : List[EventData] = p.map(build_event_data,[(i) for i in range(10)])
    #before, after = pickle_event()
    #compare_props(before.message, after.message)

    before, after = pickle_event_with_props()
    print(before)
    print(after)
    print(before.message)
    print(after.message)
    #print(type(before.message._body))
    #compare_message_props(before, after)
    #print(before.message._body.__dict__)
    #print(after.message._body.__dict__)
    #compare_props(before.message._body, after.message._body)

    #before, after = pickle_event_batch()
    #compare_props(before, after)
