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
# A `types` entry is only treated as a shadow duplicate when the sibling `models` module
# actually contains a class with the same name. This class-existence guard ensures we do not
# silently drop a change that only exists on the `types` side (a class with no `models`
# counterpart), which would otherwise disappear from the breaking-change / changelog output.
# --------------------------------------------------------------------------------------------


class ShadowTypesModuleChecker:
    def run_check(self, breaking_changes: list, features_added: list, *, diff: dict, stable_nodes: dict, current_nodes: dict, **kwargs) -> tuple[list, list]:
        def _sibling_models_module(module_name):
            if not isinstance(module_name, str):
                return None
            if module_name != "types" and not module_name.endswith(".types"):
                return None
            return module_name[: -len("types")] + "models"

        def _models_has_class(models_module, class_name) -> bool:
            if not isinstance(class_name, str):
                return False
            for nodes in (current_nodes, stable_nodes):
                module = nodes.get(models_module)
                if module and class_name in module.get("class_nodes", {}):
                    return True
            return False

        def _is_shadow_duplicate(change) -> bool:
            # The module name is the third element of every reported change tuple and the
            # class name (when present) is the fourth.
            sibling_models = _sibling_models_module(change[2])
            if sibling_models is None:
                return False
            if len(change) <= 3:
                # Module-level change with no class to match against; keep it to be safe.
                return False
            return _models_has_class(sibling_models, change[3])

        breaking_changes_copy = [
            change for change in breaking_changes if not _is_shadow_duplicate(change)
        ]
        features_added_copy = [
            change for change in features_added if not _is_shadow_duplicate(change)
        ]
        return breaking_changes_copy, features_added_copy
