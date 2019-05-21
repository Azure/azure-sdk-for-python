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
from requests import RequestException, ConnectionError, HTTPError
import requests

from msrest.authentication import OAuthTokenAuthentication, Authentication, BasicTokenAuthentication
from msrest.exceptions import TokenExpiredError as Expired
from msrest.exceptions import AuthenticationError, raise_with_traceback

from msrestazure.azure_cloud import AZURE_CHINA_CLOUD, AZURE_PUBLIC_CLOUD
from msrestazure.azure_configuration import AzureConfiguration

_LOGGER = logging.getLogger(__name__)

class AADMixin(OAuthTokenAuthentication):
    """Mixin for Authentication object.
    Provides some AAD functionality:

    - Token caching and retrieval
    - Default AAD configuration
    """
    _case = re.compile('([a-z0-9])([A-Z])')

    def _configure(self, **kwargs):
        """Configure authentication endpoint.

        Optional kwargs may include:

            - cloud_environment (msrestazure.azure_cloud.Cloud): A targeted cloud environment
            - china (bool): Configure auth for China-based service,
              default is 'False'.
            - tenant (str): Alternative tenant, default is 'common'.
            - resource (str): Alternative authentication resource, default
              is 'https://management.core.windows.net/'.
            - verify (bool): Verify secure connection, default is 'True'.
            - timeout (int): Timeout of the request in seconds.
            - proxies (dict): Dictionary mapping protocol or protocol and
              hostname to the URL of the proxy.
            - cache (adal.TokenCache): A adal.TokenCache, see ADAL configuration
              for details. This parameter is not used here and directly passed to ADAL.
        """
        if kwargs.get('china'):
            err_msg = ("china parameter is deprecated, "
                       "please use "
                       "cloud_environment=msrestazure.azure_cloud.AZURE_CHINA_CLOUD")
            warnings.warn(err_msg, DeprecationWarning)
            self._cloud_environment = AZURE_CHINA_CLOUD
        else:
            self._cloud_environment = AZURE_PUBLIC_CLOUD
        self._cloud_environment = kwargs.get('cloud_environment', self._cloud_environment)

        auth_endpoint = self._cloud_environment.endpoints.active_directory
        resource = self._cloud_environment.endpoints.active_directory_resource_id

        self._tenant = kwargs.get('tenant', "common")
        self._verify = kwargs.get('verify')  # 'None' will honor ADAL_PYTHON_SSL_NO_VERIFY
        self.resource = kwargs.get('resource', resource)
        self._proxies = kwargs.get('proxies')
        self._timeout = kwargs.get('timeout')
        self._cache = kwargs.get('cache')
        self.store_key = "{}_{}".format(
            auth_endpoint.strip('/'), self.store_key)
        self.secret = None
        self._context = None  # Future ADAL context

    def _create_adal_context(self):
        authority_url = self.cloud_environment.endpoints.active_directory
        is_adfs = bool(re.match('.+(/adfs|/adfs/)$', authority_url, re.I))
        if is_adfs:
            authority_url = authority_url.rstrip('/')  # workaround: ADAL is known to reject auth urls with trailing /
        else:
            authority_url = authority_url + '/' + self._tenant

        self._context = adal.AuthenticationContext(
            authority_url,
            timeout=self._timeout,
            verify_ssl=self._verify,
            proxies=self._proxies,
            validate_authority=not is_adfs,
            cache=self._cache,
            api_version=None
        )

    def _destroy_adal_context(self):
        self._context = None

    @property
    def verify(self):
        return self._verify

    @verify.setter
    def verify(self, value):
        self._verify = value
        self._destroy_adal_context()

    @property
    def proxies(self):
        return self._proxies

    @proxies.setter
    def proxies(self, value):
        self._proxies = value
        self._destroy_adal_context()

    @property
    def timeout(self):
        return self._timeout

    @timeout.setter
    def timeout(self, value):
        self._timeout = value
        self._destroy_adal_context()

    @property
    def cloud_environment(self):
        return self._cloud_environment

    @cloud_environment.setter
    def cloud_environment(self, value):
        self._cloud_environment = value
        self._destroy_adal_context()

    def _convert_token(self, token):
        """Convert token fields from camel case.

        :param dict token: An authentication token.
        :rtype: dict
        """
        # Beware that ADAL returns a pointer to its own dict, do
        # NOT change it in place
        token = token.copy()

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

    def set_token(self):
        if not self._context:
            self._create_adal_context()

    def signed_session(self, session=None):
        """Create token-friendly Requests session, using auto-refresh.
        Used internally when a request is made.

        If a session object is provided, configure it directly. Otherwise,
        create a new session and return it.

        :param session: The session to configure for authentication
        :type session: requests.Session
        """
        self.set_token() # Adal does the caching.
        self._parse_token()
        return super(AADMixin, self).signed_session(session)

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
            try:
                token = self._context.acquire_token_with_refresh_token(
                    self.token['refresh_token'],
                    self.id,
                    self.resource,
                    self.secret # This is needed when using Confidential Client
                )
                self.token = self._convert_token(token)
            except adal.AdalError as err:
                raise_with_traceback(AuthenticationError, "", err)
        return self.signed_session(session)


class AADTokenCredentials(AADMixin):
    """
    Credentials objects for AAD token retrieved through external process
    e.g. Python ADAL lib.

    If you just provide "token", refresh will be done on Public Azure with
    default public Azure "resource". You can set "cloud_environment",
    "tenant", "resource" and "client_id" to change that behavior.

    Optional kwargs may include:

    - cloud_environment (msrestazure.azure_cloud.Cloud): A targeted cloud environment
    - china (bool): Configure auth for China-based service,
      default is 'False'.
    - tenant (str): Alternative tenant, default is 'common'.
    - resource (str): Alternative authentication resource, default
      is 'https://management.core.windows.net/'.
    - verify (bool): Verify secure connection, default is 'True'.
    - cache (adal.TokenCache): A adal.TokenCache, see ADAL configuration
    for details. This parameter is not used here and directly passed to ADAL.


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
        self.token = self._convert_token(token)


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
    - resource (str): Alternative authentication resource, default
      is 'https://management.core.windows.net/'.
    - verify (bool): Verify secure connection, default is 'True'.
    - timeout (int): Timeout of the request in seconds.
    - proxies (dict): Dictionary mapping protocol or protocol and
      hostname to the URL of the proxy.
    - cache (adal.TokenCache): A adal.TokenCache, see ADAL configuration
    for details. This parameter is not used here and directly passed to ADAL.

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
        self.set_token()


    def set_token(self):
        """Get token using Username/Password credentials.

        :raises: AuthenticationError if credentials invalid, or call fails.
        """
        super(UserPassCredentials, self).set_token()
        try:
            token = self._context.acquire_token_with_username_password(
                self.resource,
                self.username,
                self.password,
                self.id
            )
            self.token = self._convert_token(token)
        except adal.AdalError as err:
            raise_with_traceback(AuthenticationError, "", err)

class ServicePrincipalCredentials(AADMixin):
    """Credentials object for Service Principle Authentication.
    Authenticates via a Client ID and Secret.

    Optional kwargs may include:

    - cloud_environment (msrestazure.azure_cloud.Cloud): A targeted cloud environment
    - china (bool): Configure auth for China-based service,
      default is 'False'.
    - tenant (str): Alternative tenant, default is 'common'.
    - resource (str): Alternative authentication resource, default
      is 'https://management.core.windows.net/'.
    - verify (bool): Verify secure connection, default is 'True'.
    - timeout (int): Timeout of the request in seconds.
    - proxies (dict): Dictionary mapping protocol or protocol and
      hostname to the URL of the proxy.
    - cache (adal.TokenCache): A adal.TokenCache, see ADAL configuration
    for details. This parameter is not used here and directly passed to ADAL.

    :param str client_id: Client ID.
    :param str secret: Client secret.
    """
    def __init__(self, client_id, secret, **kwargs):
        super(ServicePrincipalCredentials, self).__init__(client_id, None)
        self._configure(**kwargs)

        self.secret = secret
        self.set_token()

    def set_token(self):
        """Get token using Client ID/Secret credentials.

        :raises: AuthenticationError if credentials invalid, or call fails.
        """
        super(ServicePrincipalCredentials, self).set_token()
        try:
            token = self._context.acquire_token_with_client_credentials(
                self.resource,
                self.id,
                self.secret
            )
            self.token = self._convert_token(token)
        except adal.AdalError as err:
            raise_with_traceback(AuthenticationError, "", err)

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
                        "by the MSI extension not yet fully provisioned.",
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
            self._vm_msi = _ImdsTokenProvider(self.msi_conf)
        # Follow the same convention as all Credentials class to check for the token at creation time #106
        self.set_token()

    def set_token(self):
        if _is_app_service():
            self.scheme, _, self.token = get_msi_token_webapp(self.resource)
        elif "MSI_ENDPOINT" in os.environ:
            self.scheme, _, self.token = get_msi_token(self.resource, self.port, self.msi_conf)
        else:
            token_entry = self._vm_msi.get_token(self.resource)
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

    def __init__(self, msi_conf=None):
        self._user_agent = AzureConfiguration(None).user_agent
        self.identity_type, self.identity_id = None, None
        if msi_conf:
            if len(msi_conf.keys()) > 1:
                raise ValueError('"client_id", "object_id", "msi_res_id" are mutually exclusive')
            elif len(msi_conf.keys()) == 1:
                self.identity_type, self.identity_id = next(iter(msi_conf.items()))
        # default to system assigned identity on an empty configuration object

        self.cache = {}

    def get_token(self, resource):
        import datetime
        # let us hit the cache first
        token_entry = self.cache.get(resource, None)
        if token_entry:
            expires_on = int(token_entry['expires_on'])
            expires_on_datetime = datetime.datetime.fromtimestamp(expires_on)
            expiration_margin = 5  # in minutes
            if datetime.datetime.now() + datetime.timedelta(minutes=expiration_margin) <= expires_on_datetime:
                _LOGGER.info("MSI: token is found in cache.")
                return token_entry
            _LOGGER.info("MSI: cache is found but expired within %s minutes, so getting a new one.", expiration_margin)
            self.cache.pop(resource)

        token_entry = self._retrieve_token_from_imds_with_retry(resource)
        self.cache[resource] = token_entry
        return token_entry

    def _retrieve_token_from_imds_with_retry(self, resource):
        import random
        import json
        # 169.254.169.254 is a well known ip address hosting the web service that provides the Azure IMDS metadata
        request_uri = 'http://169.254.169.254/metadata/identity/oauth2/token'
        payload = {
            'resource': resource,
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
