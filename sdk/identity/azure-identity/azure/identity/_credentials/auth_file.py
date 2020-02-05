# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import json

from .client_credential import ClientSecretCredential
from azure.core.exceptions import ClientAuthenticationError


def _parse_credentials_file(file_path):
    with open(file_path, 'r') as f:
        auth_str = f.read()
        
    return json.loads(auth_str)


class AuthFileCredential(object):

    def __init__(self, file_path, **kwargs):
        # type: (str, **Any) -> None
        self._credential = None
        self._file_path = file_path
        self._kwargs = kwargs.copy()

    def get_token(self, *scopes, **kwargs):
        # type: (*str, **Any) -> AccessToken
        self._ensure_credential()
        return self._credential.get_token(*scopes, **kwargs)

    def _ensure_credential(self):
        if self._credential is None:
            try:
                self._credential = self._build_credential_for_creds_file(_parse_credentials_file(self._file_path))
            except IOError as e:
                raise ClientAuthenticationError('No file found on the given path')
            except Exception as parse_e:
                raise ClientAuthenticationError('Error parsing SDK Auth File')

    def _build_credential_for_creds_file(self, auth_data):
        client_id = auth_data.get('clientId')
        client_secret = auth_data.get('clientSecret')
        tenant_id = auth_data.get('tenantId')
        active_directory_endpoint_url = auth_data.get('activeDirectoryEndpointUrl')

        if any(x is None for x in (client_id, client_secret, tenant_id, active_directory_endpoint_url)):
            raise ClientAuthenticationError("Malformed Azure SDK Auth file. The file should contain "
                "'clientId', 'clientSecret', 'tenantId' and 'activeDirectoryEndpointUrl' values.")
        
        return ClientSecretCredential(tenant_id, client_id, client_secret, authority=active_directory_endpoint_url, **self._kwargs)
