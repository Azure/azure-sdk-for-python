# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
# This code violates missing-client-constructor-parameter-credential and missing-client-constructor-parameter-kwargs
class ClassNameClient():
    def __init__(self, credential, **kwargs) -> None:
        """
        :param credential: The credential to use.
        :paramtype credential: ~azure.core.credentials.TokenCredential
        :keyword eight: The eighth parameter.
        :paramtype eight: str
        :keyword api_version: The API version to use.
        :paramtype api_version: str
        """
        self.api_version: str = kwargs.pop("api_version", "2018")
        self.credential = credential
