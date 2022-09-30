# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=protected-access

from typing import Union

from azure.ai.ml._restclient.v2022_10_01_preview.models import ImageSweepLimitSettings
from azure.ai.ml._restclient.v2022_10_01_preview.models import ImageSweepSettings as RestImageSweepSettings
from azure.ai.ml._restclient.v2022_10_01_preview.models import SamplingAlgorithmType
from azure.ai.ml.entities._job.sweep.early_termination_policy import EarlyTerminationPolicy
from azure.ai.ml.entities._mixins import RestTranslatableMixin


class ImageSweepSettings(RestTranslatableMixin):
    """Sweep settings for all AutoML Image Verticals.

    :param sampling_algorithm: Required. [Required] Type of the hyperparameter sampling
        algorithms. Possible values include: "Grid", "Random", "Bayesian".
    :type sampling_algorithm: str or ~azure.mgmt.machinelearningservices.models.SamplingAlgorithmType
    :param early_termination: Type of early termination policy.
    :type early_termination: ~azure.mgmt.machinelearningservices.models.EarlyTerminationPolicy
    """

    def __init__(
        self,
        *,
        sampling_algorithm: Union[str, SamplingAlgorithmType],
        early_termination: EarlyTerminationPolicy = None,
    ):
        self.sampling_algorithm = sampling_algorithm
        self.early_termination = early_termination

    def _to_rest_object(self) -> RestImageSweepSettings:
        return RestImageSweepSettings(
            limits=ImageSweepLimitSettings(),
            sampling_algorithm=self.sampling_algorithm,
            early_termination=self.early_termination._to_rest_object(),
        )

    @classmethod
    def _from_rest_object(cls, obj: RestImageSweepSettings) -> "ImageSweepSettings":

        return cls(
            sampling_algorithm=obj.sampling_algorithm,
            early_termination=EarlyTerminationPolicy._from_rest_object(obj.early_termination)
            if obj.early_termination
            else None,
        )

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, ImageSweepSettings):
            return NotImplemented

        return self.sampling_algorithm == other.sampling_algorithm and self.early_termination == other.early_termination

    def __ne__(self, other: object) -> bool:
        return not self.__eq__(other)
