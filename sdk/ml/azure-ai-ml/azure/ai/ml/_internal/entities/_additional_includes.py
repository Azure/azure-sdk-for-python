# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
from pathlib import Path
from typing import Optional

from ...constants._common import AzureDevopsArtifactsType
from ...entities._component._additional_includes import AdditionalIncludes


class InternalAdditionalIncludes(AdditionalIncludes):
    """This class is kept for compatibility with mldesigner."""

    @property
    def includes(self):
        if self._is_artifact_includes:
            return self._get_resolved_additional_include_configs()
        return self.origin_configs

    @property
    def code_path(self) -> Optional[Path]:
        return self.resolved_code_path

    @property
    def _is_artifact_includes(self):
        return any(
            map(
                lambda x: isinstance(x, dict) and x.get("type", None) == AzureDevopsArtifactsType.ARTIFACT,
                self.origin_configs,
            )
        )
