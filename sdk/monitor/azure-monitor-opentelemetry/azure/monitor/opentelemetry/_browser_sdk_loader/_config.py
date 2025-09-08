# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License in the project root for
# license information.
# -------------------------------------------------------------------------

from typing import Optional


class BrowserSDKConfig:
    """Configuration class for the Browser SDK to be injected.

    This class handles the configuration settings for injecting the Browser SDK
    snippet into web responses.

    :param enabled: Whether snippet injection is enabled.
    :type enabled: bool
    :param connection_string: Application Insights connection string.
    :type connection_string: str
    :param config: Additional configuration options for the web SDK.
    :type config: Dict[str, Any]
    """

    def __init__(
        self,
        enabled: bool = True,
        connection_string: Optional[str] = None
    ) -> None:
        """Initialize the BrowserSDKConfig.

        :param enabled: Whether snippet injection is enabled.
        :type enabled: bool
        :param connection_string: Application Insights connection string.
        :type connection_string: str or None
        :param config: Additional configuration options for the web SDK.
        :rtype: None
        """
        self.enabled = enabled
        self.connection_string = connection_string or ""

    def to_dict(self) -> dict:
        """Convert the config to a dictionary for the web snippet.
        
        :return: Dictionary representation of the configuration.
        :rtype: dict
        """
        config_dict = {
            "cfg": {
                "connectionString": self.connection_string,
            }
        }
        return config_dict
