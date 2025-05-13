# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from typing import Callable, Final


try:
    from promptflow._cli._pf._service import stop_service as _stop_service
except ImportError:

    def _stop_service() -> None:
        pass


stop_service: Final[Callable[[], None]] = _stop_service
