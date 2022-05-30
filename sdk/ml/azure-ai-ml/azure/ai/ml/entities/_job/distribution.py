# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------


from typing import Optional, Union, Dict
from azure.ai.ml._restclient.v2022_02_01_preview.models import (
    Mpi as RestMpi,
    PyTorch as RestPyTorch,
    TensorFlow as RestTensorFlow,
    DistributionConfiguration as RestDistributionConfiguration,
    DistributionType as RestDistributionType,
)
from azure.ai.ml.entities._util import SnakeToPascalDescriptor
from azure.ai.ml.entities._mixins import RestTranslatableMixin
from azure.ai.ml.constants import DistributionType

SDK_TO_REST = {
    DistributionType.MPI: RestDistributionType.MPI,
    DistributionType.TENSORFLOW: RestDistributionType.TENSOR_FLOW,
    DistributionType.PYTORCH: RestDistributionType.PY_TORCH,
}


class DistributionConfiguration(RestTranslatableMixin):

    type = SnakeToPascalDescriptor(
        "distribution_type", transformer=lambda x: SDK_TO_REST.get(x, None), reverse_transformer=lambda x: x.lower()
    )

    def __init__(self) -> None:
        pass

    @classmethod
    def _from_rest_object(
        cls, obj: Optional[Union[RestDistributionConfiguration, Dict]]
    ) -> "DistributionConfiguration":
        """
        This function works for distribution property of a Job object and of a Component object()

        Distribution of Job when returned by MFE, is a RestDistributionConfiguration

        Distribution of Component when returned by MFE, is a Dict.
        e.g. {'type': 'Mpi', 'process_count_per_instance': '1'}

        So in the job distribution case, we need to call as_dist() first and get type from "distribution_type" property.
        In the componenet case, we need to extract type from key "type"

        """
        if obj is None:
            return None

        data = obj
        if isinstance(obj, RestDistributionConfiguration):
            data = obj.__dict__

        type_str = data.pop("distribution_type", None) or data.pop("type", None)
        cls = DISTRIBUTION_TYPE_MAP[type_str.lower()]
        return cls(**data)


class MpiDistribution(RestMpi, DistributionConfiguration):
    """MPI distribution configuration.

    :param process_count_per_instance: Number of processes per MPI node.
    :type process_count_per_instance: int
    """

    def __init__(self, *, process_count_per_instance: Optional[int] = None, **kwargs):

        super(MpiDistribution, self).__init__(process_count_per_instance=process_count_per_instance, **kwargs)


class PyTorchDistribution(RestPyTorch, DistributionConfiguration):
    """PyTorch distribution configuration.

    :param process_count_per_instance: Number of processes per node.
    :type process_count_per_instance: int
    """

    def __init__(self, *, process_count_per_instance: Optional[int] = None, **kwargs):

        super(PyTorchDistribution, self).__init__(process_count_per_instance=process_count_per_instance)


class TensorFlowDistribution(RestTensorFlow, DistributionConfiguration):
    """TensorFlow distribution configuration.

    :vartype distribution_type: str or ~azure.mgmt.machinelearningservices.models.DistributionType
    :ivar parameter_server_count: Number of parameter server tasks.
    :vartype parameter_server_count: int
    :ivar worker_count: Number of workers. If not specified, will default to the instance count.
    :vartype worker_count: int
    """

    def __init__(self, *, parameter_server_count: Optional[int] = 0, worker_count: Optional[int] = None, **kwargs):

        super(TensorFlowDistribution, self).__init__(
            parameter_server_count=parameter_server_count, worker_count=worker_count, **kwargs
        )


DISTRIBUTION_TYPE_MAP = {
    DistributionType.MPI: MpiDistribution,
    DistributionType.TENSORFLOW: TensorFlowDistribution,
    DistributionType.PYTORCH: PyTorchDistribution,
}
