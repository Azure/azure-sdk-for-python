# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
from abc import ABC
from typing import Any, Optional, Union, cast

from azure.ai.ml._restclient.v2023_08_01_preview.models import (
    BayesianSamplingAlgorithm as RestBayesianSamplingAlgorithm,
)
from azure.ai.ml._restclient.v2023_08_01_preview.models import GridSamplingAlgorithm as RestGridSamplingAlgorithm
from azure.ai.ml._restclient.v2023_08_01_preview.models import RandomSamplingAlgorithm as RestRandomSamplingAlgorithm
from azure.ai.ml._restclient.v2023_08_01_preview.models import SamplingAlgorithm as RestSamplingAlgorithm
from azure.ai.ml._restclient.v2023_08_01_preview.models import SamplingAlgorithmType
from azure.ai.ml.entities._mixins import RestTranslatableMixin


class SamplingAlgorithm(ABC, RestTranslatableMixin):
    """Base class for sampling algorithms.

    This class should not be instantiated directly. Instead, use one of its subclasses.
    """

    def __init__(self) -> None:
        self.type = None

    @classmethod
    def _from_rest_object(cls, obj: RestSamplingAlgorithm) -> Optional["SamplingAlgorithm"]:
        if not obj:
            return None

        sampling_algorithm: Any = None
        if obj.sampling_algorithm_type == SamplingAlgorithmType.RANDOM:
            sampling_algorithm = RandomSamplingAlgorithm._from_rest_object(obj)  # pylint: disable=protected-access

        if obj.sampling_algorithm_type == SamplingAlgorithmType.GRID:
            sampling_algorithm = GridSamplingAlgorithm._from_rest_object(obj)  # pylint: disable=protected-access

        if obj.sampling_algorithm_type == SamplingAlgorithmType.BAYESIAN:
            sampling_algorithm = BayesianSamplingAlgorithm._from_rest_object(obj)  # pylint: disable=protected-access

        return cast(Optional["SamplingAlgorithm"], sampling_algorithm)


class RandomSamplingAlgorithm(SamplingAlgorithm):
    """Random Sampling Algorithm.

    :keyword rule: The specific type of random algorithm. Accepted values are: "random" and "sobol".
    :type rule: str
    :keyword seed: The seed for random number generation.
    :paramtype seed: int
    :keyword logbase: A positive number or the number "e" in string format to be used as the base for log
        based random sampling.
    :paramtype logbase: Union[float, str]

    .. admonition:: Example:

        .. literalinclude:: ../samples/ml_samples_sweep_configurations.py
            :start-after: [START configure_sweep_job_random_sampling_algorithm]
            :end-before: [END configure_sweep_job_random_sampling_algorithm]
            :language: python
            :dedent: 8
            :caption: Assigning a random sampling algorithm for a SweepJob
    """

    def __init__(
        self,
        *,
        rule: Optional[str] = None,
        seed: Optional[int] = None,
        logbase: Optional[Union[float, str]] = None,
    ) -> None:
        super().__init__()
        self.type = SamplingAlgorithmType.RANDOM.lower()
        self.rule = rule
        self.seed = seed
        self.logbase = logbase

    def _to_rest_object(self) -> RestRandomSamplingAlgorithm:
        return RestRandomSamplingAlgorithm(
            rule=self.rule,
            seed=self.seed,
            logbase=self.logbase,
        )

    @classmethod
    def _from_rest_object(cls, obj: RestRandomSamplingAlgorithm) -> "RandomSamplingAlgorithm":
        return cls(
            rule=obj.rule,
            seed=obj.seed,
            logbase=obj.logbase,
        )


class GridSamplingAlgorithm(SamplingAlgorithm):
    """Grid Sampling Algorithm.

    .. admonition:: Example:

        .. literalinclude:: ../samples/ml_samples_sweep_configurations.py
            :start-after: [START configure_sweep_job_grid_sampling_algorithm]
            :end-before: [END configure_sweep_job_grid_sampling_algorithm]
            :language: python
            :dedent: 8
            :caption: Assigning a grid sampling algorithm for a SweepJob
    """

    def __init__(self) -> None:
        super().__init__()
        self.type = SamplingAlgorithmType.GRID.lower()

    def _to_rest_object(self) -> RestGridSamplingAlgorithm:
        return RestGridSamplingAlgorithm()

    @classmethod
    # pylint: disable=unused-argument
    def _from_rest_object(cls, obj: RestGridSamplingAlgorithm) -> "GridSamplingAlgorithm":
        return cls()


class BayesianSamplingAlgorithm(SamplingAlgorithm):
    """Bayesian Sampling Algorithm.

    .. admonition:: Example:

        .. literalinclude:: ../samples/ml_samples_sweep_configurations.py
            :start-after: [START configure_sweep_job_bayesian_sampling_algorithm]
            :end-before: [END configure_sweep_job_bayesian_sampling_algorithm]
            :language: python
            :dedent: 8
            :caption: Assigning a Bayesian sampling algorithm for a SweepJob
    """

    def __init__(self) -> None:
        super().__init__()
        self.type = SamplingAlgorithmType.BAYESIAN.lower()

    def _to_rest_object(self) -> RestBayesianSamplingAlgorithm:
        return RestBayesianSamplingAlgorithm()

    @classmethod
    # pylint: disable=unused-argument
    def _from_rest_object(cls, obj: RestBayesianSamplingAlgorithm) -> "BayesianSamplingAlgorithm":
        return cls()
