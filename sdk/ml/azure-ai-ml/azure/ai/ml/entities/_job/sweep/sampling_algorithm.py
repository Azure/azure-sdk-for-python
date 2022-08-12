# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from azure.ai.ml._restclient.v2022_02_01_preview.models import (
    BayesianSamplingAlgorithm as RestBayesianSamplingAlgorithm,
)
from azure.ai.ml._restclient.v2022_02_01_preview.models import GridSamplingAlgorithm as RestGridSamplingAlgorithm
from azure.ai.ml._restclient.v2022_02_01_preview.models import RandomSamplingAlgorithm as RestRandomSamplingAlgorithm
from azure.ai.ml._restclient.v2022_02_01_preview.models import SamplingAlgorithm as RestSamplingAlgorithm
from azure.ai.ml._restclient.v2022_02_01_preview.models import SamplingAlgorithmType
from azure.ai.ml.entities._util import SnakeToPascalDescriptor


class SamplingAlgorithm:

    type = SnakeToPascalDescriptor(private_name="sampling_algorithm_type")

    def __init__(self) -> None:
        pass

    @classmethod
    def _from_rest_object(cls, rest_obj: RestSamplingAlgorithm) -> "SamplingAlgorithm":
        if not rest_obj:
            return None

        sampling_algorithm = None
        if rest_obj.sampling_algorithm_type == SamplingAlgorithmType.RANDOM:
            sampling_algorithm = RandomSamplingAlgorithm(**rest_obj.as_dict())

        if rest_obj.sampling_algorithm_type == SamplingAlgorithmType.GRID:
            sampling_algorithm = GridSamplingAlgorithm(**rest_obj.as_dict())

        if rest_obj.sampling_algorithm_type == SamplingAlgorithmType.BAYESIAN:
            sampling_algorithm = BayesianSamplingAlgorithm(**rest_obj.as_dict())

        return sampling_algorithm


class RandomSamplingAlgorithm(RestRandomSamplingAlgorithm, SamplingAlgorithm):
    def __init__(self, rule=None, seed=None, **kwargs) -> None:
        super().__init__(rule=rule, seed=seed, **kwargs)


class GridSamplingAlgorithm(RestGridSamplingAlgorithm, SamplingAlgorithm):
    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)


class BayesianSamplingAlgorithm(RestBayesianSamplingAlgorithm, SamplingAlgorithm):
    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
