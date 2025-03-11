# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
from typing import Any

class ClassNameClient():
    def __init__(self, credential: str, eight: str = None) -> None:
        """
        :param credential: The credential to use for authentication.
        :type credential: str
        :param eight: The eighth parameter.
        :type eight: str
        """
        self.credential: str = credential
        self.eight: str = eight
