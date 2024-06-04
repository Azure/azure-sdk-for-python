# The MIT License (MIT)
# Copyright (c) 2014 Microsoft Corporation

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

"""Authorization helper functions in the Azure Cosmos database service.
"""

import base64
from hashlib import sha256
import hmac
import warnings
import urllib.parse
from . import http_constants


def GetAuthorizationHeader(
        cosmos_client_connection, verb, path, resource_id_or_fullname, is_name_based, resource_type, headers
):
    warnings.warn("This method has been deprecated and will be removed from the SDK in a future release.",
                  DeprecationWarning)

    return _get_authorization_header(
        cosmos_client_connection, verb, path, resource_id_or_fullname, is_name_based, resource_type, headers)


def _get_authorization_header(
        cosmos_client_connection, verb, path, resource_id_or_fullname, is_name_based, resource_type, headers
):
    """Gets the authorization header.

    :param cosmos_client_connection.CosmosClient cosmos_client_connection:
    :param str verb:
    :param str path:
    :param str resource_id_or_fullname:
    :param bool is_name_based:
    :param str resource_type:
    :param dict headers:
    :return: The authorization headers.
    :rtype: str
    """
    # In the AuthorizationToken generation logic, lower casing of ResourceID is required
    # as rest of the fields are lower cased. Lower casing should not be done for named
    # based "ID", which should be used as is
    if resource_id_or_fullname is not None and not is_name_based:
        resource_id_or_fullname = resource_id_or_fullname.lower()

    if cosmos_client_connection.master_key:
        return __get_authorization_token_using_master_key(
            verb, resource_id_or_fullname, resource_type, headers, cosmos_client_connection.master_key
        )
    if cosmos_client_connection.resource_tokens:
        return __get_authorization_token_using_resource_token(
            cosmos_client_connection.resource_tokens, path, resource_id_or_fullname
        )

    return None


def __get_authorization_token_using_master_key(verb, resource_id_or_fullname, resource_type, headers, master_key):
    """Gets the authorization token using `master_key.

    :param str verb:
    :param str resource_id_or_fullname:
    :param str resource_type:
    :param dict headers:
    :param str master_key:
    :return: The authorization token.
    :rtype: dict

    """

    # decodes the master key which is encoded in base64
    key = base64.b64decode(master_key)

    # Skipping lower casing of resource_id_or_fullname since it may now contain "ID"
    # of the resource as part of the fullname
    text = "{verb}\n{resource_type}\n{resource_id_or_fullname}\n{x_date}\n{http_date}\n".format(
        verb=(verb.lower() or ""),
        resource_type=(resource_type.lower() or ""),
        resource_id_or_fullname=(resource_id_or_fullname or ""),
        x_date=headers.get(http_constants.HttpHeaders.XDate, "").lower(),
        http_date=headers.get(http_constants.HttpHeaders.HttpDate, "").lower(),
    )

    body = text.encode("utf-8")
    digest = hmac.new(key, body, sha256).digest()
    signature = base64.encodebytes(digest).decode("utf-8")

    master_token = "master"
    token_version = "1.0"
    return "type={type}&ver={ver}&sig={sig}".format(type=master_token, ver=token_version, sig=signature[:-1])


def __get_authorization_token_using_resource_token(resource_tokens, path, resource_id_or_fullname):
    """Get the authorization token using `resource_tokens`.

    :param dict resource_tokens:
    :param str path:
    :param str resource_id_or_fullname:
    :return: The authorization token.
    :rtype: dict

    """
    if resource_tokens:
        # For database account access(through GetDatabaseAccount API), path and
        # resource_id_or_fullname are '', so in this case we return the first token to be
        # used for creating the auth header as the service will accept any token in this case
        path = urllib.parse.unquote(path)
        if not path and not resource_id_or_fullname:
            for value in resource_tokens.values():
                return value

        if resource_tokens.get(resource_id_or_fullname):
            return resource_tokens[resource_id_or_fullname]

        path_parts = []
        if path:
            path_parts = [item for item in path.split("/") if item]
        resource_types = [
            "dbs",
            "colls",
            "docs",
            "sprocs",
            "udfs",
            "triggers",
            "users",
            "permissions",
            "attachments",
            "conflicts",
            "offers",
        ]

        # Get the last resource id or resource name from the path and get it's token from resource_tokens
        for i in range(len(path_parts), 1, -1):
            segment = path_parts[i - 1]
            sub_path = "/".join(path_parts[:i])
            if not segment in resource_types and sub_path in resource_tokens:
                return resource_tokens[sub_path]

    return None
