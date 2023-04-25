# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=protected-access

from typing import Optional, Union

from azure.ai.ml._restclient.v2023_04_01_preview.models import ImageSweepSettings as RestImageSweepSettings
from azure.ai.ml._restclient.v2023_04_01_preview.models import SamplingAlgorithmType
from azure.ai.ml.entities._job.sweep.early_termination_policy import (
    BanditPolicy,
    EarlyTerminationPolicy,
    MedianStoppingPolicy,
    TruncationSelectionPolicy,
)
from azure.ai.ml.entities._mixins import RestTranslatableMixin


class ImageSweepSettings(RestTranslatableMixin):
    """Sweep settings for all AutoML Image Verticals.

    :param sampling_algorithm: Required. [Required] Type of the hyperparameter sampling
        algorithms. Possible values include: "Grid", "Random", "Bayesian".
    :type sampling_algorithm: Union[str, ~azure.mgmt.machinelearningservices.models.SamplingAlgorithmType.GRID,
    ~azure.mgmt.machinelearningservices.models.SamplingAlgorithmType.BAYESIAN,
    ~azure.mgmt.machinelearningservices.models.SamplingAlgorithmType.RANDOM]
    :param early_termination: Type of early termination policy.
    :type early_termination: Union[~azure.mgmt.machinelearningservices.models.BanditPolicy,
    ~azure.mgmt.machinelearningservices.models.MedianStoppingPolicy,
    ~azure.mgmt.machinelearningservices.models.TruncationSelectionPolicy]
    """

    def __init__(
        self,
        *,
        sampling_algorithm: Union[
            str, SamplingAlgorithmType.GRID, SamplingAlgorithmType.BAYESIAN, SamplingAlgorithmType.RANDOM
        ],
        early_termination: Optional[Union[BanditPolicy, MedianStoppingPolicy, TruncationSelectionPolicy]] = None,
    ):
        self.sampling_algorithm = sampling_algorithm
        self.early_termination = early_termination

    def _to_rest_object(self) -> RestImageSweepSettings:
        return RestImageSweepSettings(
            sampling_algorithm=self.sampling_algorithm,
            early_termination=self.early_termination._to_rest_object() if self.early_termination else None,
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
