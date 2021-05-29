# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

from typing import Any
import six

class MetricsAdvisorKeyCredential(object):
    """Credential type used for authenticating to an Azure Metrics Advisor service.

    :param str subscription_key: The subscription key
    :param str api_key: The api key
    :raises: TypeError
    """

    def __init__(self, subscription_key, api_key):
        # type: (str, str) -> None
        if not (isinstance(subscription_key, six.string_types) and isinstance(api_key, six.string_types)):
            raise TypeError("key must be a string.")
        self._subscription_key = subscription_key  # type: str
        self._api_key = api_key  # type: str

    @property
    def subscription_key(self):
        # type: () -> str
        """The value of the subscription key.

        :rtype: str
        """
        return self._subscription_key

    @property
    def api_key(self):
        # type: () -> str
        """The value of the api key.

        :rtype: str
        """
        return self._api_key

    def update_key(self, **kwargs):
        # type: (**Any) -> None
        """Update the subscription key or the api key.

        This can be used when you've regenerated your service keys and want
        to update long-lived clients.

        :keyword str subscription_key: The subscription key
        :keyword str api_key: The api key
        :raises: ValueError or TypeError
        """
        subscription_key = kwargs.pop("subscription_key", None)
        api_key = kwargs.pop("api_key", None)
        if len(kwargs) > 0:
            raise TypeError("Got an unexpected keyword argument: {}".format(list(kwargs.keys())[0]))
        if subscription_key:
            if not isinstance(subscription_key, six.string_types):
                raise TypeError("The subscription_key used for updating must be a string.")
            self._subscription_key = subscription_key
        if api_key:
            if not isinstance(api_key, six.string_types):
                raise TypeError("The api_key used for updating must be a string.")
            self._api_key = api_key
