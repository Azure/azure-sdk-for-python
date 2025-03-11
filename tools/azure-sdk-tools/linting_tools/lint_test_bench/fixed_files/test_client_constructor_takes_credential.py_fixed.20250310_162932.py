# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
# This code violates missing-client-constructor-parameter-credential and missing-client-constructor-parameter-kwargs
class ClassNameClient():
    def __init__(self, credential, *, api_version:str = "2018", **kwargs) -> None:
        """
        :keyword eight: The eighth parameter.
        :paramtype eight: str
        :keyword api_version: The API version to use.
        :paramtype api_version: str
        :param credential: The credential to use.
        :paramtype credential: Any
        """
        self.api_version: str = api_version
        self.credential = credential
        self.kwargs = kwargs
