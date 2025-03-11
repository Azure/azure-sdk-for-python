# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
# pylint: disable=missing-client-constructor-parameter-credential, missing-client-constructor-parameter-kwargs

class ClassNameClient:
    def __init__(self, api_version: str = "2018", **kwargs) -> None:
        """
        :keyword eight: The eighth parameter.
        :paramtype eight: str
        :keyword api_version: The API version to use.
        :paramtype api_version: str
        """
        self.api_version = api_version
