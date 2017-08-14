#---------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
#---------------------------------------------------------------------------------------------

import threading
from requests.auth import AuthBase
from requests.cookies import extract_cookies_to_jar
from msrest.authentication import OAuthTokenAuthentication
from azure.keyvault import HttpBearerChallenge
from azure.keyvault import HttpBearerChallengeCache as ChallengeCache


class KeyVaultAuthBase(AuthBase):
    """
    Used for handling authentication challenges, by hooking into the request AuthBase extension model.
    """

    def __init__(self, authorization_callback):
        """
        Creates a new KeyVaultAuthBase instance used for handling authentication challenges, by hooking into the request AuthBase
        extension model.
        :param authorization_callback: A callback used to provide authentication credentials to the key vault data service.  
        This callback should take three str arguments: authorization uri, resource, and scope, and return 
        a tuple of (token type, access token).
                    return token['token_type'], token['access_token']
        """
        self._callback = authorization_callback
        self._token = None
        self._thread_local = threading.local()
        self._thread_local.pos = None
        self._thread_local.auth_attempted = False

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
                # if challenge cached, use the authorization_callback to retrieve token and update the request
                self.set_authorization_header(request, challenge)
            else:
                # if the challenge is not cached we will let the request proceed without the auth header so we
                # get back the proper challenge in response. We register a callback to handle the response 401 response.
                try:
                    self._thread_local.pos = request.body.tell()
                except AttributeError:
                    self._thread_local.pos = None

                self._thread_local.auth_attempted = False
                request.register_hook('response', self.handle_401)
                request.register_hook('response', self.handle_redirect)

        return request

    def handle_redirect(self, r, **kwargs):
        """Reset auth_attempted on redirects."""
        if r.is_redirect:
            self._thread_local.auth_attempted = False

    def handle_401(self, response, **kwargs):
        """
        Takes the response authenticates and resends if neccissary
        :return: The final response to the authenticated request
        :rtype: requests.Response
        """
        # If response is not 401 do not auth and return response
        if not response.status_code == 401:
            self._thread_local.auth_attempted = False
            return response

        auth_header = response.headers.get('www-authenticate', '')

        # if the response auth header is not a bearer challenge do not auth and return response
        if not HttpBearerChallenge.is_bearer_challenge(auth_header):
            self._thread_local.auth_attempted = False
            return response

        # If we've already attempted to auth for this request once, do not auth and return response
        if self._thread_local.auth_attempted:
            self._thread_local.auth_attempted = False
            return response

        # Otherwise authenticate and retry the request
        self._thread_local.auth_attempted = True

        if self._thread_local.pos is not None:
            # Rewind the file position indicator of the body to where
            # it was to resend the request.
            response.request.body.seek(self._thread_local.pos)

        # add the challenge to the cache
        challenge = HttpBearerChallenge(response.request.url, auth_header)
        ChallengeCache.set_challenge_for_url(response.request.url, challenge)

        # Consume content and release the original connection
        # to allow our new request to reuse the same one.
        response.content
        response.close()

        # copy the request to resend
        prep = response.request.copy()
        extract_cookies_to_jar(prep._cookies, response.request, response.raw)
        prep.prepare_cookies(prep._cookies)

        # setup the auth header on the copied request
        self.set_authorization_header(prep, challenge)

        # resend the request with proper authentication
        _response = response.connection.send(prep, **kwargs)
        _response.history.append(response)
        _response.request = prep
        return _response

    def set_authorization_header(self, request, challenge):
        auth = self._callback(
            challenge.get_authorization_server(),
            challenge.get_resource(),
            challenge.get_scope())
        request.headers['Authorization'] = '{} {}'.format(auth[0], auth[1])


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
            raise ValueError("Either parameter 'authorization_callback' or parameter 'credentials' must not be None.")

        super(KeyVaultAuthentication, self).__init__()

        self._credentials = credentials

        if not authorization_callback:
            def auth_callback(server, resource, scope):
                if self._credentials.resource != resource:
                    self._credentials.resource = resource
                    token = self._credentials.set_token()
                token = self._credentials.token
                return token['token_type'], token['access_token']

            authorization_callback = auth_callback

        self.auth = KeyVaultAuthBase(authorization_callback)
        self._callback = authorization_callback
        
    def signed_session(self):
        session = None
        if self._credentials:
            session = self._credentials.signed_session()
        else:
            session = super(KeyVaultAuthentication, self).signed_session()
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
