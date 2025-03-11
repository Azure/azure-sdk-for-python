# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

class ClassNameClient():
    def __init__(self, credential: Any, api_version: str = '2018', **kwargs) -> None:
        """
        :param credential: The credential parameter.
        :paramtype credential: Any
        :param api_version: The API version to use.
        :paramtype api_version: str
        """
        self.credential = credential
        self.api_version = api_version
