# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
from abc import ABC

from azure.ai.ml._restclient.v2022_02_01_preview.models import (
    BayesianSamplingAlgorithm as RestBayesianSamplingAlgorithm,
)
from azure.ai.ml._restclient.v2022_02_01_preview.models import GridSamplingAlgorithm as RestGridSamplingAlgorithm
from azure.ai.ml._restclient.v2022_02_01_preview.models import RandomSamplingAlgorithm as RestRandomSamplingAlgorithm
from azure.ai.ml._restclient.v2022_02_01_preview.models import SamplingAlgorithm as RestSamplingAlgorithm
from azure.ai.ml._restclient.v2022_02_01_preview.models import SamplingAlgorithmType
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
    """

    def __init__(
        self,
        *,
        rule=None,
        seed=None,
    ) -> None:
        super().__init__()
        self.type = SamplingAlgorithmType.RANDOM.lower()
        self.rule = rule
        self.seed = seed

    def _to_rest_object(self) -> RestRandomSamplingAlgorithm:
        return RestRandomSamplingAlgorithm(
            rule=self.rule,
            seed=self.seed,
        )

    @classmethod
    def _from_rest_object(cls, obj: RestRandomSamplingAlgorithm) -> "RandomSamplingAlgorithm":
        return cls(
            rule=obj.rule,
            seed=obj.seed,
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
