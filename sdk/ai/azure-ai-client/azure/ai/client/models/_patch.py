# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Customize generated code here.

Follow our quickstart for examples: https://aka.ms/azsdk/python/dpcodegen/python/customize
"""
import datetime
from typing import List
from azure.core.credentials import TokenCredential
from ._models import ConnectionsListSecretsResponse


class EndpointProperties:

    def __init__(self, *, connection: ConnectionsListSecretsResponse, token_credential: TokenCredential = None) -> None:
        self.name = connection.name
        self.authentication_type = connection.properties.auth_type
        self.endpoint_type = connection.properties.category
        self.endpoint_url = (
            connection.properties.target[:-1]
            if connection.properties.target.endswith("/")
            else connection.properties.target
        )
        self.key: str = None
        if hasattr(connection.properties, "credentials"):
            if hasattr(connection.properties.credentials, "key"):
                self.key = connection.properties.credentials.key
        self.token_credential = token_credential

    def __str__(self):
        out = "{\n"
        out += f' "name": "{self.name}",\n'
        out += f' "authentication_type": "{self.authentication_type}",\n'
        out += f' "endpoint_type": "{self.endpoint_type}",\n'
        out += f' "endpoint_url": "{self.endpoint_url}",\n'
        out += f' "key": "{self.key}",\n'
        if self.token_credential:
            access_token = self.token_credential.get_token("https://cognitiveservices.azure.com/.default")
            out += f' "token_credential": "{access_token.token}", expires on {access_token.expires_on} ({datetime.datetime.fromtimestamp(access_token.expires_on, datetime.timezone.utc)})\n'
        else:
            out += f' "token_credential": "null"\n'
        out += "}\n"
        return out


__all__: List[str] = []  # Add all objects you want publicly available to users at this package level


def patch_sdk():
    """Do not remove from this file.

    `patch_sdk` is a last resort escape hatch that allows you to do customizations
    you can't accomplish using the techniques described in
    https://aka.ms/azsdk/python/dpcodegen/python/customize
    """
