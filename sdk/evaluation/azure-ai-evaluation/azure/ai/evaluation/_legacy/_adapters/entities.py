# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from typing_extensions import TypeAlias


try:
    from promptflow._sdk.entities import Run as _Run
except ImportError:
    from typing_extensions import Protocol
    from typing import Any, Dict, Optional
    from datetime import datetime
    from pathlib import Path

    class _Run(Protocol):
        name: str
        status: str
        _properties: Dict[str, Any]
        _created_on: datetime
        _end_time: Optional[datetime]
        _experiment_name: Optional[str]
        _output_path: Path


Run: TypeAlias = _Run
