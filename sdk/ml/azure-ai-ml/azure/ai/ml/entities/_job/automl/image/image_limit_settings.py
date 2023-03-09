# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from typing import Optional

from azure.ai.ml._restclient.v2023_02_01_preview.models import ImageLimitSettings as RestImageLimitSettings
from azure.ai.ml._utils.utils import from_iso_duration_format_mins, to_iso_duration_format_mins
from azure.ai.ml.entities._mixins import RestTranslatableMixin


class ImageLimitSettings(RestTranslatableMixin):
    """Limit settings for all AutoML Image Verticals.

    :keyword max_concurrent_trials: Maximum number of concurrent AutoML iterations, defaults to None
    :paramtype  max_concurrent_trials: typing.Optional[int]
    :keyword max_trials: Represents the maximum number of trials (children jobs) that would be executed in parallel.
    :paramtype  max_trials: typing.Optional[int]
    :keyword timeout_minutes: AutoML job timeout, defaults to None
    :paramtype  timeout_minutes: typing.Optional[int]

    :raises ValueError: If max_concurrent_trials is not None and is not a positive integer.
    :raises ValueError: If max_trials is not None and is not a positive integer.
    :raises ValueError: If timeout_minutes is not None and is not a positive integer.
    :return: ImageLimitSettings object.
    :rtype: ImageLimitSettings

    .. tip::
        It's a good practice to match max_concurrent_trials count with the number of nodes in the cluster.

    .. note::
        The number of concurrent runs is gated on the resources available in the specified compute target.
        Ensure that the compute target has the available resources for the desired concurrency.

    .. remarks::

        ImageLimitSettings is an optional configuration method to configure limits parameters such as timeouts etc.


    **Example usage**

    .. code-block:: python
        :caption: Configuration of ImageLimitSettings

        from azure.ai.ml import automl

        # Create the AutoML job with the related factory-function.
        image_instance_segmentation_job = automl.image_instance_segmentation(
            compute=compute_name,
            experiment_name=exp_name,
            training_data=my_training_data_input,
            validation_data=my_validation_data_input,
            target_column_name="label",
            primary_metric="MeanAveragePrecision",
            tags={"my_custom_tag": "custom value"},
        )
        # Set the limits for the AutoML job.
        image_instance_segmentation_job.set_limits(
            max_trials=10,
            max_concurrent_trials=2,
        )

    .. seealso:: `Azure ML code samples <https://github.com/Azure/azureml-examples/tree/main/sdk>`_
    """

    def __init__(
        self,
        *,
        max_concurrent_trials: Optional[int] = None,
        max_trials: Optional[int] = None,
        timeout_minutes: Optional[int] = None,
    ):
        """Initialize an ImageLimitSettings object.

        Constructor for ImageLimitSettings for all AutoML Image Verticals.

        :keyword  max_concurrent_trials: Represents the maximum number of trials (children jobs) that would be \
            executed in parallel.
        :paramtype max_concurrent_trials: typing.Optional[int]
        :keyword max_trials: Maximum number of AutoML iterations, defaults to None
        :paramtype max_trials: typing.Optional[int]
        :keyword timeout_minutes: AutoML job timeout, defaults to None
        :paramtype timeout_minutes: typing.Optional[int]
        :raises ValueError: If max_concurrent_trials is not None and is not a positive integer.
        :raises ValueError: If max_trials is not None and is not a positive integer.
        :raises ValueError: If timeout_minutes is not None and is not a positive integer.

        :return: ImageLimitSettings object.
        :rtype: ImageLimitSettings
        """
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

        _extended_summary_

        :param other: ImageLimitSettings object
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

        :param other: ImageLimitSettings object
        :type other: object
        :return: True or False
        :rtype: bool
        """
        return not self.__eq__(other)
