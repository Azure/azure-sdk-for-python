# ------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------

from ._utils import parse_connection_string


class AppConfigConnectionStringCredential(object):
    """
    Parse the app configuration service connection string and store the host, id, secret information.

    :param connection_string: Connection String(one of the access keys of the Azure App Configuration resource)
        used to access the Azure App Configuration.
    :type connection_string: str
    """

    def __init__(self, connection_string):
        self.host, self.credential, self.secret = parse_connection_string(
            connection_string
        )
