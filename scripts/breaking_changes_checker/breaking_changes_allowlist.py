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
    ]
}
