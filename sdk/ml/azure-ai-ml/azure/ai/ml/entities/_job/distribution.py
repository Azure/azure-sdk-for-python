# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=unused-argument

from typing import Dict, Optional, Union

from azure.ai.ml._restclient.v2023_04_01_preview.models import (
    DistributionConfiguration as RestDistributionConfiguration,
)
from azure.ai.ml._restclient.v2023_04_01_preview.models import DistributionType as RestDistributionType
from azure.ai.ml._restclient.v2023_04_01_preview.models import Mpi as RestMpi
from azure.ai.ml._restclient.v2023_04_01_preview.models import PyTorch as RestPyTorch
from azure.ai.ml._restclient.v2023_04_01_preview.models import TensorFlow as RestTensorFlow
from azure.ai.ml._restclient.v2023_04_01_preview.models import Ray as RestRay
from azure.ai.ml.constants import DistributionType
from azure.ai.ml.entities._mixins import RestTranslatableMixin
from azure.ai.ml._utils._experimental import experimental

SDK_TO_REST = {
    DistributionType.MPI: RestDistributionType.MPI,
    DistributionType.TENSORFLOW: RestDistributionType.TENSOR_FLOW,
    DistributionType.PYTORCH: RestDistributionType.PY_TORCH,
    DistributionType.RAY: RestDistributionType.RAY,
}


class DistributionConfiguration(RestTranslatableMixin):
    def __init__(self, **kwargs) -> None:
        self.type = None

    @classmethod
    def _from_rest_object(
        cls, obj: Optional[Union[RestDistributionConfiguration, Dict]]
    ) -> "DistributionConfiguration":
        """This function works for distribution property of a Job object and of a Component object()

        Distribution of Job when returned by MFE, is a RestDistributionConfiguration

        Distribution of Component when returned by MFE, is a Dict.
        e.g. {'type': 'Mpi', 'process_count_per_instance': '1'}

        So in the job distribution case, we need to call as_dict() first and get type from "distribution_type" property.
        In the componenet case, we need to extract type from key "type"
        """
        if obj is None:
            return None

        data = obj
        if isinstance(obj, RestDistributionConfiguration):
            data = obj.as_dict()

        type_str = data.pop("distribution_type", None) or data.pop("type", None)
        klass = DISTRIBUTION_TYPE_MAP[type_str.lower()]
        return klass(**data)

    def __eq__(self, other) -> bool:
        if not isinstance(other, DistributionConfiguration):
            return NotImplemented
        return self._to_rest_object() == other._to_rest_object()


class MpiDistribution(DistributionConfiguration):
    """MPI distribution configuration.

    :param process_count_per_instance: Number of processes per MPI node.
    :type process_count_per_instance: int
    :ivar type: Specifies the type of distribution. Set automatically to "mpi" for this class.
    :vartype type: str
    """

    def __init__(self, *, process_count_per_instance: Optional[int] = None, **kwargs):
        super().__init__(**kwargs)
        self.type = DistributionType.MPI
        self.process_count_per_instance = process_count_per_instance

    def _to_rest_object(self) -> RestMpi:
        return RestMpi(process_count_per_instance=self.process_count_per_instance)


class PyTorchDistribution(DistributionConfiguration):
    """PyTorch distribution configuration.

    :param process_count_per_instance: Number of processes per node.
    :type process_count_per_instance: int
    :ivar type: Specifies the type of distribution. Set automatically to "pytorch" for this class.
    :vartype type: str
    """

    def __init__(self, *, process_count_per_instance: Optional[int] = None, **kwargs):
        super().__init__(**kwargs)
        self.type = DistributionType.PYTORCH
        self.process_count_per_instance = process_count_per_instance

    def _to_rest_object(self) -> RestPyTorch:
        return RestPyTorch(process_count_per_instance=self.process_count_per_instance)


class TensorFlowDistribution(DistributionConfiguration):
    """TensorFlow distribution configuration.

    :vartype distribution_type: str or ~azure.mgmt.machinelearningservices.models.DistributionType
    :ivar parameter_server_count: Number of parameter server tasks.
    :vartype parameter_server_count: int
    :ivar worker_count: Number of workers. If not specified, will default to the instance count.
    :vartype worker_count: int
    :ivar type: Specifies the type of distribution. Set automatically to "tensorflow" for this class.
    :vartype type: str
    """

    def __init__(self, *, parameter_server_count: Optional[int] = 0, worker_count: Optional[int] = None, **kwargs):
        super().__init__(**kwargs)
        self.type = DistributionType.TENSORFLOW
        self.parameter_server_count = parameter_server_count
        self.worker_count = worker_count

    def _to_rest_object(self) -> RestTensorFlow:
        return RestTensorFlow(parameter_server_count=self.parameter_server_count, worker_count=self.worker_count)


@experimental
class RayDistribution(DistributionConfiguration):
    """Ray distribution configuration.

    :vartype distribution_type: str or ~azure.mgmt.machinelearningservices.models.DistributionType
    :ivar port: The port of the head ray process.
    :vartype port: int
    :ivar address: The address of Ray head node.
    :vartype address: str
    :ivar include_dashboard: Provide this argument to start the Ray dashboard GUI.
    :vartype include_dashboard: bool
    :ivar dashboard_port: The port to bind the dashboard server to.
    :vartype dashboard_port: int
    :ivar head_node_additional_args: Additional arguments passed to ray start in head node.
    :vartype head_node_additional_args: str
    :ivar worker_node_additional_args: Additional arguments passed to ray start in worker node.
    :vartype worker_node_additional_args: str
    :ivar type: Specifies the type of distribution. Set automatically to "Ray" for this class.
    :vartype type: str
    """

    def __init__(
        self,
        *,
        port: Optional[int] = None,
        address: Optional[str] = None,
        include_dashboard: Optional[bool] = None,
        dashboard_port: Optional[int] = None,
        head_node_additional_args: Optional[str] = None,
        worker_node_additional_args: Optional[str] = None,
        **kwargs
    ):
        super().__init__(**kwargs)
        self.type = DistributionType.RAY

        self.port = port
        self.address = address
        self.include_dashboard = include_dashboard
        self.dashboard_port = dashboard_port
        self.head_node_additional_args = head_node_additional_args
        self.worker_node_additional_args = worker_node_additional_args

    def _to_rest_object(self) -> RestRay:
        return RestRay(
            port=self.port,
            address=self.address,
            include_dashboard=self.include_dashboard,
            dashboard_port=self.dashboard_port,
            head_node_additional_args=self.head_node_additional_args,
            worker_node_additional_args=self.worker_node_additional_args,
        )


DISTRIBUTION_TYPE_MAP = {
    DistributionType.MPI: MpiDistribution,
    DistributionType.TENSORFLOW: TensorFlowDistribution,
    DistributionType.PYTORCH: PyTorchDistribution,
    DistributionType.RAY: RayDistribution,
}
