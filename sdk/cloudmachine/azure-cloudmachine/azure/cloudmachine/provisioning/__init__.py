# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License in the project root for
# license information.
# --------------------------------------------------------------------------

from ._deployment import (
    CloudMachineDeployment,
    init_project,
    provision_project,
    deploy_project,
    shutdown_project
)

__all__ = [
    'CloudMachineDeployment'
]
