# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import logging
from pathlib import Path
from typing import Dict, List, Optional, Union

from . import AutorestAPI, Channel


_LOGGER = logging.getLogger(__name__)


class LocalAutorestAPI(AutorestAPI):
    """A local API that will write on local disk."""

    def __init__(
        self,
        reachable_files: Optional[List[str]] = None,
        output_folder: str = "generated",
    ) -> None:
        super().__init__()
        if reachable_files is None:
            reachable_files = []
        self._reachable_files = reachable_files
        self._output_folder = Path(output_folder)
        self.values: Dict[str, Optional[str]] = {}

    def write_file(self, filename: Union[str, Path], file_content: str) -> None:
        _LOGGER.debug("Writing file: %s", filename)
        with (self._output_folder / Path(filename)).open("w", encoding="utf-8") as fd:
            fd.write(file_content)
        _LOGGER.debug("Written file: %s", filename)

    def read_file(self, filename: Union[str, Path]) -> str:
        _LOGGER.debug("Reading file: %s", filename)
        with (self._output_folder / Path(filename)).open("r", encoding="utf-8") as fd:
            return fd.read()

    def list_inputs(self) -> List[str]:
        return self._reachable_files

    def get_value(self, key: str) -> Optional[str]:
        return self.values.get(key, None)

    def message(self, channel: Channel, text: str) -> None:
        pass
