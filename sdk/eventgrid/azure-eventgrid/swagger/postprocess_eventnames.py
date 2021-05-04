import inspect
import re
import warnings
import sys
from azure.eventgrid._generated import models

def event_tuples(system_events):
    tup_list = []
    for event in system_events:
        class_name = event[0].replace("EventData", "EventName")
        try:
            event_name = re.findall("Microsoft.[a-zA-Z]+.[a-zA-Z]+", event[1].__doc__)[0]
        except:
            print(event[0])
            warnings.warn("Unable to generate the event mapping for {}", event[0])
            sys.exit(1)
        tup_list.append((class_name, event_name))
    return tup_list

def generate_enum_content(tuples):
    for tup in tup_list:
        print(tup[0] + " = '" + tup[1] + "'\n")

system_events = [m for m in inspect.getmembers(models) if m[0].endswith('EventData')]
tup_list = event_tuples(system_events)

generate_enum_content(tup_list)
