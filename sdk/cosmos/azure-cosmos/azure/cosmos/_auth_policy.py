# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See LICENSE.txt in the project root for
# license information.
# -------------------------------------------------------------------------
from typing import MutableMapping

from azure.core.pipeline.policies import BearerTokenCredentialPolicy
from azure.cosmos import http_constants


class CosmosBearerTokenCredentialPolicy(BearerTokenCredentialPolicy):

    @staticmethod
    def _update_headers(headers: MutableMapping[str, str], token: str) -> None:
        """Updates the Authorization header with the bearer token.
        This is the main method that differentiates this policy from core's BearerTokenCredentialPolicy and works
        to properly sign the authorization header for Cosmos' REST API. For more information:
        https://docs.microsoft.com/rest/api/cosmos-db/access-control-on-cosmosdb-resources#authorization-header

        :param dict headers: The HTTP Request headers
        :param str token: The OAuth token.
        """
        headers[http_constants.HttpHeaders.Authorization] = f"type=aad&ver=1.0&sig={token}"
