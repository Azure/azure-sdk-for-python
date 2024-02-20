# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
from typing import List, Optional

from ....entities._job.job_resource_configuration import BaseProperty


class ITPResourceConfiguration(BaseProperty):
    """ITP resource configuration."""

    def __init__(
        self,
        gpu_count: Optional[int] = None,
        cpu_count: Optional[int] = None,
        memory_request_in_gb: Optional[int] = None,
        **kwargs
    ):
        """
        :param gpu_count: Gpu count Defines how many gpu cores a single node gpu job will use.
        Default value is 1.
        :type gpu_count: int
        :param cpu_count: Cpu count defines how many cpu cores that a single node cpu job will use.
        Default value is 1.
        :type cpu_count: int
        :param memory_request_in_gb: Memory request defines how much GB memory a single node job
        will request. Default value is 0 which means we will automatically calculate it for user.
        :type memory_request_in_gb: int
        """
        super().__init__(**kwargs)
        self.gpu_count = gpu_count
        self.cpu_count = cpu_count
        self.memory_request_in_gb = memory_request_in_gb


class ITPPriorityConfiguration(BaseProperty):
    """ITP priority configuration."""

    def __init__(
        self,
        job_priority: Optional[int] = None,
        is_preemptible: Optional[bool] = None,
        node_count_set: Optional[List[int]] = None,
        scale_interval: Optional[int] = None,
        **kwargs
    ):
        """
        :param job_priority: The priority of a job. Default value is 200. User can set it to
        100~200. Any value larger than 200 or less than 100 will be treated as 200.
        in azureml.components
        :type job_priority: int
        :param is_preemptible: Whether to preempt extra compute resources beyond the VC quota.
        Default value is false.
        in azureml.components
        :type is_preemptible: bool
        :param node_count_set: Node count set determines how compute auto-scale nodes. The value
        should be a list of integers in ascending order. And Only available when IsPreemptible is
        true.
        :type node_count_set: List[int]
        :param scale_interval: Scale interval in min.
        :type scale_interval: int
        """
        super().__init__(**kwargs)
        self.job_priority = job_priority
        self.is_preemptible = is_preemptible
        self.node_count_set = node_count_set
        self.scale_interval = scale_interval


class ITPInteractiveConfiguration(BaseProperty):
    """ITP interactive configuration."""

    def __init__(
        self,
        is_ssh_enabled: Optional[bool] = None,
        ssh_public_key: Optional[str] = None,
        is_i_python_enabled: Optional[bool] = None,
        is_tensor_board_enabled: Optional[bool] = None,
        interactive_port: Optional[int] = None,
        **kwargs
    ):
        """
        :param is_ssh_enabled: Whether to enable SSH for interactive development.
        Default value is false.
        :type is_ssh_enabled: bool
        :param ssh_public_key: SSH public key.
        :type ssh_public_key: str
        :param is_i_python_enabled: Is iPython enabled.
        :type is_i_python_enabled: bool
        :param is_tensor_board_enabled: Whether to enable TensorBoard. Default value is false.

        :type is_tensor_board_enabled: bool
        :param interactive_port: Allows user to specify a different interactive port. Available
        value from 40000 to 49999.
        :type interactive_port: int
        """
        super().__init__(**kwargs)
        self.is_ssh_enabled = is_ssh_enabled
        self.ssh_public_key = ssh_public_key
        self.is_i_python_enabled = is_i_python_enabled
        self.is_tensor_board_enabled = is_tensor_board_enabled
        self.interactive_port = interactive_port


class ITPRetrySettings(BaseProperty):
    def __init__(self, max_retry_count=None, **kwargs):
        super().__init__(**kwargs)
        self.max_retry_count = max_retry_count


class ITPConfiguration(BaseProperty):
    """ITP configuration."""

    def __init__(
        self,
        resource_configuration: Optional[ITPResourceConfiguration] = None,
        priority_configuration: Optional[ITPPriorityConfiguration] = None,
        interactive_configuration: Optional[ITPInteractiveConfiguration] = None,
        retry: Optional[ITPRetrySettings] = None,
        **kwargs
    ):
        """
        :param resource_configuration: Resource requirement for the compute.

        :type resource_configuration: ITPResourceConfiguration
        :param priority_configuration: Priority requirement for the compute.

        :type priority_configuration: ITPPriorityConfiguration
        :param interactive_configuration: Interactive configuration when trying to access the
        compute.
        :type interactive_configuration: ITPInteractiveConfiguration
        """
        self.resource_configuration = resource_configuration or ITPResourceConfiguration()
        self.priority_configuration = priority_configuration or ITPPriorityConfiguration()
        self.interactive_configuration = interactive_configuration or ITPInteractiveConfiguration()
        self.retry = retry or ITPRetrySettings()
        super().__init__(**kwargs)
