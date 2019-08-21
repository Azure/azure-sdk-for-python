# ------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------

from .utils import parse_connection_string

class AppConfigConnectionStringCredential(object):
    """
    Parse the app configuration service connection string and store the host, id, secret information.
        """

    def __init__(self, connection_string):
        self.host, self.credential, self.secret = parse_connection_string(
            connection_string
        )

