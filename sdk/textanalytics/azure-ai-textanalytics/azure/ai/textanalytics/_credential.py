# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

import six


class SharedKeyCredential(object):
    """Credential type used for authenticating the client
    with a subscription key.

    :param str subscription_key: The subscription key to your Text Analytics
        or Cognitive Services account.
    """
    def __init__(self, subscription_key):
        if not isinstance(subscription_key, six.string_types):
            raise TypeError("Please provide the subscription key as a string.")
        self._subscription_key = subscription_key

    @property
    def subscription_key(self):
        """Returns the current value of subscription key.
        """
        return self._subscription_key

    def set_subscription_key(self, key):
        """Update the subscription key.

        This is intended to be used when you've regenerated your service subscription key
        and want to update long-lived clients.

        :param str key: The subscription key to your Text Analytics
            or Cognitive Services account.
        """
        self._subscription_key = key
