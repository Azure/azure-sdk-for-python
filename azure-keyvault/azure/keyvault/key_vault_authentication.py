#---------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
#---------------------------------------------------------------------------------------------

import inspect
import threading
from collections import namedtuple

import requests
from azure.keyvault import http_bearer_challenge_cache as ChallengeCache
from azure.keyvault.http_challenge import HttpChallenge
from azure.keyvault.http_message_security import HttpMessageSecurity
from azure.keyvault._internal import _RsaKey
from msrest.authentication import OAuthTokenAuthentication
from requests.auth import AuthBase
from requests.cookies import extract_cookies_to_jar

AccessToken = namedtuple('AccessToken', ['scheme', 'token', 'key'])
AccessToken.__new__.__defaults__ = ('Bearer', None, None)

_message_protection_supported_methods = ['sign', 'verify', 'encrypt', 'decrypt', 'wrapkey', 'unwrapkey']


def _message_protection_supported(challenge, request):
    # right now only specific key operations are supported so return true only
    # if the vault supports message protection, the request is to the keys collection
    # and the requested operation supports it
    return challenge.supports_message_protection() \
            and '/keys/' in request.url \
            and request.url.split('?')[0].strip('/').split('/')[-1].lower() in _message_protection_supported_methods


class KeyVaultAuthBase(AuthBase):
    """
    Used for handling authentication challenges, by hooking into the request AuthBase extension model.
    """

    def __init__(self, authorization_callback):
        """
        Creates a new KeyVaultAuthBase instance used for handling authentication challenges, by hooking into the request AuthBase
        extension model.
        :param authorization_callback: A callback used to provide authentication credentials to the key vault data service.  
        This callback should take four str arguments: authorization uri, resource, scope, and scheme, and return
        an AccessToken
                    return AccessToken(scheme=token['token_type'], token=token['access_token'])
        Note: for backward compatibility a tuple of the scheme and token can also be returned.
                    return token['token_type'], token['access_token']
        """
        self._user_callback = authorization_callback
        self._callback = self._auth_callback_compat
        self._token = None
        self._thread_local = threading.local()
        self._thread_local.pos = None
        self._thread_local.auth_attempted = False
        self._thread_local.orig_body = None

    # for backwards compatibility we need to support callbacks which don't accept the scheme
    def _auth_callback_compat(self, server, resource, scope, scheme):
        return self._user_callback(server, resource, scope) \
            if len(inspect.getargspec(self._user_callback).args) == 3 \
            else self._user_callback(server, resource, scope, scheme)

    def __call__(self, request):
        """
        Called prior to requests being sent.
        :param request: Request to be sent
        :return: returns the original request, registering hooks on the response if it is the first time this url has been called and an 
        auth challenge might be returned  
        """
        # attempt to pre-fetch challenge if cached
        if self._callback:
            challenge = ChallengeCache.get_challenge_for_url(request.url)
            if challenge:
                # if challenge cached get the message security
                security = self._get_message_security(request, challenge)
                # protect the request
                security.protect_request(request)
                # register a response hook to unprotect the response
                request.register_hook('response', security.unprotect_response)
            else:
                # if the challenge is not cached we will strip the body and proceed without the auth header so we
                # get back the auth challenge for the request
                self._thread_local.orig_body = request.body
                request.body = ''
                request.headers['Content-Length'] = 0
                request.register_hook('response', self._handle_401)
                request.register_hook('response', self._handle_redirect)
                self._thread_local.auth_attempted = False

        return request

    def _handle_redirect(self, r, **kwargs):
        """Reset auth_attempted on redirects."""
        if r.is_redirect:
            self._thread_local.auth_attempted = False

    def _handle_401(self, response, **kwargs):
        """
        Takes the response authenticates and resends if neccissary
        :return: The final response to the authenticated request
        :rtype: requests.Response
        """
        # If response is not 401 do not auth and return response
        if not response.status_code == 401:
            self._thread_local.auth_attempted = False
            return response

        # If we've already attempted to auth for this request once, do not auth and return response
        if self._thread_local.auth_attempted:
            self._thread_local.auth_attempted = False
            return response

        auth_header = response.headers.get('www-authenticate', '')

        # Otherwise authenticate and retry the request
        self._thread_local.auth_attempted = True

        # parse the challenge
        challenge = HttpChallenge(response.request.url, auth_header, response.headers)

        # bearer and PoP are the only authentication schemes supported at this time
        # if the response auth header is not a bearer challenge or pop challange do not auth and return response
        if not (challenge.is_bearer_challenge() or challenge.is_pop_challenge()):
            self._thread_local.auth_attempted = False
            return response

        # add the challenge to the cache
        ChallengeCache.set_challenge_for_url(response.request.url, challenge)

        # Consume content and release the original connection
        # to allow our new request to reuse the same one.
        response.content
        response.close()

        # copy the request to resend
        prep = response.request.copy()

        if self._thread_local.orig_body is not None:
            # replace the body with the saved body
            prep.prepare_body(data=self._thread_local.orig_body, files=None)

        extract_cookies_to_jar(prep._cookies, response.request, response.raw)
        prep.prepare_cookies(prep._cookies)

        security = self._get_message_security(prep, challenge)

        # auth and protect the prepped request message
        security.protect_request(prep)

        # resend the request with proper authentication and message protection
        _response = response.connection.send(prep, **kwargs)
        _response.history.append(response)
        _response.request = prep

        # unprotected the response
        security.unprotect_response(_response)

        return _response

    def _get_message_security(self, request, challenge):
        scheme = challenge.scheme

        # if the given request can be protected ensure the scheme is PoP so the proper access token is requested
        if _message_protection_supported(challenge, request):
            scheme = 'PoP'

        # use the authentication_callback to get the token and create the message security
        token = AccessToken(*self._callback(challenge.get_authorization_server(),
                                            challenge.get_resource(),
                                            challenge.get_scope(),
                                            scheme))
        security = HttpMessageSecurity(client_security_token=token.token)

        # if the given request can be protected add the appropriate keys to the message security
        if scheme == 'PoP':
            security.client_signature_key = token.key
            security.client_encryption_key = _RsaKey.generate()
            security.server_encryption_key = _RsaKey.from_jwk_str(challenge.server_encryption_key)
            security.server_signature_key = _RsaKey.from_jwk_str(challenge.server_signature_key)

        return security


class KeyVaultAuthentication(OAuthTokenAuthentication):
    """
    Authentication class to be used as credentials for the KeyVaultClient.
    :Example Usage:    
            def auth_callack(server, resource, scope):
                self.data_creds = self.data_creds or ServicePrincipalCredentials(client_id=self.config.client_id,
                                                                                 secret=self.config.client_secret,
                                                                                 tenant=self.config.tenant_id,
                                                                                 resource=resource)
                token = self.data_creds.token
                return token['token_type'], token['access_token']

            self.keyvault_data_client = KeyVaultClient(KeyVaultAuthentication(auth_callack))
    """

    def __init__(self, authorization_callback=None, credentials=None):
        """
        Creates a new KeyVaultAuthentication instance used for authentication in the KeyVaultClient
        :param authorization_callback: A callback used to provide authentication credentials to the key vault data service.  
        This callback should take three str arguments: authorization uri, resource, and scope, and return 
        a tuple of (token type, access token).
        :param credentials:: Credentials needed for the client to connect to Azure.
        :type credentials: :mod:`A msrestazure Credentials
         object<msrestazure.azure_active_directory>`
        """
        if not authorization_callback and not credentials:
            raise ValueError("Either parameter 'authorization_callback' or parameter 'credentials' must be specified.")

        # super(KeyVaultAuthentication, self).__init__()

        self._credentials = credentials

        if not authorization_callback:
            def auth_callback(server, resource, scope, scheme):
                if self._credentials.resource != resource:
                    self._credentials.resource = resource
                    self._credentials.set_token()
                token = self._credentials.token
                return AccessToken(scheme=token['token_type'], token=token['access_token'], key=None)

            authorization_callback = auth_callback

        self.auth = KeyVaultAuthBase(authorization_callback)
        self._callback = authorization_callback
        
    def signed_session(self, session=None):
        session = session or requests.Session()
        session.auth = self.auth
        return session

    def refresh_session(self):
        """Return updated session if token has expired, attempts to
        refresh using refresh token.

        :rtype: requests.Session.
        """
        if self._credentials:
            self._credentials.refresh_session()
        return self.signed_session()
