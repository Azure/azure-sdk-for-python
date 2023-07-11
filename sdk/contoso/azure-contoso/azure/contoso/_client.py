#
# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

from enum import Enum
from typing import Optional, List

class NoodleCreateRequest:

    def __init__(self, name: str, color: Optional["NoodleColor"]):
        self.name = name
        self.color = color

class NoodleColor(Enum):
    red = "red"
    blue = "blue"
    green = "green"

class NoodleResponse:

    def __init__(self, name: str, color: NoodleColor):
        self.name = name
        self.color = color

""" NoodleManager for interacting with the service synchronously. """
class NoodleManager(object):
    
    def __init__(self, endpoint, credential, options: dict):
        self._endpoint = endpoint

    """ Creates a noodle synchronously. """
    def create_noodle(self, noodle: NoodleCreateRequest, **kwargs) -> NoodleResponse:
        return NoodleResponse("test", NoodleColor.red)

    """ Gets a noodle synchronously. """
    def get_noodle(self, options: dict) -> NoodleResponse:
        return NoodleResponse("test", NoodleColor.red)

    """ Lists noodles synchronously. """
    def get_noodles(self, options: dict) -> List[NoodleResponse]:
        return [NoodleResponse("test", NoodleColor.red)]

""" NoodleAsyncManager for interacting with the service asynchronously."""
class NoodleAsyncManager(object):
    
    async def __init__(self, endpoint, credential, options: dict):
        self._endpoint = endpoint

    """ Creates a noodle asynchronously. """
    async def create_noodle_async(self, noodle: NoodleCreateRequest, **kwargs) -> NoodleResponse:
        return NoodleResponse("test", NoodleColor.red)

    """ Gets a widget asynchronously. """
    async def get_noodle_async(self, options: dict) -> NoodleResponse:
        return NoodleResponse("test", NoodleColor.red)

    """ Lists noodles asynchronously. """
    async def get_noodles_async(self, options: dict) -> List[NoodleResponse]:
        return [NoodleResponse("test", NoodleColor.red)]
