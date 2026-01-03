# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
from __future__ import annotations

import platform
from dataclasses import dataclass
from importlib.metadata import Distribution, PackageNotFoundError


@dataclass(frozen=True)
class PackageMetadata:
    name: str
    version: str
    python_version: str
    platform: str

    @staticmethod
    def from_dist(dist_name: str):
        try:
            ver = Distribution.from_name(dist_name).version
        except PackageNotFoundError:
            ver = ""

        return PackageMetadata(
            name=dist_name,
            version=ver,
            python_version=platform.python_version(),
            platform=platform.platform(),
        )

    def as_user_agent(self, component: str | None = None) -> str:
        return (f"{self.name}/{self.version} "
                f"Python {self.python_version} "
                f"{component} " if component else ""
                f"({self.platform})")


_default = PackageMetadata.from_dist("azure-ai-agentserver-core")
_app: PackageMetadata = _default


def set_current_app(app: PackageMetadata) -> None:
    global _app
    _app = app


def get_current_app() -> PackageMetadata:
    global _app
    return _app
