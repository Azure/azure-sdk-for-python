# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
from typing import Any
# This code violates missing-client-constructor-parameter-credential
class ClassNameClient():
    def __init__(self, *, api_version: str = "2018", **kwargs: Any) -> None:
        """
        :keyword eight: The eighth parameter.
        :paramtype eight: str
        :keyword api_version: The API version to use.
        :paramtype api_version: str
        """
        self.api_version: str = api_version
        self.eight: str = kwargs.get("eight")
