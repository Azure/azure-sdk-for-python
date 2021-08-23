# --------------------------------------------------------------------------
#
# Copyright (c) Microsoft Corporation. All rights reserved.
#
# The MIT License (MIT)
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the ""Software""), to
# deal in the Software without restriction, including without limitation the
# rights to use, copy, modify, merge, publish, distribute, sublicense, and/or
# sell copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED *AS IS*, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS
# IN THE SOFTWARE.
#
# --------------------------------------------------------------------------

# pylint: disable=line-too-long
# pylint: disable=redefined-builtin
# pylint: disable=unused-argument
from dataclasses import dataclass

@dataclass(init=False)
class ConnectionContext:
    hub: str
    connection_id: str
    event_name: str
    type: str
    origin: str = None
    user_id: str = None
    subprotocol: str = None
    states: dict[str, object] = None

    def __init__(self, hub: str, connection_id: str, event_name: str, type: str, origin: str = None, user_id: str = None, subprotocol: str = None, states: dict[str, object] = None, **kwargs):
        self.hub = hub
        self.connection_id = connection_id
        self.event_name = event_name
        self.type = type
        self.origin = origin
        self.user_id = user_id
        self.subprotocol = subprotocol
        self.states = states

@dataclass(init=False)
class Certificate:
    thumbprint: str

    def __init__(self, thumbprint: str, **kwargs):
        self.thumbprint = thumbprint

@dataclass(init=False)
class ConnectResponse:
    groups: list[str] = None
    roles: list[str] = None
    user_id: str = None
    subprotocol: str = None

    def __init__(self, groups: list[str] = None, roles: list[str] = None, user_id: str = None, subprotocol: str = None, **kwargs):
        self.groups = groups
        self.roles = roles
        self.user_id = user_id
        self.subprotocol = subprotocol

@dataclass(init=False)
class ConnectResquest:
    claims: dict[str, list[str]] = None
    queries: dict[str, list[str]] = None
    subprotocols: list[str] = None
    client_certificates: list[Certificate] = None

    def __init__(self, claims: dict[str, list[str]] = None, queries: dict[str, list[str]] = None, subprotocols: list[str] = None, client_certificates: list[Certificate] = None, **kwargs):
        self.claims = claims
        self.queries = queries
        self.subprotocols = subprotocols
        self.client_certificates = client_certificates


@dataclass(init=False)
class DisconnectedRequest:
    reason: str = None

    def __init__(self, reason: str = None, **kwargs):
        self.reason = reason
