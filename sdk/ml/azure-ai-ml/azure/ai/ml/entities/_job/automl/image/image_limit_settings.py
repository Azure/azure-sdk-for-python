# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from typing import Optional

from azure.ai.ml._restclient.v2023_04_01_preview.models import ImageLimitSettings as RestImageLimitSettings
from azure.ai.ml._utils.utils import from_iso_duration_format_mins, to_iso_duration_format_mins
from azure.ai.ml.entities._mixins import RestTranslatableMixin


class ImageLimitSettings(RestTranslatableMixin):
    r"""Limit settings for AutoML Image Verticals.

    ImageLimitSettings is a class that contains the following parameters:  max_concurrent_trials, max_trials, and \
    timeout_minutes.

    This is an optional configuration method to configure limits parameters such as timeouts etc.

        .. note::

            The number of concurrent runs is gated on the resources available in the specified compute target.
            Ensure that the compute target has the available resources for the desired concurrency.

    :keyword max_concurrent_trials: Maximum number of concurrent AutoML iterations, defaults to None.
    :paramtype  max_concurrent_trials: typing.Optional[int]
    :keyword max_trials: Represents the maximum number of trials (children jobs).
    :paramtype  max_trials: typing.Optional[int]
    :keyword timeout_minutes: AutoML job timeout. Defaults to None
    :paramtype  timeout_minutes: typing.Optional[int]
    :raises ValueError: If max_concurrent_trials is not None and is not a positive integer.
    :raises ValueError: If max_trials is not None and is not a positive integer.
    :raises ValueError: If timeout_minutes is not None and is not a positive integer.
    :return: ImageLimitSettings object.
    :rtype: ImageLimitSettings

    .. tip::
        It's a good practice to match max_concurrent_trials count with the number of nodes in the cluster.
        For example, if you have a cluster with 4 nodes, set max_concurrent_trials to 4.

    .. admonition:: Example:

        .. literalinclude:: ../samples/ml_samples_automl_image.py
                :start-after: [START automl.automl_image_job.image_limit_settings]
                :end-before: [END automl.automl_image_job.image_limit_settings]
                :language: python
                :dedent: 8
                :caption: Defining the limit settings for an automl image job.
    """

    def __init__(
        self,
        *,
        max_concurrent_trials: Optional[int] = None,
        max_trials: Optional[int] = None,
        timeout_minutes: Optional[int] = None,
    ) -> None:
        self.max_concurrent_trials = max_concurrent_trials
        self.max_trials = max_trials
        self.timeout_minutes = timeout_minutes

    def _to_rest_object(self) -> RestImageLimitSettings:
        """Convert ImageLimitSettings objects to a rest object.

        :return: A rest object of ImageLimitSettings objects.
        :rtype: RestImageLimitSettings
        """
        return RestImageLimitSettings(
            max_concurrent_trials=self.max_concurrent_trials,
            max_trials=self.max_trials,
            timeout=to_iso_duration_format_mins(self.timeout_minutes),
        )

    @classmethod
    def _from_rest_object(cls, obj: RestImageLimitSettings) -> "ImageLimitSettings":
        """Convert the rest object to a dict containing items to init the ImageLimitSettings objects.

        :param obj: Limit settings for the AutoML job in Rest format.
        :type obj: RestImageLimitSettings
        :return: Limit settings for an AutoML Image Vertical.
        :rtype: ImageLimitSettings
        """
        return cls(
            max_concurrent_trials=obj.max_concurrent_trials,
            max_trials=obj.max_trials,
            timeout_minutes=from_iso_duration_format_mins(obj.timeout),
        )

    def __eq__(self, other: object) -> bool:
        """Check equality between two ImageLimitSettings objects.

        This method check instances equality and returns True if both of
            the instances have the same attributes with the same values.

        :param other: Any object
        :type other: object
        :return: True or False
        :rtype: bool
        """
        if not isinstance(other, ImageLimitSettings):
            return NotImplemented

        return (
            self.max_concurrent_trials == other.max_concurrent_trials
            and self.max_trials == other.max_trials
            and self.timeout_minutes == other.timeout_minutes
        )

    def __ne__(self, other: object) -> bool:
        """Check inequality between two ImageLimitSettings objects.

        :param other: Any object
        :type other: object
        :return: True or False
        :rtype: bool
        """
        return not self.__eq__(other)
