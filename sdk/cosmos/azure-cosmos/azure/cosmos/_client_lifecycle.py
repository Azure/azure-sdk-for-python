# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
"""Exception-safe cleanup while client constructors are still running."""
import logging
from functools import wraps
from typing import Any, Callable
from typing_extensions import Concatenate, ParamSpec

_LOGGER = logging.getLogger(__name__)
_P = ParamSpec("_P")


def _cleanup(action: Callable[[], Any]) -> None:
    try:
        action()
    except Exception:  # Cleanup must not replace the original startup exception.
        _LOGGER.warning("Failed to release resources after client startup failure", exc_info=True)


def unwind_client_construction(
    constructor: Callable[Concatenate[Any, _P], None],
) -> Callable[Concatenate[Any, _P], None]:
    @wraps(constructor)
    def initialize(self: Any, /, *args: _P.args, **kwargs: _P.kwargs) -> None:
        try:
            constructor(self, *args, **kwargs)
        except BaseException:
            backend = vars(self).get("_backend")
            abort = getattr(backend, "abort_construction", None)
            if callable(abort):
                _cleanup(abort)
            raise
    return initialize


def unwind_connection_construction(
    constructor: Callable[Concatenate[Any, _P], None],
) -> Callable[Concatenate[Any, _P], None]:
    @wraps(constructor)
    def initialize(self: Any, /, *args: _P.args, **kwargs: _P.kwargs) -> None:
        try:
            constructor(self, *args, **kwargs)
        except BaseException:
            for name, method in (("_routing_map_provider", "release"), ("pipeline_client", "close")):
                resource = vars(self).get(name)
                if resource is not None:
                    _cleanup(getattr(resource, method))
            raise
    return initialize
