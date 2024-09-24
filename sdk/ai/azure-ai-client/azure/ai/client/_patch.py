# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Customize generated code here.

Follow our quickstart for examples: https://aka.ms/azsdk/python/dpcodegen/python/customize
"""
import datetime
import logging
import base64
import json
from typing import List, Tuple, Union
from azure.core.credentials import TokenCredential, AccessToken
from ._client import Client as ClientGenerated

logger = logging.getLogger(__name__)

# This is only done to rename the client. Can we do this in TypeSpec?
class AzureAIClient(ClientGenerated):
    pass

class SASTokenCredential(TokenCredential):
    def __init__(
            self,
            *,
            sas_token: str,
            credential: TokenCredential,
            subscription_id: str,
            resource_group_name: str,
            workspace_name: str,
            connection_name: str
        ):
        self._sas_token = sas_token
        self._credential = credential
        self._subscription_id = subscription_id
        self._resource_group_name = resource_group_name
        self._workspace_name = workspace_name
        self._connection_name = connection_name
        self._expires_on = SASTokenCredential._get_expiration_date_from_token(self._sas_token)
        logger.debug("[SASTokenCredential.__init__] Exit. Given token expires on %s.", self._expires_on)

    @classmethod
    def _get_expiration_date_from_token(cls, jwt_token: str) -> datetime:
        payload = jwt_token.split('.')[1]
        padded_payload = payload + '=' * (4 - len(payload) % 4)  # Add padding if necessary
        decoded_bytes = base64.urlsafe_b64decode(padded_payload)
        decoded_str = decoded_bytes.decode('utf-8')
        decoded_payload = json.loads(decoded_str)
        expiration_date = decoded_payload.get('exp')
        return datetime.datetime.fromtimestamp(expiration_date, datetime.timezone.utc)

    def _refresh_token(self) -> None:
        logger.debug("[SASTokenCredential._refresh_token] Enter")
        ai_client = ClientGenerated(
            credential=self._credential,
            subscription_id=self._subscription_id,
            resource_group_name=self._resource_group_name,
            workspace_name=self._workspace_name,
        )

        connection = ai_client.connections.get(
            connection_name=self._connection_name,
            populate_secrets=True
        )

        self._sas_token = connection.properties.credentials.sas
        self._expires_on = SASTokenCredential._get_expiration_date_from_token(self._sas_token)
        logger.debug("[SASTokenCredential._refresh_token] Exit. New token expires on %s.", self._expires_on)

    def get_token(self) -> AccessToken:
        logger.debug("SASTokenCredential.get_token] Enter")
        if self._expires_on < datetime.datetime.now(datetime.timezone.utc):
            self._refresh_token()
        return AccessToken(self._sas_token, self._expires_on.timestamp())


__all__: List[str] = [
    "AzureAIClient",
    "SASTokenCredential"
]  # Add all objects you want publicly available to users at this package level


def patch_sdk():
    """Do not remove from this file.

    `patch_sdk` is a last resort escape hatch that allows you to do customizations
    you can't accomplish using the techniques described in
    https://aka.ms/azsdk/python/dpcodegen/python/customize
    """
