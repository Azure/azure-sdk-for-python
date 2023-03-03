# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------


class ComputeType(object):
    MANAGED = "managed"
    AMLCOMPUTE = "amlcompute"
    COMPUTEINSTANCE = "computeinstance"
    VIRTUALMACHINE = "virtualmachine"
    KUBERNETES = "kubernetes"
    ADF = "DataFactory"
    SYNAPSESPARK = "synapsespark"


class ComputeTier(object):
    LOWPRIORITY = "low_priority"
    DEDICATED = "dedicated"


class IdentityType(object):
    SYSTEM_ASSIGNED = "system_assigned"
    USER_ASSIGNED = "user_assigned"
    BOTH = "system_assigned,user_assigned"


class ComputeDefaults:
    VMSIZE = "STANDARD_DS3_V2"
    ADMIN_USER = "azureuser"
    MIN_NODES = 0
    MAX_NODES = 4
    IDLE_TIME = 1800
    PRIORITY = "Dedicated"


class CustomApplicationDefaults:
    """Class defining Custom Application Defaults."""

    TARGET_PORT = "target_port"
    "Attribute CustomApplicationDefaults.TARGET_PORT: Indicates target port of the custom application on the Compute Instance. (target_port)"

    PUBLISHED_PORT = "published_port"
    "Attribute CustomApplicationDefaults.PUBLISHED_PORT: Indicates published port of the custom application on the Compute Instance. (published_port)"

    PORT_MIN_VALUE = 1025
    "Attribute CustomApplicationDefaults.PORT_MIN_VALUE: Indicates minimum port value of the custom application on the Compute Instance. (1025)"

    PORT_MAX_VALUE = 65535
    "Attribute CustomApplicationDefaults.PORT_MAX_VALUE: Indicates maximum port value of the custom application on the Compute Instance. (65535)"

    DOCKER = "docker"
    "Attribute CustomApplicationDefaults.DOCKER: Indicates type of a docker custom application on the Compute Instance. (docker)"

    ENDPOINT_NAME = "connect"
    "Attribute CustomApplicationDefaults.DOCKER: Indicates endpoint name of the custom application on the Compute Instance. (connect)"


class ComputeSizeTier:
    """Class defining Compute size tiers."""

    AML_COMPUTE_DEDICATED = "amlComputeDedicatedVMSize"
    "Attribute ComputeSizeTier.AML_COMPUTE_DEDICATED: Indicates Compute Sizes should match Dedicated-tier Virtual Machines. (amlComputeDedicatedVmSize)"

    AML_COMPUTE_LOWPRIORITY = "amlComputeLowPriorityVMSize"
    "Attribute ComputeSizeTier.AML_COMPUTE_LOWPRIORITY Indicates Compute Sizes should match Low Priority-tier Virtual Machines. (amlcomputeLowPriorityVMSize)"

    COMPUTE_INSTANCE = "computeInstanceVMSize"
    "Attribute ComputeSizeTier.COMPUTE_INSTANCE Indicates Compute Sizes should match Compute Instance Virtual Machines.  (computeInstanceVMSize)"


DUPLICATE_APPLICATION_ERROR = "Value of {} must be unique across all custom applications."
INVALID_VALUE_ERROR = "Value of {} must be between {} and {}."
