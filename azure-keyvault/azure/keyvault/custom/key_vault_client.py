#---------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
#---------------------------------------------------------------------------------------------

import uuid
from msrest.pipeline import ClientRawResponse

from .key_vault_authentication import KeyVaultAuthentication
from ..key_vault_client import KeyVaultClient as KeyVaultClientBase
from ..models import KeyVaultErrorException
from msrest.authentication import BasicTokenAuthentication


class CustomKeyVaultClient(KeyVaultClientBase):

    def __init__(self, credentials):
        """The key vault client performs cryptographic key operations and vault operations against the Key Vault service.

        :ivar config: Configuration for client.
        :vartype config: KeyVaultClientConfiguration

        :param credentials: Credentials needed for the client to connect to Azure.
        :type credentials: :mod:`A msrestazure Credentials
         object<msrestazure.azure_active_directory>` or :mod:`A KeyVaultAuthentication
         object<key_vault_authentication>` 
        """

        # if the supplied credentials instance is not derived from KeyVaultAuthBase but is an AAD credential type
        if not isinstance(credentials, KeyVaultAuthentication) and isinstance(credentials, BasicTokenAuthentication):

            # wrap the supplied credentials with a KeyVaultAuthentication instance. Use that for the credentials supplied to the base client
            credentials = KeyVaultAuthentication(credentials=credentials)

        super(CustomKeyVaultClient, self).__init__(credentials)

    def get_pending_certificate_signing_request(self, vault_base_url, certificate_name, custom_headers=None, raw=False, **operation_config):
        """Gets the Base64 pending certificate signing request (PKCS-10).

        :param vault_base_url: The vault name, e.g.
         https://myvault.vault.azure.net
        :type vault_base_url: str
        :param certificate_name: The name of the certificate
        :type certificate_name: str
        :param dict custom_headers: headers that will be added to the request
        :param bool raw: returns the direct response alongside the
         deserialized response
        :param operation_config: :ref:`Operation configuration
         overrides<msrest:optionsforoperations>`.
        :return: Base64 encoded pending certificate signing request (PKCS-10).
        :rtype: str
        :rtype: :class:`ClientRawResponse<msrest.pipeline.ClientRawResponse>`
         if raw=true
        """
        # Construct URL
        url = '/certificates/{certificate-name}/pending'
        path_format_arguments = {
            'vaultBaseUrl': self._serialize.url("vault_base_url", vault_base_url, 'str', skip_quote=True),
            'certificate-name': self._serialize.url("certificate_name", certificate_name, 'str')
        }
        url = self._client.format_url(url, **path_format_arguments)

        # Construct parameters
        query_parameters = {}
        query_parameters['api-version'] = self._serialize.query("self.api_version", self.api_version, 'str')

        # Construct headers
        header_parameters = {}
        header_parameters['Content-Type'] = 'application/json; charset=utf-8'
        header_parameters['Accept'] = 'application/pkcs10'
        if self.config.generate_client_request_id:
            header_parameters['x-ms-client-request-id'] = str(uuid.uuid1())
        if custom_headers:
            header_parameters.update(custom_headers)
        if self.config.accept_language is not None:
            header_parameters['accept-language'] = self._serialize.header("self.config.accept_language", self.config.accept_language, 'str')

        # Construct and send request
        request = self._client.get(url, query_parameters)
        response = self._client.send(request, header_parameters, **operation_config)

        if response.status_code not in [200]:
            raise KeyVaultErrorException(self._deserialize, response)

        deserialized = None

        if response.status_code == 200:
            deserialized = response.content

        if raw:
            client_raw_response = ClientRawResponse(deserialized, response)
            return client_raw_response

        return deserialized
