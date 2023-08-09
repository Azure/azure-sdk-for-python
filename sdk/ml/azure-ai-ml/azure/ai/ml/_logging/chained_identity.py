# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import logging
import os
from contextlib import ContextDecorator
from typing import Any, Optional

START_MSG = "[START]"
STOP_MSG = "[STOP]"

_PRINT_STACK = os.environ.get("_AZUREML_TRACE_STACK", False)


class ChainedIdentity(object):
    """A mixin that provides structured, chained logging for objects and contexts."""

    DELIM = "#"

    def __init__(self, _ident: Optional[str] = None, _parent_logger: Optional[logging.Logger] = None, **kwargs):
        """Internal class used to improve logging information.

        :param _ident: Identity of the object
        :type _ident: str
        :param _parent_logger: Parent logger, used to maintain creation hierarchy
        :type _parent_logger: logging.Logger
        """

        # TODO: Ideally move constructor params to None defaulted
        # and pick up the stack trace as a reasonable approximation
        self._identity = self.__class__.__name__ if _ident is None else _ident
        parent = logging.getLogger("azureml") if _parent_logger is None else _parent_logger
        self._logger = parent.getChild(self._identity)
        try:
            super(ChainedIdentity, self).__init__(**kwargs)
        except TypeError as type_error:
            raise TypeError(
                "{}. Found key word arguments: {}.".format(",".join(type_error.args), kwargs.keys())
            ) from type_error

    @property
    def identity(self) -> str:
        return self._identity

    def _log_context(self, context_name: str) -> Any:
        return LogScope(_ident=context_name, _parent_logger=self._logger)


class LogScope(ChainedIdentity, ContextDecorator):
    """Convenience for logging a context."""

    def __enter__(self) -> logging.Logger:
        msg = START_MSG
        if _PRINT_STACK:
            import io
            import traceback

            stackstr = io.StringIO()
            traceback.print_stack(file=stackstr)
            msg = "{}\n{}".format(msg, stackstr.getvalue())
        self._logger.debug(msg)
        return self._logger

    def __exit__(self, etype, value, traceback) -> None:
        if value is not None:
            self._logger.debug("Error {0}: {1}\n{2}".format(etype, value, traceback))
        self._logger.debug(STOP_MSG)
