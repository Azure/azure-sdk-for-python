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

import ast
import os
import logging
import re
import time
import warnings
try:
    from urlparse import urlparse, parse_qs
except ImportError:
    from urllib.parse import urlparse, parse_qs

import adal
from oauthlib.oauth2 import BackendApplicationClient, LegacyApplicationClient
from oauthlib.oauth2.rfc6749.errors import (
    InvalidGrantError,
    MismatchingStateError,
    OAuth2Error,
    TokenExpiredError)
from requests import RequestException, ConnectionError, HTTPError
import requests
import requests_oauthlib as oauth

try:
    import keyring
except Exception as err:
    keyring = False
    KEYRING_EXCEPTION = err

from msrest.authentication import OAuthTokenAuthentication, Authentication, BasicTokenAuthentication
from msrest.exceptions import TokenExpiredError as Expired
from msrest.exceptions import AuthenticationError, raise_with_traceback

from msrestazure.azure_cloud import AZURE_CHINA_CLOUD, AZURE_PUBLIC_CLOUD
from msrestazure.azure_configuration import AzureConfiguration

_LOGGER = logging.getLogger(__name__)

if not keyring:
    _LOGGER.warning("Cannot load 'keyring' on your system (either not installed, or not configured correctly): %s", KEYRING_EXCEPTION)

def _build_url(uri, paths, scheme):
    """Combine URL parts.

    :param str uri: The base URL.
    :param list paths: List of strings that make up the URL.
    :param str scheme: The URL scheme, 'http' or 'https'.
    :rtype: str
    :return: Combined, formatted URL.
    """
    path = [str(p).strip('/') for p in paths]
    combined_path = '/'.join(path)
    parsed_url = urlparse(uri)
    replaced = parsed_url._replace(scheme=scheme)
    if combined_path:
        path = '/'.join([replaced.path, combined_path])
        replaced = replaced._replace(path=path)

    new_url = replaced.geturl()
    new_url = new_url.replace('///', '//')
    return new_url


def _http(uri, *extra):
    """Convert https URL to http.

    :param str uri: The base URL.
    :param str extra: Additional URL paths (optional).
    :rtype: str
    :return: An HTTP URL.
    """
    return _build_url(uri, extra, 'http')


def _https(uri, *extra):
    """Convert http URL to https.

    :param str uri: The base URL.
    :param str extra: Additional URL paths (optional).
    :rtype: str
    :return: An HTTPS URL.
    """
    return _build_url(uri, extra, 'https')


class AADMixin(OAuthTokenAuthentication):
    """Mixin for Authentication object.
    Provides some AAD functionality:

    - State validation
    - Token caching and retrieval
    - Default AAD configuration
    """
    _token_uri = "/oauth2/token"
    _auth_uri = "/oauth2/authorize"
    _tenant = "common"
    _keyring = "AzureAAD"
    _case = re.compile('([a-z0-9])([A-Z])')

    def _configure(self, **kwargs):
        """Configure authentication endpoint.

        Optional kwargs may include:

            - cloud_environment (msrestazure.azure_cloud.Cloud): A targeted cloud environment
            - china (bool): Configure auth for China-based service,
              default is 'False'.
            - tenant (str): Alternative tenant, default is 'common'.
            - auth_uri (str): Alternative authentication endpoint.
            - token_uri (str): Alternative token retrieval endpoint.
            - resource (str): Alternative authentication resource, default
              is 'https://management.core.windows.net/'.
            - verify (bool): Verify secure connection, default is 'True'.
            - keyring (str): Name of local token cache, default is 'AzureAAD'.
            - timeout (int): Timeout of the request in seconds.
            - proxies (dict): Dictionary mapping protocol or protocol and
              hostname to the URL of the proxy.
        """
        if kwargs.get('china'):
            err_msg = ("china parameter is deprecated, "
                       "please use "
                       "cloud_environment=msrestazure.azure_cloud.AZURE_CHINA_CLOUD")
            warnings.warn(err_msg, DeprecationWarning)
            self.cloud_environment = AZURE_CHINA_CLOUD
        else:
            self.cloud_environment = AZURE_PUBLIC_CLOUD
        self.cloud_environment = kwargs.get('cloud_environment', self.cloud_environment)

        auth_endpoint = self.cloud_environment.endpoints.active_directory
        resource = self.cloud_environment.endpoints.active_directory_resource_id

        tenant = kwargs.get('tenant', self._tenant)
        self.auth_uri = kwargs.get('auth_uri', _https(
            auth_endpoint, tenant, self._auth_uri))
        self.token_uri = kwargs.get('token_uri', _https(
            auth_endpoint, tenant, self._token_uri))
        self.verify = kwargs.get('verify', True)
        self.cred_store = kwargs.get('keyring', self._keyring)
        self.resource = kwargs.get('resource', resource)
        self.proxies = kwargs.get('proxies')
        self.timeout = kwargs.get('timeout')
        self.state = oauth.oauth2_session.generate_token()
        self.store_key = "{}_{}".format(
            auth_endpoint.strip('/'), self.store_key)

    def _check_state(self, response):
        """Validate state returned by AAD server.

        :param str response: URL returned by server redirect.
        :raises: ValueError if state does not match that of the request.
        :rtype: None
        """
        query = parse_qs(urlparse(response).query)
        if self.state not in query.get('state', []):
            raise ValueError(
                "State received from server does not match that of request.")

    def _convert_token(self, token):
        """Convert token fields from camel case.

        :param dict token: An authentication token.
        :rtype: dict
        """
        # If it's from ADAL, expiresOn will be in ISO form.
        # Bring it back to float, using expiresIn
        if "expiresOn" in token and "expiresIn" in token:
            token["expiresOn"] = token['expiresIn'] + time.time()
        return {self._case.sub(r'\1_\2', k).lower(): v
                for k, v in token.items()}

    def _parse_token(self):
        # AD answers 'expires_on', and Python oauthlib expects 'expires_at'
        if 'expires_on' in self.token and 'expires_at' not in self.token:
            self.token['expires_at'] = self.token['expires_on']

        if self.token.get('expires_at'):
            countdown = float(self.token['expires_at']) - time.time()
            self.token['expires_in'] = countdown

    def _default_token_cache(self, token):
        """Store token for future sessions.

        :param dict token: An authentication token.
        :rtype: None
        """
        self.token = token
        if keyring:
            try:
                keyring.set_password(self.cred_store, self.store_key, str(token))
            except Exception as err:
                _LOGGER.warning("Keyring cache token has failed: %s", str(err))

    def _retrieve_stored_token(self):
        """Retrieve stored token for new session.

        :raises: ValueError if no cached token found.
        :rtype: dict
        :return: Retrieved token.
        """
        token = keyring.get_password(self.cred_store, self.store_key)
        if token is None:
            raise ValueError("No stored token found.")
        self.token = ast.literal_eval(str(token))
        self.signed_session()

    def signed_session(self, session=None):
        """Create token-friendly Requests session, using auto-refresh.
        Used internally when a request is made.

        If a session object is provided, configure it directly. Otherwise,
        create a new session and return it.

        :param session: The session to configure for authentication
        :type session: requests.Session
        """
        self._parse_token()
        return super(AADMixin, self).signed_session(session)

    def _setup_session(self):
        """Create token-friendly Requests session.

        :rtype: requests_oauthlib.OAuth2Session
        """
        return oauth.OAuth2Session(client=self.client)

    def refresh_session(self, session=None):
        """Return updated session if token has expired, attempts to
        refresh using newly acquired token.

        If a session object is provided, configure it directly. Otherwise,
        create a new session and return it.

        :param session: The session to configure for authentication
        :type session: requests.Session
        :rtype: requests.Session.
        """
        if 'refresh_token' in self.token:
            with self._setup_session() as oauth_session:
                try:
                    token = oauth_session.refresh_token(self.token_uri,
                                                  refresh_token=self.token['refresh_token'],
                                                  verify=self.verify,
                                                  proxies=self.proxies,
                                                  timeout=self.timeout)
                except (RequestException, OAuth2Error, InvalidGrantError) as err:
                    raise_with_traceback(AuthenticationError, "", err)

                self.token = token
                self._default_token_cache(self.token)
        else:
            self.set_token()
        return self.signed_session(session)

    def clear_cached_token(self):
        """Clear any stored tokens.

        :raises: KeyError if failed to clear token.
        """
        try:
            keyring.delete_password(self.cred_store, self.store_key)
        except keyring.errors.PasswordDeleteError:
            raise_with_traceback(KeyError, "Unable to clear token.")


class AADTokenCredentials(AADMixin):
    """
    Credentials objects for AAD token retrieved through external process
    e.g. Python ADAL lib.

    Optional kwargs may include:

    - cloud_environment (msrestazure.azure_cloud.Cloud): A targeted cloud environment
    - china (bool): Configure auth for China-based service,
      default is 'False'.
    - tenant (str): Alternative tenant, default is 'common'.
    - auth_uri (str): Alternative authentication endpoint.
    - token_uri (str): Alternative token retrieval endpoint.
    - resource (str): Alternative authentication resource, default
      is 'https://management.core.windows.net/'.
    - verify (bool): Verify secure connection, default is 'True'.
    - keyring (str): Name of local token cache, default is 'AzureAAD'.
    - cached (bool): If true, will not attempt to collect a token,
      which can then be populated later from a cached token.

    :param dict token: Authentication token.
    :param str client_id: Client ID, if not set, Xplat Client ID
     will be used.
    """

    def __init__(self, token, client_id=None, **kwargs):
        if not client_id:
            # Default to Xplat Client ID.
            client_id = '04b07795-8ddb-461a-bbee-02f9e1bf7b46'
        super(AADTokenCredentials, self).__init__(client_id, None)
        self._configure(**kwargs)
        self.client = None
        if not kwargs.get('cached'):
            self.token = self._convert_token(token)
            self.signed_session()

    @classmethod
    def retrieve_session(cls, client_id=None):
        """Create AADTokenCredentials from a cached token if it has not
        yet expired.
        """
        session = cls(None, client_id=client_id, cached=True)
        session._retrieve_stored_token()
        return session


class UserPassCredentials(AADMixin):
    """Credentials object for Headless Authentication,
    i.e. AAD authentication via username and password.

    Headless Auth requires an AAD login (no a Live ID) that already has
    permission to access the resource e.g. an organization account, and
    that 2-factor auth be disabled.

    Optional kwargs may include:

    - cloud_environment (msrestazure.azure_cloud.Cloud): A targeted cloud environment
    - china (bool): Configure auth for China-based service,
      default is 'False'.
    - tenant (str): Alternative tenant, default is 'common'.
    - auth_uri (str): Alternative authentication endpoint.
    - token_uri (str): Alternative token retrieval endpoint.
    - resource (str): Alternative authentication resource, default
      is 'https://management.core.windows.net/'.
    - verify (bool): Verify secure connection, default is 'True'.
    - keyring (str): Name of local token cache, default is 'AzureAAD'.
    - timeout (int): Timeout of the request in seconds.
    - cached (bool): If true, will not attempt to collect a token,
      which can then be populated later from a cached token.
    - proxies (dict): Dictionary mapping protocol or protocol and
      hostname to the URL of the proxy.

    :param str username: Account username.
    :param str password: Account password.
    :param str client_id: Client ID, if not set, Xplat Client ID
     will be used.
    :param str secret: Client secret, only if required by server.
    """

    def __init__(self, username, password,
                 client_id=None, secret=None, **kwargs):
        if not client_id:
            # Default to Xplat Client ID.
            client_id = '04b07795-8ddb-461a-bbee-02f9e1bf7b46'
        super(UserPassCredentials, self).__init__(client_id, None)
        self._configure(**kwargs)

        self.store_key += "_{}".format(username)
        self.username = username
        self.password = password
        self.secret = secret
        self.client = LegacyApplicationClient(client_id=self.id)
        if not kwargs.get('cached'):
            self.set_token()

    @classmethod
    def retrieve_session(cls, username, client_id=None):
        """Create ServicePrincipalCredentials from a cached token if it has not
        yet expired.
        """
        session = cls(username, None, client_id=client_id, cached=True)
        session._retrieve_stored_token()
        return session


    def set_token(self):
        """Get token using Username/Password credentials.

        :raises: AuthenticationError if credentials invalid, or call fails.
        """
        with self._setup_session() as session:
            optional = {}
            if self.secret:
                optional['client_secret'] = self.secret
            try:
                token = session.fetch_token(self.token_uri,
                                            client_id=self.id,
                                            username=self.username,
                                            password=self.password,
                                            resource=self.resource,
                                            verify=self.verify,
                                            proxies=self.proxies,
                                            timeout=self.timeout,
                                            **optional)
            except (RequestException, OAuth2Error, InvalidGrantError) as err:
                raise_with_traceback(AuthenticationError, "", err)

            self.token = token
            self._default_token_cache(self.token)


class ServicePrincipalCredentials(AADMixin):
    """Credentials object for Service Principle Authentication.
    Authenticates via a Client ID and Secret.

    Optional kwargs may include:

    - cloud_environment (msrestazure.azure_cloud.Cloud): A targeted cloud environment
    - china (bool): Configure auth for China-based service,
      default is 'False'.
    - tenant (str): Alternative tenant, default is 'common'.
    - auth_uri (str): Alternative authentication endpoint.
    - token_uri (str): Alternative token retrieval endpoint.
    - resource (str): Alternative authentication resource, default
      is 'https://management.core.windows.net/'.
    - verify (bool): Verify secure connection, default is 'True'.
    - keyring (str): Name of local token cache, default is 'AzureAAD'.
    - timeout (int): Timeout of the request in seconds.
    - cached (bool): If true, will not attempt to collect a token,
      which can then be populated later from a cached token.
    - proxies (dict): Dictionary mapping protocol or protocol and
      hostname to the URL of the proxy.

    :param str client_id: Client ID.
    :param str secret: Client secret.
    """
    def __init__(self, client_id, secret, **kwargs):
        super(ServicePrincipalCredentials, self).__init__(client_id, None)
        self._configure(**kwargs)

        self.secret = secret
        self.client = BackendApplicationClient(self.id)
        if not kwargs.get('cached'):
            self.set_token()

    @classmethod
    def retrieve_session(cls, client_id):
        """Create ServicePrincipalCredentials from a cached token if it has not
        yet expired.
        """
        session = cls(client_id, None, cached=True)
        session._retrieve_stored_token()
        return session

    def set_token(self):
        """Get token using Client ID/Secret credentials.

        :raises: AuthenticationError if credentials invalid, or call fails.
        """
        with self._setup_session() as session:
            try:
                token = session.fetch_token(self.token_uri,
                                            client_id=self.id,
                                            resource=self.resource,
                                            client_secret=self.secret,
                                            response_type="client_credentials",
                                            verify=self.verify,
                                            timeout=self.timeout,
                                            proxies=self.proxies)
            except (RequestException, OAuth2Error, InvalidGrantError) as err:
                raise_with_traceback(AuthenticationError, "", err)
            else:
                self.token = token
                self._default_token_cache(self.token)

# For backward compatibility of import, but I doubt someone uses that...
class InteractiveCredentials(object):
    """This class has been removed and using it will raise a NotImplementedError error.
    """
    def __init__(self, *args, **kwargs):
        raise NotImplementedError("InteractiveCredentials was not functionning and was removed. Please use ADAL and device code instead.")

class AdalAuthentication(Authentication):  # pylint: disable=too-few-public-methods
    """A wrapper to use ADAL for Python easily to authenticate on Azure.

    .. versionadded:: 0.4.5

    Take an ADAL `acquire_token` method and its parameters.

    :Example:

    .. code:: python

        context = adal.AuthenticationContext('https://login.microsoftonline.com/ABCDEFGH-1234-1234-1234-ABCDEFGHIJKL')
        RESOURCE = '00000002-0000-0000-c000-000000000000' #AAD graph resource
        token = context.acquire_token_with_client_credentials(
            RESOURCE,
            "http://PythonSDK",
            "Key-Configured-In-Portal")

    can be written here:

    .. code:: python

        context = adal.AuthenticationContext('https://login.microsoftonline.com/ABCDEFGH-1234-1234-1234-ABCDEFGHIJKL')
        RESOURCE = '00000002-0000-0000-c000-000000000000' #AAD graph resource
        credentials = AdalAuthentication(
            context.acquire_token_with_client_credentials,
            RESOURCE,
            "http://PythonSDK",
            "Key-Configured-In-Portal")

    or using a lambda if you prefer:

    .. code:: python

        context = adal.AuthenticationContext('https://login.microsoftonline.com/ABCDEFGH-1234-1234-1234-ABCDEFGHIJKL')
        RESOURCE = '00000002-0000-0000-c000-000000000000' #AAD graph resource
        credentials = AdalAuthentication(
            lambda: context.acquire_token_with_client_credentials(
                RESOURCE,
                "http://PythonSDK",
                "Key-Configured-In-Portal"
            )
        )

    :param callable adal_method: A lambda with no args, or `acquire_token` method with args using args/kwargs
    :param args: Optional positional args for the method
    :param kwargs: Optional kwargs for the method
    """

    def __init__(self, adal_method, *args, **kwargs):
        super(AdalAuthentication, self).__init__()
        self._adal_method = adal_method
        self._args = args
        self._kwargs = kwargs

    def signed_session(self, session=None):
        """Create requests session with any required auth headers applied.

        If a session object is provided, configure it directly. Otherwise,
        create a new session and return it.

        :param session: The session to configure for authentication
        :type session: requests.Session
        :rtype: requests.Session
        """
        session = super(AdalAuthentication, self).signed_session(session)

        try:
            raw_token = self._adal_method(*self._args, **self._kwargs)
        except adal.AdalError as err:
            # pylint: disable=no-member
            if 'AADSTS70008:' in ((getattr(err, 'error_response', None) or {}).get('error_description') or ''):
                raise Expired("Credentials have expired due to inactivity.")
            else:
                raise AuthenticationError(err)
        except ConnectionError as err:
            raise AuthenticationError('Please ensure you have network connection. Error detail: ' + str(err))

        scheme, token = raw_token['tokenType'], raw_token['accessToken']
        header = "{} {}".format(scheme, token)
        session.headers['Authorization'] = header
        return session

def get_msi_token(resource, port=50342, msi_conf=None):
    """Get MSI token if MSI_ENDPOINT is set.

    IF MSI_ENDPOINT is not set, will try legacy access through 'http://localhost:{}/oauth2/token'.format(port).

    If msi_conf is used, must be a dict of one key in ["client_id", "object_id", "msi_res_id"]

    :param str resource: The resource where the token would be use.
    :param int port: The port if not the default 50342 is used. Ignored if MSI_ENDPOINT is set.
    :param dict[str,str] msi_conf: msi_conf if to request a token through a User Assigned Identity (if not specified, assume System Assigned)
    """
    request_uri = os.environ.get("MSI_ENDPOINT", 'http://localhost:{}/oauth2/token'.format(port))
    payload = {
        'resource': resource
    }
    if msi_conf:
        if len(msi_conf) > 1:
            raise ValueError("{} are mutually exclusive".format(list(msi_conf.keys())))
        payload.update(msi_conf)

    try:
        result = requests.post(request_uri, data=payload, headers={'Metadata': 'true'})
        _LOGGER.debug("MSI: Retrieving a token from %s, with payload %s", request_uri, payload)
        result.raise_for_status()
    except Exception as ex:  # pylint: disable=broad-except
        _LOGGER.warning("MSI: Failed to retrieve a token from '%s' with an error of '%s'. This could be caused "
                        "by the MSI extension not yet fullly provisioned.",
                        request_uri, ex)
        raise
    token_entry = result.json()
    return token_entry['token_type'], token_entry['access_token'], token_entry

def get_msi_token_webapp(resource):
    """Get a MSI token from inside a webapp or functions.

    Env variable will look like:

    - MSI_ENDPOINT = http://127.0.0.1:41741/MSI/token/
    - MSI_SECRET = 69418689F1E342DD946CB82994CDA3CB
    """
    try:
        msi_endpoint = os.environ['MSI_ENDPOINT']
        msi_secret = os.environ['MSI_SECRET']
    except KeyError as err:
        err_msg = "{} required env variable was not found. You might need to restart your app/function.".format(err)
        _LOGGER.critical(err_msg)
        raise RuntimeError(err_msg)
    request_uri = '{}/?resource={}&api-version=2017-09-01'.format(msi_endpoint, resource)
    headers = {
        'secret': msi_secret
    }

    err = None
    try:
        result = requests.get(request_uri, headers=headers)
        _LOGGER.debug("MSI: Retrieving a token from %s", request_uri)
        if result.status_code != 200:
            err = result.text
        # Workaround since not all failures are != 200
        if 'ExceptionMessage' in result.text:
            err = result.text
    except Exception as ex:  # pylint: disable=broad-except
        err = str(ex)

    if err:
        err_msg = "MSI: Failed to retrieve a token from '{}' with an error of '{}'.".format(
            request_uri, err
        )
        _LOGGER.critical(err_msg)
        raise RuntimeError(err_msg)
    _LOGGER.debug('MSI: token retrieved')
    token_entry = result.json()
    return token_entry['token_type'], token_entry['access_token'], token_entry


def _is_app_service():
    # Might be discussed if we think it's not robust enough
    return 'APPSETTING_WEBSITE_SITE_NAME' in os.environ


class MSIAuthentication(BasicTokenAuthentication):
    """Credentials object for MSI authentication,.

    Optional kwargs may include:

    - client_id: Identifies, by Azure AD client id, a specific explicit identity to use when authenticating to Azure AD. Mutually exclusive with object_id and msi_res_id.
    - object_id: Identifies, by Azure AD object id, a specific explicit identity to use when authenticating to Azure AD. Mutually exclusive with client_id and msi_res_id.
    - msi_res_id: Identifies, by ARM resource id, a specific explicit identity to use when authenticating to Azure AD. Mutually exclusive with client_id and object_id.
    - cloud_environment (msrestazure.azure_cloud.Cloud): A targeted cloud environment
    - resource (str): Alternative authentication resource, default
      is 'https://management.core.windows.net/'.

    .. versionadded:: 0.4.14
    """

    def __init__(self, port=50342, **kwargs):
        super(MSIAuthentication, self).__init__(None)

        if port != 50342:
            warnings.warn("The 'port' argument is no longer used, and will be removed in a future release", DeprecationWarning)
        self.port = port

        self.msi_conf = {k:v for k,v in kwargs.items() if k in ["client_id", "object_id", "msi_res_id"]}

        self.cloud_environment = kwargs.get('cloud_environment', AZURE_PUBLIC_CLOUD)
        self.resource = kwargs.get('resource', self.cloud_environment.endpoints.active_directory_resource_id)

        if _is_app_service():
            if self.msi_conf:
                raise AuthenticationError("User Assigned Entity is not available on WebApp yet.")
        elif "MSI_ENDPOINT" not in os.environ:
            # Use IMDS if no MSI_ENDPOINT
            self._vm_msi = _ImdsTokenProvider(self.resource, self.msi_conf)
        # Follow the same convention as all Credentials class to check for the token at creation time #106
        self.set_token()

    def set_token(self):
        if _is_app_service():
            self.scheme, _, self.token = get_msi_token_webapp(self.resource)
        elif "MSI_ENDPOINT" in os.environ:
            self.scheme, _, self.token = get_msi_token(self.resource, self.port, self.msi_conf)
        else:
            token_entry = self._vm_msi.get_token()
            self.scheme, self.token = token_entry['token_type'], token_entry

    def signed_session(self, session=None):
        """Create requests session with any required auth headers applied.

        If a session object is provided, configure it directly. Otherwise,
        create a new session and return it.

        :param session: The session to configure for authentication
        :type session: requests.Session
        :rtype: requests.Session
        """
        # Token cache is handled by the VM extension, call each time to avoid expiration
        self.set_token()
        return super(MSIAuthentication, self).signed_session(session)


class _ImdsTokenProvider(object):
    """A help class handling token acquisitions through Azure IMDS plugin.
    """

    def __init__(self, resource, msi_conf=None):
        self._user_agent = AzureConfiguration(None).user_agent
        self.identity_type, self.identity_id = None, None
        if msi_conf:
            if len(msi_conf.keys()) > 1:
                raise ValueError('"client_id", "object_id", "msi_res_id" are mutually exclusive')
            elif len(msi_conf.keys()) == 1:
                self.identity_type, self.identity_id = next(iter(msi_conf.items()))
        # default to system assigned identity on an empty configuration object

        self.cache = {}
        self.resource = resource

    def get_token(self):
        import datetime
        # let us hit the cache first
        token_entry = self.cache.get(self.resource, None)
        if token_entry:
            expires_on = int(token_entry['expires_on'])
            expires_on_datetime = datetime.datetime.fromtimestamp(expires_on)
            expiration_margin = 5  # in minutes
            if datetime.datetime.now() + datetime.timedelta(minutes=expiration_margin) <= expires_on_datetime:
                _LOGGER.info("MSI: token is found in cache.")
                return token_entry
            _LOGGER.info("MSI: cache is found but expired within %s minutes, so getting a new one.", expiration_margin)
            self.cache.pop(self.resource)

        token_entry = self._retrieve_token_from_imds_with_retry()
        self.cache[self.resource] = token_entry
        return token_entry

    def _retrieve_token_from_imds_with_retry(self):
        import random
        import json
        # 169.254.169.254 is a well known ip address hosting the web service that provides the Azure IMDS metadata
        request_uri = 'http://169.254.169.254/metadata/identity/oauth2/token'
        payload = {
            'resource': self.resource,
            'api-version': '2018-02-01'
        }
        if self.identity_id:
            payload[self.identity_type] = self.identity_id

        retry, max_retry, start_time = 1, 12, time.time()
        # simplified version of https://en.wikipedia.org/wiki/Exponential_backoff
        slots = [100 * ((2 << x) - 1) / 1000 for x in range(max_retry)]
        while True:
            result = requests.get(request_uri, params=payload, headers={'Metadata': 'true', 'User-Agent':self._user_agent})
            _LOGGER.debug("MSI: Retrieving a token from %s, with payload %s", request_uri, payload)
            if result.status_code in [404, 410, 429] or (499 < result.status_code < 600):
                if retry <= max_retry:
                    wait = random.choice(slots[:retry])
                    _LOGGER.warning("MSI: wait: %ss and retry: %s", wait, retry)
                    time.sleep(wait)
                    retry += 1
                else:
                    if result.status_code == 410:  # For IMDS upgrading, we wait up to 70s
                        gap = 70 - (time.time() - start_time)
                        if gap > 0:
                            _LOGGER.warning("MSI: wait till 70 seconds when IMDS is upgrading")
                            time.sleep(gap)
                            continue
                    break
            elif result.status_code != 200:
                raise HTTPError(request=result.request, response=result.raw)
            else:
                break

        if result.status_code != 200:
            raise TimeoutError('MSI: Failed to acquire tokens after {} times'.format(max_retry))

        _LOGGER.debug('MSI: Token retrieved')
        token_entry = json.loads(result.content.decode())
        return token_entry
