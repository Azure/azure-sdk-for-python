#!/usr/bin/env python

# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------


RUN_BREAKING_CHANGES_PACKAGES = ["azure-mgmt-*"]


# See Readme for ignore format

IGNORE_BREAKING_CHANGES = {
    "azure-mgmt-": [
        # Changes due to latest dpg design + need to support overloads in this tool
        ("ChangedParameterOrdering", "*", "*", "__init__"),
        # Changes due to latest dpg design
        ("ChangedParameterKind", "*", "*", "*", "top"),
        ("ChangedParameterKind", "*", "*", "*", "filter"),
        ("ChangedParameterKind", "*", "*", "*", "skip"),
        ("RemovedOrRenamedPositionalParam", "*", "*", "*", "maxpagesize"),
        # msrest model bases on vendored _serialization.model instead of msrest.Model which no longer has "validate"
        ("RemovedOrRenamedClassMethod", "*", "*", "validate"),
        # Changes due to not using msrest anymore
        ("RemovedOrRenamedClassMethod", "*", "*", "as_dict"),
        ("RemovedOrRenamedClassMethod", "*", "*", "deserialize"),
        ("RemovedOrRenamedClassMethod", "*", "*", "enable_additional_properties_sending"),
        ("RemovedOrRenamedClassMethod", "*", "*", "from_dict"),
        ("RemovedOrRenamedClassMethod", "*", "*", "is_xml_model"),
        ("RemovedOrRenamedClassMethod", "*", "*", "serialize"),
        ("RemovedOrRenamedPositionalParam", "*", "*", "as_dict", "key_transformer"),
        ("RemovedOrRenamedPositionalParam", "*", "*", "as_dict"),
        ("RemovedFunctionKwargs", "*", "*", "as_dict"),
        # operation group can't be instantiated independently so don't need check for it
        ("RemovedOrRenamedPositionalParam", "*", "*", "__init__", "client"),
        ("RemovedOrRenamedPositionalParam", "*", "*", "__init__", "config"),
        ("RemovedOrRenamedPositionalParam", "*", "*", "__init__", "serializer"),
        ("RemovedOrRenamedPositionalParam", "*", "*", "__init__", "deserializer"),
        # compared with msrest model, new DPG model is inherited from dict so we shall ignore some methods(e.g get/keys/items/values/...)
        ("ADDED_CLASS_METHOD", "*", "*", "clear"),
        ("ADDED_CLASS_METHOD", "*", "*", "copy"),
        ("ADDED_CLASS_METHOD", "*", "*", "get"),
        ("ADDED_CLASS_METHOD", "*", "*", "items"),
        ("ADDED_CLASS_METHOD", "*", "*", "keys"),
        ("ADDED_CLASS_METHOD", "*", "*", "pop"),
        ("ADDED_CLASS_METHOD", "*", "*", "popitem"),
        ("ADDED_CLASS_METHOD", "*", "*", "setdefault"),
        ("ADDED_CLASS_METHOD", "*", "*", "update"),
        ("ADDED_CLASS_METHOD", "*", "*", "values"),
        ("ADDED_CLASS_METHOD_PARAMETER", "*", "*", "args", "__init__"),
    ]
}
