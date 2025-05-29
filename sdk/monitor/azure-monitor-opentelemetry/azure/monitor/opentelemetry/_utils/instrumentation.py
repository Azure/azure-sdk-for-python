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

    def __init__(self, required: str | None, found: str | None = None):
        self.required = required
        self.found = found

    def __str__(self):
        return f'DependencyConflict: requested: "{self.required}" but found: "{self.found}"'


def get_dist_dependency_conflicts(
    dist: Distribution,
) -> DependencyConflict | None:
    instrumentation_deps = []
    extra = "extra"
    instruments = "instruments"
    instruments_marker = {extra: instruments}
    if dist.requires:
        for dep in dist.requires:
            if extra not in dep or instruments not in dep:
                continue

            req = Requirement(dep)
            if req.marker.evaluate(instruments_marker):  # type: ignore
                instrumentation_deps.append(req)

    return get_dependency_conflicts(instrumentation_deps)


def get_dependency_conflicts(
    deps: Collection[str | Requirement],
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
    return None
