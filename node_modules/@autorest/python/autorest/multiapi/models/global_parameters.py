# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
from typing import Any, Dict, List
from .global_parameter import GlobalParameter
from .constant_global_parameter import ConstantGlobalParameter


def _convert_global_parameters(sync_metadata, async_metadata):
    global_parameters = [
        GlobalParameter(
            name=parameter_name,
            global_parameter_metadata_sync=gp_sync,
            global_parameter_metadata_async=async_metadata[parameter_name],
        )
        for parameter_name, gp_sync in sync_metadata.items()
    ]
    return global_parameters


class GlobalParameters:
    def __init__(
        self,
        global_parameters_metadata: Dict[str, Any],
    ):
        self.call = global_parameters_metadata["call"]
        self.global_parameters_metadata = global_parameters_metadata

    @property
    def service_client_specific_global_parameters(self) -> List[GlobalParameter]:
        """Return global params specific to multiapi service client + config
        api_version, endpoint (re-adding it in specific are), and profile
        """
        service_client_params_sync = self.global_parameters_metadata[
            "service_client_specific"
        ]["sync"]
        service_client_params_async = self.global_parameters_metadata[
            "service_client_specific"
        ]["async"]

        return _convert_global_parameters(
            service_client_params_sync, service_client_params_async
        )

    @property
    def parameters(self) -> List[GlobalParameter]:
        global_parameters_metadata_sync = self.global_parameters_metadata["sync"]
        global_parameters_metadata_async = self.global_parameters_metadata["async"]

        return _convert_global_parameters(
            global_parameters_metadata_sync, global_parameters_metadata_async
        )

    @property
    def constant_parameters(self) -> List[ConstantGlobalParameter]:
        return [
            ConstantGlobalParameter(constant_name, constant_value)
            for constant_name, constant_value in self.global_parameters_metadata[
                "constant"
            ].items()
        ]
