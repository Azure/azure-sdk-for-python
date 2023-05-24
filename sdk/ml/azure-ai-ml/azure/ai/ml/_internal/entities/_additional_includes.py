# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from pathlib import Path
import yaml

from ...entities._component._additional_includes import (
    AdditionalIncludes,
    ADDITIONAL_INCLUDES_KEY,
    ADDITIONAL_INCLUDES_SUFFIX,
)


class InternalAdditionalIncludes(AdditionalIncludes):
    @property
    def includes(self):
        if not self.additional_includes_file_path.is_file():
            return []
        if self._includes is None:
            if self.is_artifact_includes:
                self._includes = self._load_artifact_additional_includes()
            else:
                with open(self.additional_includes_file_path, "r") as f:
                    lines = f.readlines()
                    self._includes = [line.strip() for line in lines if len(line.strip()) > 0]
        return self._includes

    @property
    def code_path(self) -> Path:
        if self._code_path is not None:
            return (self.yaml_path.parent / self._code_path).resolve()
        return self.yaml_path.parent

    @property
    def additional_includes_file_path(self) -> Path:
        return self.yaml_path.with_suffix(ADDITIONAL_INCLUDES_SUFFIX)

    @property
    def base_path(self) -> Path:
        return self.additional_includes_file_path.parent

    @property
    def is_artifact_includes(self):
        try:
            with open(self.additional_includes_file_path) as f:
                additional_includes_configs = yaml.safe_load(f)
                return (
                    isinstance(additional_includes_configs, dict)
                    and ADDITIONAL_INCLUDES_KEY in additional_includes_configs
                )
        except Exception:  # pylint: disable=broad-except
            return False
