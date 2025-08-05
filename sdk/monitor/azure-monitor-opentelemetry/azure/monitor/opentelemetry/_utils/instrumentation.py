# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License in the project root for
# license information.
# --------------------------------------------------------------------------

from __future__ import annotations

from logging import getLogger
from typing import Collection

from packaging.requirements import InvalidRequirement, Requirement

from opentelemetry.util._importlib_metadata import (
    Distribution,
    PackageNotFoundError,
    version,
)

logger = getLogger(__name__)

# --------------------Instrumentation------------------------------

# The below classes/functions are vendored from upstream OpenTelemetry Python due to being experimental.
# Due to possible breaking changes in the upstream code, we have decided to vendor this code

# TODO: Remove this vendored code once the upstream code is stable and released.
# Original breaking PR: https://github.com/open-telemetry/opentelemetry-python-contrib/pull/3202
# Tracking issue: https://github.com/open-telemetry/opentelemetry-python-contrib/issues/3434

class DependencyConflict:
    required: str | None = None
    found: str | None = None
    # The following fields are used when an instrumentation requires any of a set of dependencies rather than all.
    required_any: list[str] | None = None
    found_any: list[str] | None = None

    def __init__(
        self,
        required: str | None = None,
        found: str | None = None,
        required_any: list[str] | None = None,
        found_any: list[str] | None = None
    ):
        self.required = required
        self.found = found
        self.required_any = required_any
        self.found_any = found_any

    def __str__(self):
        if not self.required and (self.required_any or self.found_any):
            return (f'DependencyConflict: requested any of the following: "{self.required_any}" '
                    f'but found: "{self.found_any}"')
        return f'DependencyConflict: requested: "{self.required}" but found: "{self.found}"'


def get_dist_dependency_conflicts(
    dist: Distribution,
) -> DependencyConflict | None:
    instrumentation_deps = []
    instrumentation_any_deps = []
    extra = "extra"
    instruments = "instruments"
    instruments_any = "instruments-any"
    instruments_marker = {extra: instruments}
    instruments_any_marker = {extra: instruments_any}
    if dist.requires:
        for dep in dist.requires:
            if extra not in dep or instruments not in dep and instruments_any not in dep:
                continue

            req = Requirement(dep)
            if req.marker.evaluate(instruments_marker):  # type: ignore
                instrumentation_deps.append(req)
            if req.marker.evaluate(instruments_any_marker):  # type: ignore
                instrumentation_any_deps.append(req)

    return get_dependency_conflicts(instrumentation_deps, instrumentation_any_deps)


def get_dependency_conflicts(
    deps: Collection[str | Requirement],
    deps_any: Collection[str | Requirement]
    | None = None,
) -> DependencyConflict | None:
    for dep in deps:
        if isinstance(dep, Requirement):
            req = dep
        else:
            try:
                req = Requirement(dep)
            except InvalidRequirement as exc:
                logger.warning(
                    'error parsing dependency, reporting as a conflict: "%s" - %s',
                    dep,
                    exc,
                )
                return DependencyConflict(dep)

        try:
            dist_version = version(req.name)
        except PackageNotFoundError:
            return DependencyConflict(dep)  # type: ignore

        if not req.specifier.contains(dist_version):
            return DependencyConflict(dep, f"{req.name} {dist_version}")  # type: ignore

    if deps_any:
        return _get_dependency_conflicts_any(deps_any)
    return None

def _get_dependency_conflicts_any(
    deps_any: Collection[str | Requirement],
) -> DependencyConflict | None:
    if not deps_any:
        return None
    is_dependency_conflict = True
    required_any: list[str] = []
    found_any: list[str] = []
    for dep in deps_any:
        if isinstance(dep, Requirement):
            req = dep
        else:
            try:
                req = Requirement(dep)
            except InvalidRequirement as exc:
                logger.warning(
                    'error parsing dependency, reporting as a conflict: "%s" - %s',
                    dep,
                    exc,
                )
                return DependencyConflict(dep)

        try:
            dist_version = version(req.name)
        except PackageNotFoundError:
            required_any.append(str(dep))
            continue

        if req.specifier.contains(dist_version):
            # Since only one of the instrumentation_any dependencies is required, there is no dependency conflict.
            is_dependency_conflict = False
            break
        # If the version does not match, add it to the list of unfulfilled requirement options.
        required_any.append(str(dep))
        found_any.append(f"{req.name} {dist_version}")

    if is_dependency_conflict:
        return DependencyConflict(
            required_any=required_any,
            found_any=found_any,
        )
    return None
