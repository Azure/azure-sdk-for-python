#!/usr/bin/env python

# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# --------------------------------------------------------------------------------------------
# This checker cleans up duplicate reporting caused by the generated `types` module.
# TypeSpec generated libraries emit a `types` module containing `TypedDict` input aliases
# that shadow the real models defined in the sibling `models` module. Because the same class
# name exists in both modules, changes such as adding a new model are reported twice, e.g.
# "Added model `Foo`" appears once for `...models` and once for `...types`.
#
# Since the `types` module is always a shadow of the `models` module, any change reported for
# the `types` module is a duplicate of the corresponding `models` change. This checker removes
# entries originating from a `types` module when the sibling `models` module exists.
# --------------------------------------------------------------------------------------------

import sys
import os
sys.path.append(os.path.abspath("../../scripts/breaking_changes_checker"))


class ShadowTypesModuleChecker:
    def run_check(self, breaking_changes: list, features_added: list, *, diff: dict, stable_nodes: dict, current_nodes: dict, **kwargs) -> tuple[list, list]:
        def _is_shadow_types_module(module_name) -> bool:
            # The module name is the third element of every reported change tuple.
            if not isinstance(module_name, str):
                return False
            if module_name != "types" and not module_name.endswith(".types"):
                return False
            # Only treat it as a shadow module when a sibling `models` module exists.
            sibling_models = module_name[: -len("types")] + "models"
            return sibling_models in current_nodes or sibling_models in stable_nodes

        breaking_changes_copy = [
            change for change in breaking_changes if not _is_shadow_types_module(change[2])
        ]
        features_added_copy = [
            change for change in features_added if not _is_shadow_types_module(change[2])
        ]
        return breaking_changes_copy, features_added_copy
