# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
from azure.ai.ml._utils._experimental import experimental

@experimental
class ImageMetadata:
    """ Metadata about the operating system image for this compute instance.
    """
    def __init__(self, *, is_latest_os_version: bool, current_os_version: str, latest_os_version: str):
        self._is_latest_os_version = is_latest_os_version
        self._current_os_version = current_os_version
        self._latest_os_version = latest_os_version

    @property
    def is_latest_os_version(self) -> bool:
        """
        Indicates whether a compute instance is running on the latest OS image version.

        return: State of whether the compute instance is running the latest OS image version.
        rtype: bool
        """
        return self._is_latest_os_version

    @property
    def current_os_version(self) -> str:
        """
        Indicates the current OS image version number.

        return: Current OS Image version number.
        rtype: str
        """
        return self._current_os_version

    @property
    def latest_os_version(self) -> str:
        """
        Indicates the latest OS image version number.

        return: Latest OS Image version number.
        rtype: str
        """
        return self._latest_os_version
