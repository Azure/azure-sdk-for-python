# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------


class ContainerRegistryTokenRequestContext(object):
    """A token request context associated with a given container registry token"""

    def __init__(self, service_name, scope):
        # type: (str, str) -> None
        self.service_name = service_name
        self.scope = scope
