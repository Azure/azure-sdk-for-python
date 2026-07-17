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
# A `types` entry is only dropped when the sibling `models` module reports the *same* change
# (same change type and arguments, with the module substituted). This ensures we never silently
# drop a change that only exists on the `types` side (which would otherwise disappear from the
# breaking-change / changelog output). Member names are normalized to snake_case before
# comparison because the `types` TypedDicts expose wire names (e.g. `serviceTreeId`) while the
# `models` classes expose the Python attribute names (e.g. `service_tree_id`).
# --------------------------------------------------------------------------------------------

import re


def _to_snake_case(name):
    if not isinstance(name, str):
        return name
    name = re.sub(r"(.)([A-Z][a-z]+)", r"\1_\2", name)
    name = re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", name)
    return name.lower()


class ShadowTypesModuleChecker:
    def run_check(self, breaking_changes: list, features_added: list, *, diff: dict, stable_nodes: dict, current_nodes: dict, **kwargs) -> tuple[list, list]:
        def _sibling_models_module(module_name):
            if not isinstance(module_name, str):
                return None
            if module_name != "types" and not module_name.endswith(".types"):
                return None
            return module_name[: -len("types")] + "models"

        def _normalized_payload(change, module):
            # (change_type, module, *args) with member/class names normalized to snake_case so
            # that `types` wire names match the corresponding `models` attribute names.
            return (change[1], module) + tuple(_to_snake_case(arg) for arg in change[3:])

        def _is_shadow_duplicate(change, changes_list) -> bool:
            # The module name is the third element of every reported change tuple and the
            # class name (when present) is the fourth.
            sibling_models = _sibling_models_module(change[2])
            if sibling_models is None:
                return False
            if len(change) <= 3:
                # Module-level change with no class to match against; keep it to be safe.
                return False
            target = _normalized_payload(change, sibling_models)
            for candidate in changes_list:
                if candidate is change or candidate[2] != sibling_models:
                    continue
                if _normalized_payload(candidate, candidate[2]) == target:
                    return True
            return False

        breaking_changes_copy = [
            change for change in breaking_changes if not _is_shadow_duplicate(change, breaking_changes)
        ]
        features_added_copy = [
            change for change in features_added if not _is_shadow_duplicate(change, features_added)
        ]
        return breaking_changes_copy, features_added_copy
