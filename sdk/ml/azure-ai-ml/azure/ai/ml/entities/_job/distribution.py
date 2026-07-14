# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=unused-argument

from typing import Any, Dict, Optional, Union

from azure.ai.ml._restclient.arm_ml_service.models import (
    DistributionConfiguration as RestDistributionConfiguration,
)
from azure.ai.ml._restclient.arm_ml_service.models import Mpi as RestMpi
from azure.ai.ml._restclient.arm_ml_service.models import PyTorch as RestPyTorch
from azure.ai.ml._restclient.arm_ml_service.models import TensorFlow as RestTensorFlow
from azure.ai.ml._utils._experimental import experimental
from azure.ai.ml._utils.utils import camel_to_snake
from azure.ai.ml.constants import DistributionType
from azure.ai.ml.entities._mixins import RestTranslatableMixin


class DistributionConfiguration(RestTranslatableMixin):
    """Distribution configuration for a component or job.

    This class is not meant to be instantiated directly. Instead, use one of its subclasses.
    """

    def __init__(self, **kwargs: Any) -> None:
        self.type: Any = None

    @classmethod
    def _from_rest_object(
        cls, obj: Optional[Union[RestDistributionConfiguration, Dict]]
    ) -> Optional["DistributionConfiguration"]:
        """Constructs a DistributionConfiguration object from a REST object

        This function works for distribution property of a Job object and of a Component object()

        Distribution of Job when returned by MFE, is a RestDistributionConfiguration

        Distribution of Component when returned by MFE, is a Dict.
        e.g. {'type': 'Mpi', 'process_count_per_instance': '1'}

        So in the job distribution case, we need to call as_dict() first and get type from "distribution_type" property.
        In the componenet case, we need to extract type from key "type"


        :param obj: The object to translate
        :type obj: Optional[Union[RestDistributionConfiguration, Dict]]
        :return: The distribution configuration
        :rtype: DistributionConfiguration
        """
        if obj is None:
            return None

        if isinstance(obj, dict):
            data = obj
        else:
            data = obj.as_dict()

        # The distribution may arrive as a msrest model (snake_case ``as_dict()``), a shared
        # arm_ml_service hybrid model (camelCase ``as_dict()``), or a component dict (snake_case with a
        # ``type`` key). Normalize every key to snake_case so the discriminator lookup and the
        # ``klass(**data)`` construction below work regardless of the source casing.
        data = {camel_to_snake(key): value for key, value in data.items()}

        type_str = data.pop("distribution_type", None) or data.pop("type", None)
        klass = DISTRIBUTION_TYPE_MAP[type_str.lower()]
        res: DistributionConfiguration = klass(**data)
        return res

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, DistributionConfiguration):
            return NotImplemented
        res: bool = self._to_rest_object() == other._to_rest_object()
        return res


class MpiDistribution(DistributionConfiguration):
    """MPI distribution configuration.

    :keyword process_count_per_instance: The number of processes per node.
    :paramtype process_count_per_instance: Optional[int]
    :ivar type: Specifies the type of distribution. Set automatically to "mpi" for this class.
    :vartype type: str

    .. admonition:: Example:

        .. literalinclude:: ../samples/ml_samples_misc.py
            :start-after: [START mpi_distribution_configuration]
            :end-before: [END mpi_distribution_configuration]
            :language: python
            :dedent: 8
            :caption: Configuring a CommandComponent with an MpiDistribution.
    """

    def __init__(self, *, process_count_per_instance: Optional[int] = None, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.type = DistributionType.MPI
        self.process_count_per_instance = process_count_per_instance

    def _to_rest_object(self) -> RestMpi:
        return RestMpi(process_count_per_instance=self.process_count_per_instance)


class PyTorchDistribution(DistributionConfiguration):
    """PyTorch distribution configuration.

    :keyword process_count_per_instance: The number of processes per node.
    :paramtype process_count_per_instance: Optional[int]
    :ivar type: Specifies the type of distribution. Set automatically to "pytorch" for this class.
    :vartype type: str

    .. admonition:: Example:

        .. literalinclude:: ../samples/ml_samples_misc.py
            :start-after: [START pytorch_distribution_configuration]
            :end-before: [END pytorch_distribution_configuration]
            :language: python
            :dedent: 8
            :caption: Configuring a CommandComponent with a PyTorchDistribution.
    """

    def __init__(self, *, process_count_per_instance: Optional[int] = None, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.type = DistributionType.PYTORCH
        self.process_count_per_instance = process_count_per_instance

    def _to_rest_object(self) -> RestPyTorch:
        return RestPyTorch(process_count_per_instance=self.process_count_per_instance)


class TensorFlowDistribution(DistributionConfiguration):
    """TensorFlow distribution configuration.

    :vartype distribution_type: str or ~azure.mgmt.machinelearningservices.models.DistributionType
    :keyword parameter_server_count: The number of parameter server tasks. Defaults to 0.
    :paramtype parameter_server_count: Optional[int]
    :keyword worker_count: The number of workers. Defaults to the instance count.
    :paramtype worker_count: Optional[int]
    :ivar parameter_server_count: Number of parameter server tasks.
    :vartype parameter_server_count: int
    :ivar worker_count: Number of workers. If not specified, will default to the instance count.
    :vartype worker_count: int
    :ivar type: Specifies the type of distribution. Set automatically to "tensorflow" for this class.
    :vartype type: str

    .. admonition:: Example:

        .. literalinclude:: ../samples/ml_samples_misc.py
            :start-after: [START tensorflow_distribution_configuration]
            :end-before: [END tensorflow_distribution_configuration]
            :language: python
            :dedent: 8
            :caption: Configuring a CommandComponent with a TensorFlowDistribution.
    """

    def __init__(
        self, *, parameter_server_count: Optional[int] = 0, worker_count: Optional[int] = None, **kwargs: Any
    ) -> None:
        super().__init__(**kwargs)
        self.type = DistributionType.TENSORFLOW
        self.parameter_server_count = parameter_server_count
        self.worker_count = worker_count

    def _to_rest_object(self) -> RestTensorFlow:
        return RestTensorFlow(
            parameter_server_count=self.parameter_server_count,
            worker_count=self.worker_count,
        )


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
        **kwargs: Any
    ):
        super().__init__(**kwargs)
        self.type = DistributionType.RAY

        self.port = port
        self.address = address
        self.include_dashboard = include_dashboard
        self.dashboard_port = dashboard_port
        self.head_node_additional_args = head_node_additional_args
        self.worker_node_additional_args = worker_node_additional_args

    def _to_rest_object(self) -> RestDistributionConfiguration:
        # ``Ray`` is not modeled on the shared arm_ml_service client. Build the wire dict directly (omitting
        # None fields to match the legacy msrest ``Ray.serialize()`` output) and deserialize it into the arm
        # ``DistributionConfiguration`` hybrid so it serializes byte-identically inside an arm job envelope.
        wire: Dict[str, Any] = {"distributionType": "Ray"}
        if self.port is not None:
            wire["port"] = self.port
        if self.address is not None:
            wire["address"] = self.address
        if self.include_dashboard is not None:
            wire["includeDashboard"] = self.include_dashboard
        if self.dashboard_port is not None:
            wire["dashboardPort"] = self.dashboard_port
        if self.head_node_additional_args is not None:
            wire["headNodeAdditionalArgs"] = self.head_node_additional_args
        if self.worker_node_additional_args is not None:
            wire["workerNodeAdditionalArgs"] = self.worker_node_additional_args
        return RestDistributionConfiguration._deserialize(wire, [])  # pylint: disable=protected-access


DISTRIBUTION_TYPE_MAP = {
    DistributionType.MPI: MpiDistribution,
    DistributionType.TENSORFLOW: TensorFlowDistribution,
    DistributionType.PYTORCH: PyTorchDistribution,
    DistributionType.RAY: RayDistribution,
}
