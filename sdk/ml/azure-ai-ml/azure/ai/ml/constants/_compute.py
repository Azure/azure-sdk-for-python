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
