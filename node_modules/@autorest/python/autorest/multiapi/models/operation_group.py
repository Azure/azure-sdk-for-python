# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
from typing import Dict, List, TypeVar

T = TypeVar("T")
OrderedSet = Dict[T, None]


class OperationGroup:
    def __init__(self, name: str):
        self.name = name
        self._available_apis: OrderedSet[str] = {}
        self._api_to_class_name: Dict[str, str] = {}

    @property
    def available_apis(self) -> List[str]:
        return list(self._available_apis.keys())

    def append_available_api(self, val: str) -> None:
        self._available_apis[val] = None

    def append_api_class_name_pair(self, api_version: str, class_name: str):
        self._api_to_class_name[api_version] = class_name

    def class_name(self, api_version: str):
        return self._api_to_class_name[api_version]
