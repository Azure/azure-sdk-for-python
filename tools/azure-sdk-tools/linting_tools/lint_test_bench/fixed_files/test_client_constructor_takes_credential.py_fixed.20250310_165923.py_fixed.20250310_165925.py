# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
class ClassNameClient():
    def __init__(self, credential: str, api_version: str = "2018", **kwargs) -> None:
        """
        :keyword eight: The eighth parameter.
        :paramtype eight: str
        :keyword api_version: The API version to use.
        :paramtype api_version: str
        :keyword credential: The credential to use for authentication.
        :paramtype credential: str
        """
        self.api_version: str = api_version
        self.credential: str = credential
