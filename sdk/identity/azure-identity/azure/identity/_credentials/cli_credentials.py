# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
from azure.common.credentials import get_azure_cli_credentials
from azure.core.credentials import AccessToken
import time


class CliCredentials(object):

    _DEFAULT_PREFIX = "/.default()"

    def get_token(self, *scopes, **kwargs):  # pylint:disable=unused-argument
        if len(scopes) != 1:
            raise ValueError("Cannot deal with multiple scope: {}".format(scopes))
        scope = scopes[0]
        if scope.endswith(self._DEFAULT_PREFIX):
            resource = scope[:-len(self._DEFAULT_PREFIX)]
        else:
            resource = scope

        credentials, subscription_id, tenant_id = get_azure_cli_credentials(resource=resource,
                                                                            with_tenant=True)
        scheme, token, fulltoken = credentials._token_retriever()

        return AccessToken(token, int(fulltoken['expiresIn'] + time.time()))
