# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# This code violates missing-client-constructor-parameter-kwargs
class ClassNameClient():
    def __init__(self, credential: str, *, api_version:str = "2018") -> None:
        """
        :param credential: The credential to use for authentication.
        :type credential: str
        :keyword api_version: The API version to use.
        :paramtype api_version: str
        """
        self.credential: str = credential
        self.api_version: str = api_version
