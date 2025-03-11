# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
from typing import Optional

class ClassNameClient:
    def __init__(self, credential: str, eight: Optional[str] = None) -> None:
        """
        :param credential: The credential to use for authentication.
        :type credential: str
        :param eight: The eighth parameter.
        :type eight: Optional[str]
        """
        self.credential = credential
        self.eight = eight
