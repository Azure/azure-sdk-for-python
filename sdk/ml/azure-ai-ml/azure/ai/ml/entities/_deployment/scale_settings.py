# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from abc import abstractmethod
import logging
from azure.ai.ml._restclient.v2022_02_01_preview.models import (
    OnlineScaleSettings as RestOnlineScaleSettings,
    DefaultScaleSettings as RestDefaultScaleSettings,
    TargetUtilizationScaleSettings as RestTargetUtilizationScaleSettings,
    ScaleType,
)
from azure.ai.ml.entities._mixins import RestTranslatableMixin
from azure.ai.ml._utils.utils import (
    to_iso_duration_format,
    from_iso_duration_format,
    camel_to_snake,
)

from azure.ai.ml._ml_exceptions import DeploymentException, ErrorCategory, ErrorTarget

module_logger = logging.getLogger(__name__)


class OnlineScaleSettings(RestTranslatableMixin):
    """Scale settings for online deployment

    :param scale_type: Type of the scale settings, allowed values are "default" and "target_utilization".
    :type scale_type: str
    """

    def __init__(self, scale_type: str, **kwargs):
        self.scale_type = camel_to_snake(scale_type)

    @abstractmethod
    def _to_rest_object(self) -> RestOnlineScaleSettings:
        pass

    def _merge_with(self, other: "OnlineScaleSettings") -> None:
        if other:
            self.scale_type = other.scale_type or self.scale_type

    @classmethod
    def _from_rest_object(cls, settings: RestOnlineScaleSettings) -> "OnlineScaleSettings":
        if isinstance(settings, RestDefaultScaleSettings):
            return DefaultScaleSettings._from_rest_object(settings)
        elif isinstance(settings, RestTargetUtilizationScaleSettings):
            return TargetUtilizationScaleSettings._from_rest_object(settings)
        else:
            msg = f"Unsupported online scale setting type {settings.scale_type}."
            raise DeploymentException(
                message=msg,
                target=ErrorTarget.ONLINE_DEPLOYMENT,
                no_personal_data_message=msg,
                error_category=ErrorCategory.SYSTEM_ERROR,
            )


class DefaultScaleSettings(OnlineScaleSettings):
    """Default scale settings"""

    def __init__(self, **kwargs):
        super(DefaultScaleSettings, self).__init__(
            scale_type=ScaleType.DEFAULT.value,
        )

    def _to_rest_object(self) -> RestDefaultScaleSettings:
        return RestDefaultScaleSettings()

    @classmethod
    def _from_rest_object(cls, settings: RestDefaultScaleSettings) -> "DefaultScaleSettings":
        return DefaultScaleSettings()

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, DefaultScaleSettings):
            return NotImplemented
        if not other:
            return False
        # only compare mutable fields
        return self.scale_type.lower() == other.scale_type.lower()

    def __ne__(self, other: object) -> bool:
        return not self.__eq__(other)


class TargetUtilizationScaleSettings(OnlineScaleSettings):
    """Auto scale settings

    :param min_instances: Minimum number of the instances
    :type min_instances: int, optional
    :param max_instances: Maximum number of the instances
    :type max_instances: int, optional
    :param polling_interval: The polling interval in ISO 8691 format. Only supports duration with
     precision as low as Seconds.
    :type polling_interval: str
    :param target_utilization_percentage:
    :type target_utilization_percentage: int
    """

    def __init__(
        self,
        *,
        min_instances: int = None,
        max_instances: int = None,
        polling_interval: int = None,
        target_utilization_percentage: int = None,
        **kwargs,
    ):
        super(TargetUtilizationScaleSettings, self).__init__(
            scale_type=ScaleType.TARGET_UTILIZATION.value,
        )
        self.min_instances = min_instances
        self.max_instances = max_instances
        self.polling_interval = polling_interval
        self.target_utilization_percentage = target_utilization_percentage

    def _to_rest_object(self) -> RestTargetUtilizationScaleSettings:
        return RestTargetUtilizationScaleSettings(
            min_instances=self.min_instances,
            max_instances=self.max_instances,
            polling_interval=to_iso_duration_format(self.polling_interval),
            target_utilization_percentage=self.target_utilization_percentage,
        )

    def _merge_with(self, other: "TargetUtilizationScaleSettings") -> None:
        if other:
            super()._merge_with(other)
            self.min_instances = other.min_instances or self.min_instances
            self.max_instances = other.max_instances or self.max_instances
            self.polling_interval = other.polling_interval or self.polling_interval
            self.target_utilization_percentage = (
                other.target_utilization_percentage or self.target_utilization_percentage
            )

    @classmethod
    def _from_rest_object(cls, settings: RestTargetUtilizationScaleSettings) -> "TargetUtilizationScaleSettings":
        return cls(
            min_instances=settings.min_instances,
            max_instances=settings.max_instances,
            polling_interval=from_iso_duration_format(settings.polling_interval),
            target_utilization_percentage=settings.target_utilization_percentage,
        )

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, TargetUtilizationScaleSettings):
            return NotImplemented
        if not other:
            return False
        # only compare mutable fields
        return (
            self.scale_type.lower() == other.scale_type.lower()
            and self.min_instances == other.min_instances
            and self.max_instances == other.max_instances
            and self.polling_interval == other.polling_interval
            and self.target_utilization_percentage == other.target_utilization_percentage
        )

    def __ne__(self, other: object) -> bool:
        return not self.__eq__(other)
