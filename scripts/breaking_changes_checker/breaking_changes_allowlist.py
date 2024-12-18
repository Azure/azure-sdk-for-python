#!/usr/bin/env python

# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from _models import RegexSuppression

RUN_BREAKING_CHANGES_PACKAGES = ["azure-mgmt-*", "azure-ai-contentsafety", "azure-ai-vision-face"]


# See Readme for ignore format

IGNORE_BREAKING_CHANGES = {
    "azure-mgmt-": [
        # Rules that mgmt packages want to ignore
        ("AddedMethodOverload", "*"),
        # Changes due to latest dpg design + need to support overloads in this tool
        ("ChangedParameterOrdering", "*", "*", "__init__"),
        # Changes due to latest dpg design
        ("RemovedOrRenamedClass", "*", RegexSuppression(".*ListResult$")),
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
        ("AddedClassMethod", "*", "*", "clear"),
        ("AddedClassMethod", "*", "*", "copy"),
        ("AddedClassMethod", "*", "*", "get"),
        ("AddedClassMethod", "*", "*", "items"),
        ("AddedClassMethod", "*", "*", "keys"),
        ("AddedClassMethod", "*", "*", "pop"),
        ("AddedClassMethod", "*", "*", "popitem"),
        ("AddedClassMethod", "*", "*", "setdefault"),
        ("AddedClassMethod", "*", "*", "update"),
        ("AddedClassMethod", "*", "*", "values"),
        ("AddedClassMethodParameter", "*", "*", "args", "__init__"),
        ("AddedClassMethodParameter", "*", "*", "exclude_readonly", "as_dict"),
    ]
}
