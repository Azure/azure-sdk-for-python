# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
from azure.ai.ml._utils._experimental import experimental


@experimental
class ImageMetadata:
    """Metadata about the operating system image for this compute instance."""

    def __init__(self, *, is_latest_os_image_version: bool, current_image_version: str, latest_image_version: str):
        self._is_latest_os_image_version = is_latest_os_image_version
        self._current_image_version = current_image_version
        self._latest_image_version = latest_image_version

    @property
    def is_latest_os_image_version(self) -> bool:
        """Indicates whether a compute instance is running on the latest OS image version.

        return: State of whether the compute instance is running the latest OS image version.
        rtype: bool
        """
        return self._is_latest_os_image_version

    @property
    def current_image_version(self) -> str:
        """Indicates the current OS image version number.

        return: Current OS Image version number.
        rtype: str
        """
        return self._current_image_version

    @property
    def latest_image_version(self) -> str:
        """Indicates the latest OS image version number.

        return: Latest OS Image version number.
        rtype: str
        """
        return self._latest_image_version
