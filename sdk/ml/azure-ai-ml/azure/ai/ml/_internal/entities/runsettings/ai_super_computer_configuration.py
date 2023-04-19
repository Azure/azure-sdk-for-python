# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from typing import Dict, List, Optional

from ....entities._job.job_resource_configuration import BaseProperty


class PascalCaseProperty(BaseProperty):
    _KEY_MAPPING = {}

    def items(self):
        result = []
        for key, value in super().items():
            if key.lower() in self._KEY_MAPPING:
                key = self._KEY_MAPPING[key.lower()]
            result.append((key, value))
        return result


class AISuperComputerStorageReferenceConfiguration(PascalCaseProperty):
    _KEY_MAPPING = {
        "container_name": "ContainerName",
        "relative_path": "RelativePath",
    }

    def __init__(
        self,
        container_name: str,
        relative_path: str,
        **kwargs,
    ):
        """
        :param container_name: The name of the ai-super-computer storage container.
        :type container_name: str
        :param relative_path: The path on the ai-super-computer storage container.
        :type relative_path: str
        """
        super().__init__(**kwargs)
        self.container_name = container_name
        self.relative_path = relative_path


class AISuperComputerScalePolicy(PascalCaseProperty):
    _KEY_MAPPING = {
        "auto_scale_instance_type_count_set": "AutoScaleInstanceTypeCountSet",
        "auto_scale_interval_in_sec": "AutoScaleIntervalInSec",
        "max_instance_type_count": "MaxInstanceTypeCount",
        "min_instance_type_count": "MinInstanceTypeCount",
    }

    def __init__(
        self,
        auto_scale_instance_type_count_set: Optional[List[int]] = None,
        auto_scale_interval_in_sec: Optional[int] = None,
        max_instance_type_count: Optional[int] = None,
        min_instance_type_count: Optional[int] = None,
        **kwargs,
    ):
        """
        :param auto_scale_instance_type_count_set: The list of instance type counts available
        for elastically scaling the job. Assume currentInstanceTypeCount = 4 and
        autoScaleInstanceTypeCountSet = [2,4,8], the job will automatically scale down as 8->4->2
        when less capacity is available, and scale up as 2->4->8 when more capacity is available.
        The value should be a list of integers in ascending order.
        :type auto_scale_instance_type_count_set: List[int]
        :param auto_scale_interval_in_sec: The minimum interval in seconds between job autoscaling.
        You are recommended to set the autoScaleIntervalInSec longer than the checkpoint interval,
        to make sure at least one checkpoint is saved before auto-scaling of the job.
        :type auto_scale_interval_in_sec: int
        :param max_instance_type_count: The maximum instance type count.
        :type max_instance_type_count: int
        :param min_instance_type_count: The minimum instance type count.
        :type min_instance_type_count: int
        """
        super().__init__(**kwargs)
        self.auto_scale_instance_type_count_set = auto_scale_instance_type_count_set
        self.auto_scale_interval_in_sec = auto_scale_interval_in_sec
        self.max_instance_type_count = max_instance_type_count
        self.min_instance_type_count = min_instance_type_count


class AISuperComputerConfiguration(PascalCaseProperty):  # pylint: disable=too-many-instance-attributes
    """A class to manage AI Super Computer Configuration."""

    _KEY_MAPPING = {
        "instance_type": "InstanceType",
        "instance_types": "InstanceTypes",
        "image_version": "ImageVersion",
        "location": "Location",
        "locations": "Locations",
        "ai_super_computer_storage_data": "AISuperComputerStorageData",
        "interactive": "Interactive",
        "scale_policy": "ScalePolicy",
        "virtual_cluster_arm_id": "VirtualClusterArmId",
        "tensorboard_log_directory": "TensorboardLogDirectory",
        "ssh_public_key": "SSHPublicKey",
        "ssh_public_keys": "SSHPublicKeys",
        "enable_azml_int": "EnableAzmlInt",
        "priority": "Priority",
        "sla_tier": "SLATier",
        "suspend_on_idle_time_hours": "SuspendOnIdleTimeHours",
        "user_alias": "UserAlias",
    }

    def __init__(
        self,
        instance_type: Optional[str] = None,
        instance_types: Optional[List[str]] = None,
        image_version: Optional[str] = None,
        location: Optional[str] = None,
        locations: Optional[List[str]] = None,
        ai_super_computer_storage_data: Optional[Dict[str, AISuperComputerStorageReferenceConfiguration]] = None,
        interactive: Optional[bool] = None,
        scale_policy: Optional[AISuperComputerScalePolicy] = None,
        virtual_cluster_arm_id: Optional[str] = None,
        tensorboard_log_directory: Optional[str] = None,
        ssh_public_key: Optional[str] = None,
        ssh_public_keys: Optional[List[str]] = None,
        enable_azml_int: Optional[bool] = None,
        priority: Optional[str] = None,
        sla_tier: Optional[str] = None,
        suspend_on_idle_time_hours: Optional[int] = None,
        user_alias: Optional[str] = None,
        **kwargs,
    ):
        """
        :param instance_type: The class of compute to be used. The list of instance types is
        available in https://singularitydocs.azurewebsites.net/docs/overview/instance_types/
        :type instance_type: str
        :param instance_types: The class of compute to be used. The list of instance types is
        available in https://singularitydocs.azurewebsites.net/docs/overview/instance_types/
        :type instance_types: List[str]
        :param image_version: The image to use in ai-super-computer.  Currently only a limited set of predefined
        images are supported.
        :type image_version: str
        :param location: The location (region) where the job will run. The workspace region is used
        if neither location nor locations is specified.
        :type location: str
        :param locations: The location (region) where the job will run. The workspace region is used
        if neither location nor locations is specified.
        :type locations: List[str]
        :param ai_super_computer_storage_data: All of the AI SuperComputer storage data sources to
        be made available to the run based on the configurations.
        :type ai_super_computer_storage_data: Dict[str, AISuperComputerStorageReferenceConfiguration]
        :param interactive: Specifies whether the job should be interactive. Interactive jobs will
        start the requested nodes, but not run a command.
        :type interactive: bool
        :param scale_policy: The elasticity options for a job. By leveraging elastic training,
        the job will automatically scale up when there is extra capacity available,
        and automatically scale down when resources are gradually called back.
        :type scale_policy: AISuperComputerScalePolicy
        :param virtual_cluster_arm_id: The ARM Resource Id for the Virtual Cluster to submit the
        job to.
        :type virtual_cluster_arm_id: str
        :param tensorboard_log_directory: The directory where the Tensorboard logs will be written.
        :type tensorboard_log_directory: str
        :param ssh_public_key: The SSH Public Key to use when enabling SSH access to the job.
        If not specified, username/password auth will be enabled.
        :type ssh_public_key: str
        :param ssh_public_keys: The SSH Public Key to use when enabling SSH access to the job.
        If not specified, username/password auth will be enabled.
        :type ssh_public_keys: List[str]
        :param enable_azml_int: Specifies whether the job should include the azml_int utility
        :type enable_azml_int: bool
        :param priority: The priority of the job. The default value is Medium.
        :type priority: str
        :param sla_tier: The SLA tier of the job. The default value is Standard.
        :type sla_tier: str
        :param suspend_on_idle_time_hours: Minimum idle time before run gets automatically suspended
        (in hours).
        :type suspend_on_idle_time_hours: int
        :param user_alias: User alias, used for naming mount paths.
        :type user_alias: str
        """
        super().__init__(**kwargs)
        self.instance_type = instance_type
        self.instance_types = instance_types
        self.image_version = image_version
        self.location = location
        self.locations = locations
        self.ai_super_computer_storage_data = ai_super_computer_storage_data
        self.interactive = interactive
        self.scale_policy = scale_policy
        self.virtual_cluster_arm_id = virtual_cluster_arm_id
        self.tensorboard_log_directory = tensorboard_log_directory
        self.ssh_public_key = ssh_public_key
        self.ssh_public_keys = ssh_public_keys
        self.enable_azml_int = enable_azml_int
        self.priority = priority
        self.sla_tier = sla_tier
        self.suspend_on_idle_time_hours = suspend_on_idle_time_hours
        self.user_alias = user_alias
