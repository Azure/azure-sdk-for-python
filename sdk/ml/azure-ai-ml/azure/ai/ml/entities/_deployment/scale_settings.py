# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=protected-access

import logging
from abc import abstractmethod
from typing import Optional

from azure.ai.ml._restclient.v2023_04_01_preview.models import DefaultScaleSettings as RestDefaultScaleSettings
from azure.ai.ml._restclient.v2023_04_01_preview.models import OnlineScaleSettings as RestOnlineScaleSettings
from azure.ai.ml._restclient.v2023_04_01_preview.models import ScaleType
from azure.ai.ml._restclient.v2023_04_01_preview.models import (
    TargetUtilizationScaleSettings as RestTargetUtilizationScaleSettings,
)
from azure.ai.ml._utils.utils import camel_to_snake, from_iso_duration_format, to_iso_duration_format
from azure.ai.ml.entities._mixins import RestTranslatableMixin
from azure.ai.ml.exceptions import DeploymentException, ErrorCategory, ErrorTarget

module_logger = logging.getLogger(__name__)


class OnlineScaleSettings(RestTranslatableMixin):
    """Scale settings for online deployment.

    :param type: Type of the scale settings, allowed values are "default" and "target_utilization".
    :type type: str
    """

    def __init__(
        self,
        type: str,  # pylint: disable=redefined-builtin
        **kwargs,  # pylint: disable=unused-argument
    ):
        self.type = camel_to_snake(type)

    @abstractmethod
    def _to_rest_object(self) -> RestOnlineScaleSettings:
        pass

    def _merge_with(self, other: "OnlineScaleSettings") -> None:
        if other:
            self.type = other.type or self.type

    @classmethod
    def _from_rest_object(  # pylint: disable=arguments-renamed
        cls, settings: RestOnlineScaleSettings
    ) -> "OnlineScaleSettings":
        if settings.scale_type == "Default":
            return DefaultScaleSettings._from_rest_object(settings)
        if settings.scale_type == "TargetUtilization":
            return TargetUtilizationScaleSettings._from_rest_object(settings)

        msg = f"Unsupported online scale setting type {settings.type}."
        raise DeploymentException(
            message=msg,
            target=ErrorTarget.ONLINE_DEPLOYMENT,
            no_personal_data_message=msg,
            error_category=ErrorCategory.SYSTEM_ERROR,
        )


class DefaultScaleSettings(OnlineScaleSettings):
    """Default scale settings.

    :ivar type: Default scale settings type. Set automatically to "default" for this class.
    :vartype type: str
    """

    def __init__(self, **kwargs):
        super(DefaultScaleSettings, self).__init__(
            type=ScaleType.DEFAULT.value,  # pylint: disable=no-member
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
        return self.type.lower() == other.type.lower()

    def __ne__(self, other: object) -> bool:
        return not self.__eq__(other)


class TargetUtilizationScaleSettings(OnlineScaleSettings):
    """Auto scale settings.

    :param min_instances: Minimum number of the instances
    :type min_instances: int, optional
    :param max_instances: Maximum number of the instances
    :type max_instances: int, optional
    :param polling_interval: The polling interval in ISO 8691 format. Only supports duration with
     precision as low as Seconds.
    :type polling_interval: str
    :param target_utilization_percentage:
    :type target_utilization_percentage: int
    :ivar type: Target utilization scale settings type. Set automatically to "target_utilization" for this class.
    :vartype type: str
    """

    def __init__(
        self,
        *,
        min_instances: Optional[int] = None,
        max_instances: Optional[int] = None,
        polling_interval: Optional[int] = None,
        target_utilization_percentage: Optional[int] = None,
        **kwargs,
    ):
        super(TargetUtilizationScaleSettings, self).__init__(
            type=ScaleType.TARGET_UTILIZATION.value,  # pylint: disable=no-member
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
            self.type.lower() == other.type.lower()
            and self.min_instances == other.min_instances
            and self.max_instances == other.max_instances
            and self.polling_interval == other.polling_interval
            and self.target_utilization_percentage == other.target_utilization_percentage
        )

    def __ne__(self, other: object) -> bool:
        return not self.__eq__(other)
