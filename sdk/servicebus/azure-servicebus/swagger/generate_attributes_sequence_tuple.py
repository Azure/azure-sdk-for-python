# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------


# This is a tool, not a part of the SDK code. Run it with Python 3.6+.
#
# It iterates the _attribute_map of model classes and print the attributes of each class into a tuple.
# `dict` in Python 3.6+ guarantees order when iterating over the dict so the attributes tuple
# has the correct order of model class attributes.
# Copy the output to file azure.servicebus.management._model_workaround.py, which will convert
# _attribute_map of each model class from dict to OrderedDict.

import inspect
from azure.servicebus.management._generated._serialization import Model
from azure.servicebus.management._generated.models import _models


if __name__ == "__main__":
    members = inspect.getmembers(_models, inspect.isclass)
    class_names = []
    model_class_attributes_string = "MODEL_CLASS_ATTRIBUTES = {\n"
    for class_name, class_ in members:
        if issubclass(class_, Model) and len(class_._attribute_map) > 1:
            attributes = ", ".join('"' + x + '"' for x in class_._attribute_map.keys())
            attributes = "    {}: ({})".format(class_name, attributes)
            model_class_attributes_string += attributes + ",\n"
            class_names.append(class_name)
    model_class_attributes_string += "}\n"
    print("from azure.servicebus.management._generated.models import", ", ".join(class_names))
    print("\n")
    print(model_class_attributes_string)
