# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
from typing import Any
# This code violates check-api-version-kwarg
class ClassNameClient():
    def __init__(self, credential: str, **kwargs: Any) -> None:
        """
        :param credential: The credential to use for authentication.
        :type credential: str
        :keyword api_version: The API version to use.
        :paramtype api_version: str
        :keyword eight: The eighth parameter.
        :paramtype eight: str
        """
        self.credential: str = credential
        self.api_version: str = kwargs.get("api_version")
        self.eight: str = kwargs.get("eight")
