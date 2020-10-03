# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

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
        self.subscription_key = subscription_key  # type: str
        self.api_key = api_key  # type: str
