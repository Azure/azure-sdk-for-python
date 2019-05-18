# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
from uamqp import AMQPClient
from abc import abstractmethod


class AMQPClientPolicy(object):

    def __init__(self, **kwargs):
        pass

    @abstractmethod
    def apply(self, amqp_client):
        # type: (AMQPClient) -> None
        pass
