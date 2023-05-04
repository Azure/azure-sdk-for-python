# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
from abc import ABC
from typing import Union

from azure.ai.ml._restclient.v2023_04_01_preview.models import (
    BayesianSamplingAlgorithm as RestBayesianSamplingAlgorithm,
)
from azure.ai.ml._restclient.v2023_04_01_preview.models import GridSamplingAlgorithm as RestGridSamplingAlgorithm
from azure.ai.ml._restclient.v2023_04_01_preview.models import RandomSamplingAlgorithm as RestRandomSamplingAlgorithm
from azure.ai.ml._restclient.v2023_04_01_preview.models import SamplingAlgorithm as RestSamplingAlgorithm
from azure.ai.ml._restclient.v2023_04_01_preview.models import SamplingAlgorithmType
from azure.ai.ml.entities._mixins import RestTranslatableMixin


class SamplingAlgorithm(ABC, RestTranslatableMixin):
    def __init__(self) -> None:
        self.type = None

    @classmethod
    def _from_rest_object(cls, obj: RestSamplingAlgorithm) -> "SamplingAlgorithm":
        if not obj:
            return None

        sampling_algorithm = None
        if obj.sampling_algorithm_type == SamplingAlgorithmType.RANDOM:
            sampling_algorithm = RandomSamplingAlgorithm._from_rest_object(obj)  # pylint: disable=protected-access

        if obj.sampling_algorithm_type == SamplingAlgorithmType.GRID:
            sampling_algorithm = GridSamplingAlgorithm._from_rest_object(obj)  # pylint: disable=protected-access

        if obj.sampling_algorithm_type == SamplingAlgorithmType.BAYESIAN:
            sampling_algorithm = BayesianSamplingAlgorithm._from_rest_object(obj)  # pylint: disable=protected-access

        return sampling_algorithm


class RandomSamplingAlgorithm(SamplingAlgorithm):
    """Random Sampling Algorithm.

    :ivar type: Specifies the type of sampling algorithm. Set automatically to "random" for this class.
    :vartype type: str
    :param logbase: A positive number or e in string format to be used as base for log
        based random sampling.
    :type logbase: Union[float, str]
    :param rule: The specific type of random algorithm. Possible values include: "random",
        "sobol".
    :type rule: str
    :param seed: An integer to use as the seed for random number generation.
    :type seed: int
    """

    def __init__(
        self,
        *,
        rule: str = None,
        seed: int = None,
        logbase: Union[float, str] = None,
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

    :ivar type: Specifies the type of sampling algorithm. Set automatically to "grid" for this class.
    :vartype type: str
    """

    def __init__(self) -> None:
        super().__init__()
        self.type = SamplingAlgorithmType.GRID.lower()

    # pylint: disable=no-self-use
    def _to_rest_object(self) -> RestGridSamplingAlgorithm:
        return RestGridSamplingAlgorithm()

    @classmethod
    # pylint: disable=unused-argument
    def _from_rest_object(cls, obj: RestGridSamplingAlgorithm) -> "GridSamplingAlgorithm":
        return cls()


class BayesianSamplingAlgorithm(SamplingAlgorithm):
    """Bayesian Sampling Algorithm.

    :ivar type: Specifies the type of sampling algorithm. Set automatically to "bayesian" for this class.
    :vartype type: str
    """

    def __init__(self):
        super().__init__()
        self.type = SamplingAlgorithmType.BAYESIAN.lower()

    # pylint: disable=no-self-use
    def _to_rest_object(self) -> RestBayesianSamplingAlgorithm:
        return RestBayesianSamplingAlgorithm()

    @classmethod
    # pylint: disable=unused-argument
    def _from_rest_object(cls, obj: RestBayesianSamplingAlgorithm) -> "BayesianSamplingAlgorithm":
        return cls()
