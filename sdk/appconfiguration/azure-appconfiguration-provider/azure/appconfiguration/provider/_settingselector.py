# ------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------


class SettingSelector:
    """
    Selects a set of configuration settings from Azure App Configuration.

    :param key_filter: A filter to select configuration settings based on their keys.
    :type key_filter: str
    :param label_filter: A filter to select configuration settings based on their labels. Default is value is '\0'
    :type label_filter: str
    """

    def __init__(self, key_filter, label_filter="\0"):
        # type: (str, str) -> None
        self.key_filter = key_filter
        self.label_filter = label_filter
