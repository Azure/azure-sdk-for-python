# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
from typing import Any
# This code violates do-not-use-legacy-typing
class ClassNameClient():
    def __init__(self, credential, *, api_version="2018", **kwargs):
        # type: (str, Any, str, Any) -> None
        """
        :param credential: The credential to use for authentication.
        :type credential: str
        :keyword api_version: The API version to use for the client.
        :paramtype api_version: str
        :keyword eight: The eighth parameter.
        :paramtype eight: str
        """
        self.credential: str = credential
        self.api_version: str = api_version
        self.eight: str = kwargs.get("eight")
