#---------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
#---------------------------------------------------------------------------------------------

try:
    import urllib.parse as parse
except ImportError:
    import urlparse as parse # pylint: disable=import-error


class HttpBearerChallenge(object):

    def __init__(self, request_uri, challenge):
        """ Parses an HTTP WWW-Authentication Bearer challenge from a server. """
        self.source_authority = self._validate_request_uri(request_uri)
        self.source_uri = request_uri
        self._parameters = {}

        trimmed_challenge = self._validate_challenge(challenge)

        # split trimmed challenge into comma-separated name=value pairs. Values are expected
        # to be surrounded by quotes which are stripped here.
        for item in trimmed_challenge.split(','):
            # process name=value pairs
            comps = item.split('=')
            if len(comps) == 2:
                key = comps[0].strip(' "')
                value = comps[1].strip(' "')
                if key:
                    self._parameters[key] = value

        # minimum set of parameters
        if not self._parameters:
            raise ValueError('Invalid challenge parameters')

        # must specify authorization or authorization_uri
        if 'authorization' not in self._parameters and 'authorization_uri' not in self._parameters:
            raise ValueError('Invalid challenge parameters')

    # pylint: disable=no-self-use
    @staticmethod
    def is_bearer_challenge(authentication_header):
        """ Tests whether an authentication header is a Bearer challenge.
        :param authentication_header: the authentication header to test
        rtype: bool """
        if not authentication_header:
            return False

        return authentication_header.strip().startswith('Bearer ')

    def get_value(self, key):
        return self._parameters.get(key)

    def get_authorization_server(self):
        """ Returns the URI for the authorization server if present, otherwise empty string. """
        value = ''
        for key in ['authorization_uri', 'authorization']:
            value = self.get_value(key) or ''
            if value:
                break
        return value

    def get_resource(self):
        """ Returns the resource if present, otherwise empty string. """
        return self.get_value('resource') or ''

    def get_scope(self):
        """ Returns the scope if present, otherwise empty string. """
        return self.get_value('scope') or ''

    # pylint: disable=no-self-use
    def _validate_challenge(self, challenge):
        """ Verifies that the challenge is a Bearer challenge and returns the key=value pairs. """
        bearer_string = 'Bearer '
        if not challenge:
            raise ValueError('Challenge cannot be empty')

        challenge = challenge.strip()
        if not challenge.startswith(bearer_string):
            raise ValueError('Challenge is not Bearer')

        return challenge[len(bearer_string):]

    # pylint: disable=no-self-use
    def _validate_request_uri(self, uri):
        """ Extracts the host authority from the given URI. """
        if not uri:
            raise ValueError('request_uri cannot be empty')

        uri = parse.urlparse(uri)
        if not uri.netloc:
            raise ValueError('request_uri must be an absolute URI')

        if uri.scheme.lower() not in ['http', 'https']:
            raise ValueError('request_uri must be HTTP or HTTPS')

        return uri.netloc
