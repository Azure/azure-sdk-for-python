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
# breaking-change / changelog output). Class names and semantic values (type strings, defaults)
# are compared exactly; only the member-name position is normalized to snake_case, because the
# `types` TypedDicts expose wire names (e.g. `serviceTreeId`) while the `models` classes expose
# the Python attribute names (e.g. `service_tree_id`).
#
# There is one additional case: the emitter only generates a `TypedDict` for a model that is
# reachable as request input. When a model stops being used as input (e.g. it becomes
# output-only), its `TypedDict` disappears from `types` while the real class stays in `models`.
# That is not an API removal, but the sibling `models` module reports no change at all, so the
# match-based rule above cannot suppress it. Such class removals are dropped when the class is
# still present in the sibling `models` module of the current API surface.
# --------------------------------------------------------------------------------------------

import re

# Mirrors BreakingChangeType.REMOVED_OR_RENAMED_CLASS; duplicated as a literal to keep this
# post-processing checker free of a dependency on the tracker module.
_REMOVED_OR_RENAMED_CLASS = "RemovedOrRenamedClass"


def _to_snake_case(name):
    if not isinstance(name, str):
        return name
    name = re.sub(r"(.)([A-Z][a-z]+)", r"\1_\2", name)
    name = re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", name)
    return name.lower()


def _hashable(value):
    # Change tuples may carry list arguments (e.g. parameter-ordering changes); convert them to
    # tuples so the resulting match key can live in a set.
    if isinstance(value, list):
        return tuple(_hashable(item) for item in value)
    return value


class ShadowTypesModuleChecker:
    def run_check(
        self,
        breaking_changes: list,
        features_added: list,
        *,
        diff: dict,
        stable_nodes: dict,
        current_nodes: dict,
        **kwargs
    ) -> tuple[list, list]:
        def _sibling_models_module(module_name):
            if not isinstance(module_name, str):
                return None
            if module_name != "types" and not module_name.endswith(".types"):
                return None
            return module_name[: -len("types")] + "models"

        def _match_key(change, module):
            # Key is (change_type, module, class_name, [member_name], *rest). The class name
            # (args[0]) and any trailing semantic values are compared exactly; only the member
            # name (args[1]) is normalized so that `types` wire names match `models` attribute
            # names.
            args = change[3:]
            normalized_args = tuple(
                _hashable(_to_snake_case(arg) if index == 1 else arg) for index, arg in enumerate(args)
            )
            return (change[1], module) + normalized_args

        def _still_in_models(change, sibling_models):
            # The `types` TypedDict for a model is only emitted while that model is reachable as
            # request input. Its disappearance is not an API removal when the class itself is
            # still exposed by the sibling `models` module.
            if change[1] != _REMOVED_OR_RENAMED_CLASS:
                return False
            class_name = change[3]
            return class_name in current_nodes.get(sibling_models, {}).get("class_nodes", {})

        def _filter(changes_list):
            # Pre-index the match key of every change once so each `types` entry can be checked
            # with a single O(1) set lookup instead of rescanning the whole list (avoids O(n^2)).
            candidate_keys = {_match_key(change, change[2]) for change in changes_list if len(change) > 3}
            result = []
            for change in changes_list:
                sibling_models = _sibling_models_module(change[2])
                # Drop a `types` entry only when the sibling `models` module reports the same
                # change. A module-level change (len <= 3) has no class to match, so keep it.
                if (
                    sibling_models is not None
                    and len(change) > 3
                    and (
                        _match_key(change, sibling_models) in candidate_keys or _still_in_models(change, sibling_models)
                    )
                ):
                    continue
                result.append(change)
            return result

        return _filter(breaking_changes), _filter(features_added)
