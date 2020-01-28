# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

import six


class TextAnalyticsApiKeyCredential(object):
    """Credential type used for authenticating the client
    with an API key.

    :param str api_key: The API key to your Text Analytics
        or Cognitive Services account.
    """
    def __init__(self, api_key):
        if not isinstance(api_key, six.string_types):
            raise TypeError("Please provide the API key as a string.")
        self._api_key = api_key

    @property
    def api_key(self):
        """Returns the current value of the API key.
        """
        return self._api_key

    def update_key(self, key):
        """Update the API key.

        This is intended to be used when you've regenerated your service API key
        and want to update long-lived clients.

        :param str key: The API key to your Text Analytics
            or Cognitive Services account.
        """
        self._api_key = key
