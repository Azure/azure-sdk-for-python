# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
from __future__ import annotations

import os
import platform  # pylint: disable=unused-import
from dataclasses import dataclass, field
from importlib.metadata import Distribution, PackageNotFoundError

@dataclass(frozen=True, kw_only=True)
class PackageMetadata:
    name: str
    version: str

    @staticmethod
    def from_dist(dist_name: str) -> "PackageMetadata":
        try:
            ver = Distribution.from_name(dist_name).version
        except PackageNotFoundError:
            ver = ""

        return PackageMetadata(
            name=dist_name,
            version=ver,
        )


@dataclass(frozen=True, kw_only=True)
class RuntimeMetadata:
    python_version: str = field(default_factory=platform.python_version)
    platform: str = field(default_factory=platform.platform)
    host_name: str = ""
    replica_name: str = ""

    @staticmethod
    def from_aca_app_env() -> "RuntimeMetadata | None":
        host_name = os.environ.get("CONTAINER_APP_REVISION_FQDN")
        replica_name = os.environ.get("CONTAINER_APP_REPLICA_NAME")

        if not host_name and not replica_name:
            return None

        return RuntimeMetadata(
            host_name=host_name or "",
            replica_name=replica_name or "",
        )

    @staticmethod
    def resolve(host_name: str | None = None, replica_name: str | None = None) -> "RuntimeMetadata":
        runtime = RuntimeMetadata.from_aca_app_env()

        override = RuntimeMetadata(host_name=host_name or "", replica_name=replica_name or "")
        return runtime.merged_with(override) if runtime else override

    def merged_with(self, override: "RuntimeMetadata | None") -> "RuntimeMetadata":
        if override is None:
            return self

        return RuntimeMetadata(
            python_version=override.python_version or self.python_version,
            platform=override.platform or self.platform,
            host_name=override.host_name or self.host_name,
            replica_name=override.replica_name or self.replica_name,
        )


@dataclass(frozen=True)
class AgentServerMetadata:
    package: PackageMetadata
    runtime: RuntimeMetadata

    def as_user_agent(self, component: str | None = None) -> str:
        component_value = f" {component}" if component else ""
        return (
            f"{self.package.name}/{self.package.version} "
            f"Python {self.runtime.python_version}{component_value} "
            f"({self.runtime.platform})"
        )


_default = AgentServerMetadata(
    package=PackageMetadata.from_dist("azure-ai-agentserver-core"),
    runtime=RuntimeMetadata.resolve(),
)
_app: AgentServerMetadata = _default


def set_current_app(app: PackageMetadata, runtime: RuntimeMetadata | None = None) -> None:
    global _app  # pylint: disable=W0603
    resolved_runtime = RuntimeMetadata.resolve()
    merged_runtime = resolved_runtime.merged_with(runtime)
    _app = AgentServerMetadata(package=app, runtime=merged_runtime)


def get_current_app() -> AgentServerMetadata:
    global _app  # pylint: disable=W0602
    return _app
