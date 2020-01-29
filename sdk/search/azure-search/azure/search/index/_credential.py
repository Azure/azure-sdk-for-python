# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

import six


class SearchApiKeyCredential(object):
    """Credential type used for authenticating a SearchIndexClient
    with an API key.

    :param str api_key: An admin or query key for your Azure Search
        index.

    """

    def __init__(self, api_key):
        # type: (str) -> None
        if not isinstance(api_key, six.string_types):
            raise TypeError("api_key must be a string.")
        self._api_key = api_key  # type: str

    @property
    def api_key(self):
        """The value of the configured API key.
        """
        # type () -> str
        return self._api_key

    def update_key(self, key):
        """Update the API key.
        This cab be used when you've regenerated your service API key and want
        to update long-lived clients.

        :param str key: The API key to your Azure search account.
        """
        self._api_key = key
