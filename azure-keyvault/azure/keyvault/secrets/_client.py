import uuid

from azure.core.configuration import Configuration
from azure.core.pipeline.policies import UserAgentPolicy, HeadersPolicy, RetryPolicy, \
    RedirectPolicy, CredentialsPolicy, HTTPPolicy
from azure.core.pipeline.transport import RequestsTransport, HttpRequest
from azure.core.pipeline import Pipeline
from azure.core.exceptions import ClientRequestError

from msrest import Serializer, Deserializer

from ._models import Secret, SecretPaged, SecretAttributes

from .._internal import _BackupResult

class BearerTokenCredentialPolicy(HTTPPolicy):

    def __init__(self, credentials):
        self._credentials = credentials

    def send(self, request, **kwargs):
        auth_header = 'Bearer ' + self._credentials.token['access_token']
        request.http_request.headers['Authorization'] = auth_header

        return self.next.send(request, **kwargs)


class SecretClient:

    _api_version = '7.0'

    @staticmethod
    def create_config(**kwargs):
        config = Configuration(**kwargs)
        config.user_agent = UserAgentPolicy('SecretClient', **kwargs)
        config.headers = None
        config.retry = RetryPolicy(**kwargs)
        config.redirect = RedirectPolicy(**kwargs)
        return config

    def __init__(self, credentials, vault_url, config=None, **kwargs):
        """Creates a SecretClient with the for managing secrets in the specified vault.

        :param credentials:  A credential or credential provider which can be used to authenticate to the vault
        :type credentials: azure.authenctication.Credential or azure.authenctication.CredentialProvider
        :param str vault_url: The url of the vault
        :param azure.core.configuration.Configuration config:  The configuration for the SecretClient
        """
        if not credentials:
            raise ValueError('credentials')

        if not vault_url:
            raise ValueError('vault_url')

        self.vault_url = vault_url
        config = config or SecretClient.create_config(**kwargs)
        transport = RequestsTransport(config.connection)
        policies = [
            config.user_agent,
            config.headers,
            BearerTokenCredentialPolicy(credentials),
            config.redirect,
            config.retry,
            config.logging,
        ]
        client_models = {
            'Secret': Secret,
            'SecretAttributes': SecretAttributes,
            '_BackupResult': _BackupResult
        }
        self._serialize = Serializer(client_models)
        self._deserialize = Deserializer(client_models)
        self._pipeline = Pipeline(transport, policies=policies)

    def get_secret(self, name, version=None, **kwargs):
        """Get a specified from the vault.

        The GET operation is applicable to any secret stored in Azure Key
        Vault. This operation requires the secrets/get permission.

        :param str name: The name of the secret.
        :param str version: The version of the secret.  If not specified the latest version of 
            the secret is returned
        :return: Secret
        :rtype: ~azure.keyvault.secrets.Secret
        :raises:
         :class:`KeyVaultErrorException<azure.keyvault.KeyVaultErrorException>`
        """
        url = '/'.join([s.strip('/') for s in (self.vault_url, 'secrets', name, version or '')])

        query_parameters = {'api-version' : self._api_version}

        headers = {
            'Content-Type': 'application/json; charset=utf-8',
            'x-ms-client-request-id': str(uuid.uuid1())
        }

        request = HttpRequest('GET', url, headers)

        request.format_parameters(query_parameters)

        response = self._pipeline.run(request, **kwargs).http_response

        if response.status_code != 200:
            raise ClientRequestError('Request failed status code {}.  {}'.format(response.status_code, response.text()))

        return self._deserialize('Secret', response)

    def set_secret(self, name, value, content_type=None, attributes=None, tags=None, **kwargs):
        """Sets a secret in the vault.

        The SET operation adds a secret to the Azure Key Vault. If the named
        secret already exists, Azure Key Vault creates a new version of that
        secret. This operation requires the secrets/set permission.

        :param str name: The name of the secret
        :param str value: The value of the secret
        :param str content_type: Type of the secret value such as a password
        :param attributes: The secret management attributes
        :type attributes: ~azure.keyvault.secrets.SecretAttributes
        :param dict[str, str] tags: Application specific metadata in the form of key-value
            deserialized response
        :param operation_config: :ref:`Operation configuration
            overrides<msrest:optionsforoperations>`.
        :return: The created secret
        :rtype: ~azure.keyvault.secret.Secret
        :raises:
        :class:`azure.core.ClientRequestError`
        """
        secret = Secret(value=value, content_type=content_type, attributes=attributes, tags=tags)

        url = '/'.join([s.strip('/') for s in (self.vault_url, 'secrets', name)])

        query_parameters = {'api-version': self._api_version}

        headers = {
            'Content-Type': 'application/json; charset=utf-8',
            'x-ms-client-request-id': str(uuid.uuid1())
        }

        request_body = self._serialize.body(secret, 'Secret')

        request = HttpRequest('PUT', url, headers, data=request_body)

        request.format_parameters(query_parameters)

        response = self._pipeline.run(request, **kwargs).http_response

        if response.status_code != 200:
            raise ClientRequestError('Request failed status code {}.  {}'.format(response.status_code, response.text()))

        return self._deserialize('Secret', response)


    def update_secret(self, name, version, content_type=None, attributes=None, tags=None, **kwargs):

        url = '/'.join([s.strip('/') for s in (self.vault_url, 'secrets', name, version)])

        secret = Secret(content_type=content_type, attributes=attributes, tags=tags)

        query_parameters = {'api-version': self._api_version}

        headers = {
            'Content-Type': 'application/json; charset=utf-8',
            'x-ms-client-request-id': str(uuid.uuid1())
        }

        request_body = self._serialize.body(secret, 'Secret')

        request = HttpRequest('PATCH', url, headers, data=request_body)

        request.format_parameters(query_parameters)

        response = self._pipeline.run(request, **kwargs).http_response

        if response.status_code != 200:
            raise ClientRequestError('Request failed status code {}.  {}'.format(response.status_code, response.text()))

        return self._deserialize('Secret', response)


    def list_secrets(self, max_page_size=None, **kwargs):
        """List secrets in the vault.

        The Get Secrets operation is applicable to the entire vault. However,
        only the latest secret identifier and its attributes are provided in the
        response. No secret values are returned and individual secret versions are 
        not listed in the response.  This operation requires the secrets/list permission.

        :param max_page_size: Maximum number of results to return in a page. If
         not max_page_size, the service will return up to 25 results.
        :type maxresults: int
        :return: An iterator like instance of Secrets
        :rtype:
         ~azure.keyvault.secrets.SecretPaged[~azure.keyvault.secret.Secret]
        :raises:
         :class:`ClientRequestError<azure.core.ClientRequestError>`
        """
        def internal_paging(next_link=None, raw=False):
            if not next_link:
                # Construct URL
                url = '/'.join([s.strip('/') for s in (self.vault_url, 'secrets')])

                # Construct parameters
                query_parameters = {'api-version': self._api_version}
                if max_page_size is not None:
                    query_parameters['maxresults'] = str(max_page_size)
            else:
                url = next_link
                query_parameters = {}

            headers = {
                'Content-Type': 'application/json; charset=utf-8',
                'x-ms-client-request-id': str(uuid.uuid1())
            }

            # Construct and send request
            request = HttpRequest('GET', url, headers)

            request.format_parameters(query_parameters)

            response = self._pipeline.run(request, **kwargs).http_response

            if response.status_code != 200:
                raise ClientRequestError('Request failed status code {}.  {}'.format(response.status_code, response.text()))

            return response

        return SecretPaged(internal_paging, self._deserialize.dependencies)

    def list_secret_versions(self, name, max_page_size=None, **kwargs):
        """List all versions of the specified secret.

        The full secret identifier and attributes are provided in the response.
        No values are returned for the secrets. This operations requires the
        secrets/list permission.

        :param name: The name of the secret.
        :type name: str
        :param max_page_size: Maximum number of results to return in a page. If
         not max_page_size, the service will return up to 25 results.
        :type maxresults: int
        :return: An iterator like instance of Secret
        :rtype:
         ~azure.keyvault.secrets.SecretPaged[~azure.keyvault.secret.Secret]
        :raises:
         :class:`ClientRequestError<azure.core.ClientRequestError>`
        """
        def internal_paging(next_link=None, raw=False):
            if not next_link:
                # Construct URL
                url = '/'.join([s.strip('/') for s in (self.vault_url, 'secrets', name, 'versions')])

                # Construct parameters
                query_parameters = {'api-version': self._api_version}
                if max_page_size is not None:
                    query_parameters['maxresults'] = str(max_page_size)
            else:
                url = next_link
                query_parameters = {}

            headers = {
                'Content-Type': 'application/json; charset=utf-8',
                'x-ms-client-request-id': str(uuid.uuid1())
            }

            # Construct and send request
            request = HttpRequest('GET', url, headers)

            request.format_parameters(query_parameters)

            response = self._pipeline.run(request, **kwargs).http_response

            if response.status_code != 200:
                raise ClientRequestError('Request failed status code {}.  {}'.format(response.status_code, response.text()))

            return response

        return SecretPaged(internal_paging, self._deserialize.dependencies)

    def backup_secret(self, name, **kwargs):
        """Backs up the specified secret.

        Requests that a backup of the specified secret be downloaded to the
        client. All versions of the secret will be downloaded. This operation
        requires the secrets/backup permission.

        :param str name: The name of the secret.
        :return: The raw bytes of the secret backup.
        :rtype: bytes
        :raises:
         :class:azure.core.ClientRequestError
        """
        url = '/'.join([s.strip('/') for s in (self.vault_url, 'secrets', name, 'backup')])

        query_parameters = {'api-version' : self._api_version}

        headers = {
            'Content-Type': 'application/json; charset=utf-8',
            'x-ms-client-request-id': str(uuid.uuid1())
        }

        request = HttpRequest('POST', url, headers)

        request.format_parameters(query_parameters)

        response = self._pipeline.run(request, **kwargs).http_response

        if response.status_code != 200:
            raise ClientRequestError('Request failed status code {}.  {}'.format(response.status_code, response.text()))

        return self._deserialize('_BackupResult', response).value

    def restore_secret(self, backup, **kwargs):
        """Restores a backed up secret to a vault.

        Restores a backed up secret, and all its versions, to a vault. This
        operation requires the secrets/restore permission.

        :param bytes backup: The raw bytes of the secret backup
        :return: The restored secret
        :rtype: ~azure.keyvault.secrets.Secret
        :raises:
         :class:azure.core.ClientRequestError
        """
        backup = _BackupResult(value=backup)

        url = '/'.join([s.strip('/') for s in (self.vault_url, 'secrets', 'restore')])

        query_parameters = {'api-version': self._api_version}

        headers = {
            'Content-Type': 'application/json; charset=utf-8',
            'x-ms-client-request-id': str(uuid.uuid1())
        }

        request_body = self._serialize.body(backup, '_BackupResult')

        request = HttpRequest('POST', url, headers, data=request_body)

        request.format_parameters(query_parameters)

        response = self._pipeline.run(request, **kwargs).http_response

        if response.status_code != 200:
            raise ClientRequestError('Request failed status code {}.  {}'.format(response.status_code, response.text()))

        return self._deserialize('Secret', response)

    def delete_secret(self, name, **kwargs):
        pass

    def get_deleted_secret(self, name, **kwargs):
        pass

    def list_deleted_secrets(self, max_page_size=None, **kwargs):
        pass

    def purge_deleted_secret(self, name, **kwargs):
        pass

    def recover_deleted_secret(self, name, **kwargs):
        pass


