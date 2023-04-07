# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------


class ComputeType:
    """ComputeType is an enum-like class that defines the types of compute that can be used for training.

    ComputeType can be used to specify the compute type for a compute target. It can also be used to
    specify the compute type for a compute target that is being created.

    Valid values are "managed", "amlcompute", "computeinstance", "virtualmachine", "kubernetes", "DataFactory"
        , "synapsespark".
    """

    MANAGED = "managed"
    """Managed compute is a compute resource that is managed by Azure Machine Learning."""
    AMLCOMPUTE = "amlcompute"
    """AmlCompute is a compute resource that is managed by Azure Machine Learning."""
    COMPUTEINSTANCE = "computeinstance"
    """Compute Instance is a compute resource that is managed by Azure Machine Learning."""
    VIRTUALMACHINE = "virtualmachine"
    """Virtual Machine is a compute resource that is managed by Azure Machine Learning."""
    KUBERNETES = "kubernetes"
    """Kubernetes is a compute resource that is managed by Azure Machine Learning."""
    ADF = "DataFactory"
    """Data Factory is a compute resource that is managed by Azure Machine Learning."""
    SYNAPSESPARK = "synapsespark"
    """Synapse Spark is a compute resource that is managed by Azure Machine Learning."""


class ComputeTier:
    """ComputeTier is an enum-like class that defines the tiers of compute that can be used for training.

    ComputeTier can be used to specify the compute tier for a compute target. It can also be used to specify the compute
    tier for a compute target that is being created. Valid values are "lowpriority", "dedicated".
    """

    LOWPRIORITY = "low_priority"
    """LOWPRIORITY is a compute tier that is used for low priority compute targets."""
    DEDICATED = "dedicated"
    """DEDICATED is a compute tier that is used for dedicated compute targets."""


class IdentityType:
    """IdentityType is an enum-like class that defines the types of identity that can be used for compute.

    IdentityType can be used to specify the identity type for a compute target. It can also be used to specify the
    identity type for a compute target that is being created. Valid values are "system_assigned", "user_assigned",
    "both".
    """

    SYSTEM_ASSIGNED = "system_assigned"
    """SYSTEM_ASSIGNED is a compute identity type that is used for system assigned compute targets."""
    USER_ASSIGNED = "user_assigned"
    """USER_ASSIGNED is a compute identity type that is used for user assigned compute targets."""
    BOTH = "system_assigned,user_assigned"
    """BOTH is a compute identity type that is used for both system and user assigned compute targets."""


class ComputeDefaults:
    """Class defining Compute Defaults."""

    VMSIZE = "STANDARD_DS3_V2"
    """ComputeDefaults.VMSIZE: Indicates default VM size. (STANDARD_DS3_V2)
    """
    ADMIN_USER = "azureuser"
    """ComputeDefaults.ADMIN_USER: Indicates default admin user. (azureuser)
    """
    MIN_NODES = 0
    """ComputeDefaults.MIN_NODES: Indicates default minimum number of nodes. (0)
    """
    MAX_NODES = 4
    """ComputeDefaults.MAX_NODES: Indicates default maximum number of nodes. (4)
    """
    IDLE_TIME = 1800
    """ComputeDefaults.IDLE_TIME: Indicates default idle time. (1800)
    """
    PRIORITY = "Dedicated"
    """ComputeDefaults.PRIORITY: Indicates default priority. (Dedicated)
    """


class CustomApplicationDefaults:
    """Class defining Custom Application Defaults."""

    TARGET_PORT = "target_port"
    """CustomApplicationDefaults.TARGET_PORT: Indicates target port of the custom application on the Compute
      Instance. (target_port)
    """

    PUBLISHED_PORT = "published_port"
    """CustomApplicationDefaults.PUBLISHED_PORT: Indicates published port of the custom application on the Compute
      Instance. (published_port)
    """

    PORT_MIN_VALUE = 1025
    """CustomApplicationDefaults.PORT_MIN_VALUE: Indicates minimum port value of the custom application on the
      Compute Instance. (1025)
    """

    PORT_MAX_VALUE = 65535
    """CustomApplicationDefaults.PORT_MAX_VALUE: Indicates maximum port value of the custom application on the
      Compute Instance. (65535)
    """

    DOCKER = "docker"
    """CustomApplicationDefaults.DOCKER: Indicates type of a docker custom application on the Compute Instance. (docker)
    """

    ENDPOINT_NAME = "connect"
    """CustomApplicationDefaults.ENDPOINT_NAME: Indicates endpoint name of the custom application on the Compute
     Instance. (connect)
    """


class ComputeSizeTier:
    """Class defining Compute size tiers."""

    AML_COMPUTE_DEDICATED = "amlComputeDedicatedVMSize"
    """ComputeSizeTier.AML_COMPUTE_DEDICATED: Indicates Compute Sizes should match Dedicated-tier Virtual Machines.
    (amlComputeDedicatedVmSize)
    """

    AML_COMPUTE_LOWPRIORITY = "amlComputeLowPriorityVMSize"
    """ComputeSizeTier.AML_COMPUTE_LOWPRIORITY: Indicates Compute Sizes should match Low Priority-tier Virtual
     Machines. (amlcomputeLowPriorityVMSize)
    """

    COMPUTE_INSTANCE = "computeInstanceVMSize"
    """ComputeSizeTier.COMPUTE_INSTANCE: Indicates Compute Sizes should match Compute Instance Virtual Machines.
    (computeInstanceVMSize)
    """


DUPLICATE_APPLICATION_ERROR = "Value of {} must be unique across all custom applications."
INVALID_VALUE_ERROR = "Value of {} must be between {} and {}."
