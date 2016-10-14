#---------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
#---------------------------------------------------------------------------------------------

#pylint: skip-file

import adal
import urllib
from requests.auth import AuthBase
import requests

from msrest.authentication import Authentication

from . import HttpBearerChallenge
from . import HttpBearerChallengeCache as ChallengeCache

class KeyVaultAuthBase(AuthBase):

    def __init__(self, authorization_callback):
        self._callback = authorization_callback
        self._token = None

    def __call__(self, request):
        # attempt to pre-fetch challenge if cached
        if self._callback:
            challenge = ChallengeCache.get_challenge_for_url(request.url)
            if challenge:
                # if challenge cached, retrieve token and update the request
                self.set_authorization_header(request, challenge)
            else:
                # send the request to retrieve the challenge, then request the token and update
                # the request
                # TODO: wire up commons flag for things like Fiddler, logging, etc.
                response = requests.Session().send(request)
                auth_header = response.headers['WWW-Authenticate']
                if HttpBearerChallenge.is_bearer_challenge(auth_header):
                    challenge = HttpBearerChallenge(response.request.url, auth_header)
                    ChallengeCache.set_challenge_for_url(response.request.url, challenge)
                    self.set_authorization_header(request, challenge)
        return request

    def set_authorization_header(self, request, challenge):
        auth = self._callback(
            challenge.get_authorization_server(),
            challenge.get_resource(),
            challenge.get_scope())
        request.headers['Authorization'] = '{} {}'.format(auth[0], auth[1])

class KeyVaultAuthentication(Authentication):

    def __init__(self, authorization_callback):
        super(KeyVaultAuthentication, self).__init__()
        self.auth = KeyVaultAuthBase(authorization_callback)
        self._callback = authorization_callback
        
    def signed_session(self):
        session = super(KeyVaultAuthentication, self).signed_session()
        session.auth = self.auth
        return session
