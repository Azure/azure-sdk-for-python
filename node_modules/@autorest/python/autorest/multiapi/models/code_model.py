# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

from typing import Any, Dict, List, Optional
from pathlib import Path
from .client import Client
from .config import Config
from .operation_group import OperationGroup
from .operation_mixin_group import OperationMixinGroup
from .global_parameters import GlobalParameters
from ..utils import _get_default_api_version_from_list


class CodeModel:  # pylint: disable=too-many-instance-attributes
    def __init__(
        self,
        module_name: str,
        package_name: str,
        default_api_version: str,
        preview_mode: bool,
        default_version_metadata: Dict[str, Any],
        mod_to_api_version: Dict[str, str],
        version_path_to_metadata: Dict[Path, Dict[str, Any]],
        user_specified_default_api: Optional[str] = None,
    ):
        self.module_name = module_name
        self.package_name = package_name
        self.mod_to_api_version = mod_to_api_version
        self.default_api_version = default_api_version
        self.preview_mode = preview_mode
        self.azure_arm = default_version_metadata["client"]["azure_arm"]
        self.default_version_metadata = default_version_metadata
        self.version_path_to_metadata = version_path_to_metadata
        self.client = Client(
            self.azure_arm, default_version_metadata, version_path_to_metadata
        )
        self.config = Config(default_version_metadata)
        self.operation_mixin_group = OperationMixinGroup(
            version_path_to_metadata, default_api_version
        )
        self.global_parameters = GlobalParameters(
            default_version_metadata["global_parameters"]
        )
        self.user_specified_default_api = user_specified_default_api

    @property
    def operation_groups(self) -> List[OperationGroup]:
        operation_groups: List[OperationGroup] = []
        for version_path, metadata_json in self.version_path_to_metadata.items():
            if not metadata_json.get("operation_groups"):
                continue
            operation_groups_metadata = metadata_json["operation_groups"]
            for (
                operation_group_name,
                operation_group_class_name,
            ) in operation_groups_metadata.items():
                try:
                    operation_group = [
                        og for og in operation_groups if og.name == operation_group_name
                    ][0]
                except IndexError:
                    operation_group = OperationGroup(operation_group_name)
                    operation_groups.append(operation_group)
                operation_group.append_available_api(version_path.name)
                operation_group.append_api_class_name_pair(
                    version_path.name, operation_group_class_name
                )
        operation_groups.sort(key=lambda x: x.name)
        return operation_groups

    @property
    def host_variable_name(self) -> str:
        if self.client.parameterized_host_template_to_api_version:
            return "base_url"
        params = (
            self.global_parameters.parameters
            + self.global_parameters.service_client_specific_global_parameters
        )
        try:
            return next(p for p in params if p.name in ["endpoint", "base_url"]).name
        except StopIteration:
            return "_endpoint"

    @property
    def last_rt_list(self) -> Dict[str, str]:
        """Build the a mapping RT => API version if RT doesn't exist in latest detected API version.

        Example:
        last_rt_list = {
        'check_dns_name_availability': '2018-05-01'
        }

        There is one subtle scenario if PREVIEW mode is disabled:
        - RT1 available on 2019-05-01 and 2019-06-01-preview
        - RT2 available on 2019-06-01-preview
        - RT3 available on 2019-07-01-preview

        Then, if I put "RT2: 2019-06-01-preview" in the list, this means I have to make
        "2019-06-01-preview" the default for models loading (otherwise "RT2: 2019-06-01-preview" won't work).
        But this likely breaks RT1 default operations at "2019-05-01", with default models at "2019-06-01-preview"
        since "models" are shared for the entire set of operations groups (I wished models would be split by
        operation groups, but meh, that's not the case)

        So, until we have a smarter Autorest to deal with that, only preview RTs which do not share models with
        a stable RT can be added to this map. In this case, RT2 is out, RT3 is in.
        """

        def there_is_a_rt_that_contains_api_version(rt_dict, api_version):
            "Test in the given api_version is is one of those RT."
            for rt_api_version in rt_dict.values():
                if api_version in rt_api_version:
                    return True
            return False

        last_rt_list = {}

        # First let's map operation groups to their available APIs
        versioned_dict = {
            operation_group.name: operation_group.available_apis
            for operation_group in self.operation_groups
        }

        # Now let's also include mixins to their available APIs
        versioned_dict.update(
            {
                mixin_operation.name: mixin_operation.available_apis
                for mixin_operation in self.operation_mixin_group.mixin_operations
            }
        )
        for operation, api_versions_list in versioned_dict.items():
            local_default_api_version = _get_default_api_version_from_list(
                self.mod_to_api_version,
                api_versions_list,
                self.preview_mode,
                self.user_specified_default_api,
            )
            if local_default_api_version == self.default_api_version:
                continue
            # If some others RT contains "local_default_api_version", and
            # if it's greater than the future default, danger, don't profile it
            if (
                there_is_a_rt_that_contains_api_version(
                    versioned_dict, local_default_api_version
                )
                and local_default_api_version > self.default_api_version
            ):
                continue
            last_rt_list[operation] = local_default_api_version
        return last_rt_list

    @property
    def default_models(self):
        return sorted(
            {self.default_api_version}
            | {versions for _, versions in self.last_rt_list.items()}
        )
