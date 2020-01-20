# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import six
import json

from .client_credential import ClientSecretCredential
from azure.core.exceptions import ClientAuthenticationError


def _parse_credentials_file(file_path):
    with open(file_path, 'rb') as f:
        auth_str = six.ensure_str(f.read())
        
    return json.loads(auth_str)


class AuthFileCredential(object):

    def __init__(self, file_path, **kwargs):
        self._credential = None
        self.file_path = file_path
        self.kwargs = kwargs

    def get_token(self, *scopes, **kwargs):
        self._ensure_credential()
        return self._credential.get_token(*scopes, **kwargs)

    def _ensure_credential(self):
        if self._credential is None:
            try:
                self.kwargs.pop('activeDirectoryEndpointUrl', None)
                self._credential = self._build_credential_for_creds_file(_parse_credentials_file(self.file_path))
            except Exception as e:
                raise ClientAuthenticationError('Error parsing SDK Auth File')

    def _build_credential_for_creds_file(self, auth_data:dict):
        client_id = auth_data.get('clientId')
        client_secret = auth_data.get('clientSecret')
        tenant_id = auth_data.get('tenantId')
        active_directory_endpoint_url = auth_data.get('activeDirectoryEndpointUrl')

        if any(x is None for x in (client_id, client_secret, tenant_id, active_directory_endpoint_url)):
            raise ClientAuthenticationError("Malformed Azure SDK Auth file. The file should contain \
                'clientId', 'clientSecret', 'tenentId' and 'activeDirectoryEndpointUrl' values.")
        
        return ClientSecretCredential(tenant_id, client_id, client_secret, authority=active_directory_endpoint_url, **self.kwargs)
