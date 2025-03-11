# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
from typing import Any

# This code violates check-api-version-kwarg
class ClassNameClient:
    def __init__(self, credential: str, eight: str, api_version: str = "latest", **kwargs: Any) -> None:
        """
        :param credential: The credential to use for authentication.
        :type credential: str
        :param eight: The eighth parameter.
        :type eight: str
        :param api_version: The API version to use for the client.
        :type api_version: str
        :param kwargs: Additional keyword arguments.
        """
        self.credential: str = credential
        self.eight: str = eight
        self.api_version: str = api_version
        self.kwargs: Any = kwargs
