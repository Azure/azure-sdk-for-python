import json
import re
import warnings
import sys
from urllib.request import urlopen
from azure.eventgrid._generated import models
from _constants import files, backward_compat, EXCEPTIONS

def extract(definitions):
    if not definitions:
        return
    tups = []
    for event in definitions:
        if event.endswith('Data') and event not in EXCEPTIONS:
            try:
                key, txt = "Name".join(event.rsplit('Data', 1)), definitions[event]['description']
                val = re.findall("Microsoft.[a-zA-Z]+.[a-zA-Z]+", txt)
                tups.append((key, val[0]))
            except:
                warnings.warn("Unable to generate the event mapping for {}".format(event[0]))
                sys.exit(1)
    return tups

def generate_enum_content(tuples):
    print("# these names below are for backward compat only - refrain from using them.")
    for k, v in backward_compat.items():
        print(k + " = '" + v + "'\n")
    print("# backward compat names end here.")
    for tup in tup_list:
        print(tup[0] + " = '" + tup[1].replace('API', 'Api') + "'\n")

definitions = {}
for fp in files:
    data = json.loads(urlopen(fp).read())
    definitions.update(data.get('definitions'))
tup_list = extract(definitions)
tup_list.sort(key=lambda tup: tup[0])
generate_enum_content(tup_list)
