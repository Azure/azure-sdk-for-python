# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from typing import Iterable


class EndpointsOperations():
    def __init__(self):
        pass

    def list(self, type: str = None) -> Iterable["Endpoint"]:
        pass

    def get_online_endpoint_keys() -> object:
        pass

    def get_serverless_endpoint_keys() -> object:
        pass
