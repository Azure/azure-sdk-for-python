# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

from datetime import datetime
from pathlib import Path
from tempfile import gettempdir
from typing import Union


def create_timestamped_temp_log_file(script_path: Union[str, Path]) -> Path:
    script_path = Path(script_path)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return Path(gettempdir()) / f"{script_path.stem}_{timestamp}.log"
