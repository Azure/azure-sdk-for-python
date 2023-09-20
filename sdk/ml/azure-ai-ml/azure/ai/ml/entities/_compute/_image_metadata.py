# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------


class ImageMetadata:
    """Metadata about the operating system image for the compute instance.

    :param is_latest_os_image_version: Specifies if the compute instance is running on the latest OS image version.
    :type is_latest_os_image_version: bool
    :param current_image_version: Version of the current image.
    :type current_image_version: str
    :param latest_image_version: The latest image version.
    :type latest_image_version: str

    .. admonition:: Example:

        .. literalinclude:: ../samples/ml_samples_compute.py
            :start-after: [START image_metadata]
            :end-before: [END image_metadata]
            :language: python
            :dedent: 8
            :caption: Creating a ImageMetadata object.
    """

    def __init__(
        self, *, is_latest_os_image_version: bool, current_image_version: str, latest_image_version: str
    ) -> None:
        self._is_latest_os_image_version = is_latest_os_image_version
        self._current_image_version = current_image_version
        self._latest_image_version = latest_image_version

    @property
    def is_latest_os_image_version(self) -> bool:
        """Whether or not a compute instance is running on the latest OS image version.

        :return: Boolean indicating if the compute instance is running the latest OS image version.
        :rtype: bool
        """
        return self._is_latest_os_image_version

    @property
    def current_image_version(self) -> str:
        """The current OS image version number.

        :return: The current OS image version number.
        :rtype: str
        """
        return self._current_image_version

    @property
    def latest_image_version(self) -> str:
        """The latest OS image version number.

        :return: The latest OS image version number.
        :rtype: str
        """
        return self._latest_image_version
