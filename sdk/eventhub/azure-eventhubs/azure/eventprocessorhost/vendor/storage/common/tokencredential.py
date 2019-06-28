# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

import requests


class TokenCredential(object):
    """
    Represents a token credential that is used to authorize HTTPS requests.
    The token can be updated by the user.

    :ivar str token:
        The authorization token. It can be set by the user at any point in a thread-safe way.
    """

    def __init__(self, initial_value=None):
        """
        :param initial_value: initial value for the token.
        """
        self.token = initial_value

    def signed_session(self, session=None):
        """
        Sign requests session with the token. This method is called every time a request is going on the wire.
        The user is responsible for updating the token with the preferred tool/SDK.
        In general there are two options:
            - override this method to update the token in a preferred way and set Authorization header on session
            - not override this method, and have a timer that triggers periodically to update the token on this class

        The second option is recommended as it tends to be more performance-friendly.

        :param session: The session to configure for authentication
        :type session: requests.Session
        :rtype: requests.Session
        """
        session = session or requests.Session()
        session.headers['Authorization'] = "Bearer {}".format(self.token)

        return session

    def token(self, new_value):
        """
        :param new_value: new value to be set as the token.
        """
        self.token = new_value