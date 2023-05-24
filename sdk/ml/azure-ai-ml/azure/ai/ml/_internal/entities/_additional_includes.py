# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from pathlib import Path
from typing import List, Union

import yaml

from ...entities._component.additional_includes import AdditionalIncludes


class InternalAdditionalIncludes(AdditionalIncludes):
    def __init__(self, code_path: Union[None, str], yaml_path: Path):
        self._yaml_path = yaml_path

        super(InternalAdditionalIncludes, self).__init__(
            code_path=code_path, base_path=yaml_path.parent, configs=self._read_configs(yaml_path)
        )

    @classmethod
    def _read_configs(cls, yaml_path) -> List:
        additional_includes_config_path = yaml_path.with_suffix(cls.get_suffix())
        if additional_includes_config_path.is_file():
            with open(additional_includes_config_path) as f:
                file_content = f.read()
                configs = yaml.safe_load(file_content)
                if isinstance(configs, dict):
                    return configs.get(cls.get_config_key(), [])
                return [line.strip() for line in file_content.splitlines(keepends=False) if len(line.strip()) > 0]
        return []

    @property
    def yaml_path(self):
        return self._yaml_path

    @property
    def code_path(self) -> Path:
        if self._code_path is not None:
            return (self.yaml_path.parent / self._code_path).resolve()
        return self.yaml_path.parent

    @property
    def additional_includes_file_path(self) -> Path:
        return self.yaml_path.with_suffix(self.get_suffix())

    def get_config_file_name(self):
        return self.additional_includes_file_path.name

    @property
    def base_path(self) -> Path:
        return self.additional_includes_file_path.parent
