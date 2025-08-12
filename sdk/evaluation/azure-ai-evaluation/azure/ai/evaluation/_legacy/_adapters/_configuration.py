# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from pathlib import Path
from typing import Any, Dict, Final, Optional
from typing_extensions import TypeAlias


try:
    from promptflow._sdk._configuration import Configuration as _Configuration
except ImportError:
    _global_config: Final[Dict[str, Any]] = {}

    class _Configuration:
        TRACE_DESTINATION: Final[str] = "trace.destination"
        _instance = None

        def __init__(self, *, override_config: Optional[Dict[str, Any]] = None) -> None:
            self._config = override_config or {}

        @classmethod
        def get_instance(cls) -> "_Configuration":
            """Use this to get instance to avoid multiple copies of same global config."""
            if cls._instance is None:
                cls._instance = Configuration(override_config=_global_config)
            return cls._instance

        def set_config(self, key: str, value: Any) -> None:
            # Simulated config storage
            self._config[key] = value

        def get_config(self, key: str) -> Any:
            # Simulated config storage
            if key in self._config:
                return self._config[key]
            return _global_config.get(key, None)

        def get_trace_destination(self, path: Optional[Path] = None) -> Optional[str]:
            if path:
                raise NotImplementedError("Setting trace destination with a path is not supported.")
            return self._config.get("trace.destination", None)


Configuration: TypeAlias = _Configuration
