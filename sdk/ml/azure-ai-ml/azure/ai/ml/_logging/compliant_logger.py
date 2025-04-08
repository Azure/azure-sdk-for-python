# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

""" This is logger utility which will work with allowed logged filter AML policy
    https://github.com/Azure/azure-policy/blob/master/built-in-policies/policyDefinitions/Machine%20Learning/AllowedLogFilter_EnforceSetting.json
    You have to define the same "logFilters" while initializing the logger using  "enable_compliant_logging" method
    e.g. 
        log filters: ["^SystemLog:.*$"]
        initialize : enable_compliant_logging(format_key="prefix",
                                format_key_value="SystemLog",
                                format=f"%(prefix)s{logging.BASIC_FORMAT}")
    By default log message will not compliant e.g. not modified
"""

import logging
import sys
from datetime import datetime
from enum import Enum
from threading import Lock
from typing import Optional

_LOCK = Lock()
_FORMAT_KEY = None
_FORMAT_VALUE = None


# pylint: disable=global-statement
def set_format(key_name: str, value: str) -> None:
    with _LOCK:
        global _FORMAT_KEY
        _FORMAT_KEY = key_name
        global _FORMAT_VALUE
        _FORMAT_VALUE = value


def get_format_key() -> Optional[str]:
    return _FORMAT_KEY


def get_format_value() -> Optional[str]:
    return _FORMAT_VALUE


def get_default_logging_format() -> str:
    return f"%({get_format_key()})s{logging.BASIC_FORMAT}"


class DataCategory(Enum):
    """
    Enumeration of data categories in compliant machine learning.

    Values:
    - PRIVATE: data which is private. Researchers may not view this.
    - PUBLIC: data which may safely be viewed by researchers.
    """

    PRIVATE = 1
    PUBLIC = 2


class CompliantLogger(logging.getLoggerClass()):  # type: ignore
    """
    Subclass of the default logging class with an explicit `is_compliant` parameter
    on all logging methods. It will pass an `extra` param with `format` key
    (value depending on whether `is_compliant` is True or False) to the
    handlers.

    The default value for data `is_compliant` is `False` for all methods.

    Implementation is inspired by:
    https://github.com/python/cpython/blob/3.8/Lib/logging/__init__.py
    """

    def __init__(self, name: str, handlers=None):
        super().__init__(name)  # type: ignore

        self.format_key = get_format_key()
        self.format_value = get_format_value()

        if handlers:
            self.handlers = handlers

        self.start_time = datetime.now()
        self.metric_count = 1
        # number of iterable items that are logged
        self.max_iter_items = 10

    def _log(
        self,
        level,
        msg,
        args=None,
        exc_info=None,
        extra=None,
        stack_info=False,
        stacklevel=1,
        category=DataCategory.PRIVATE,
    ):
        if category == DataCategory.PUBLIC:
            format_value = self.format_value
        else:
            format_value = ""

        if extra:
            extra.update({self.format_key: format_value})
        else:
            extra = {self.format_key: format_value}

        if sys.version_info[1] <= 7:
            super(CompliantLogger, self)._log(
                level=level,
                msg=msg,
                args=args,
                exc_info=exc_info,
                extra=extra,
                stack_info=stack_info,
            )
        else:
            super(CompliantLogger, self)._log(
                level=level,
                msg=msg,
                args=args,
                exc_info=exc_info,
                extra=extra,
                stack_info=stack_info,
                stacklevel=stacklevel,  # type: ignore
            )


_logging_basic_config_set_warning = """
********************************************************************************
The root logger already has handlers set! As a result, the behavior of this
library is undefined. If running in Python >= 3.8, this library will attempt to
call logging.basicConfig(force=True), which will remove all existing root
handlers. See https://stackoverflow.com/q/20240464 and
https://github.com/Azure/confidential-ml-utils/issues/33 for more information.
********************************************************************************
"""


def enable_compliant_logging(
    format_key: str = "prefix",
    format_key_value: str = "SystemLog:",
    **kwargs,
) -> None:
    """
    The default format is `logging.BASIC_FORMAT` (`%(levelname)s:%(name)s:%(message)s`).
    All other kwargs are passed to `logging.basicConfig`. Sets the default
    logger class and root logger to be compliant. This means the format
    string `%(xxxx)` will work.

    :param format_key: key for format
    :type format_key: str
    :param format_key_value: value for format
    :type format_key_value: str

    Set the format using the `format` kwarg.

    If running in Python >= 3.8, will attempt to add `force=True` to the kwargs
    for logging.basicConfig.

    The standard implementation of the logging API is a good reference:
    https://github.com/python/cpython/blob/3.9/Lib/logging/__init__.py
    """
    set_format(format_key, format_key_value)

    if "format" not in kwargs:
        kwargs["format"] = get_default_logging_format()

    # Ensure that all loggers created via `logging.getLogger` are instances of
    # the `CompliantLogger` class.
    logging.setLoggerClass(CompliantLogger)

    if len(logging.root.handlers) > 0:
        p = get_format_value()
        for line in _logging_basic_config_set_warning.splitlines():
            print(f"{p}{line}", file=sys.stderr)

    if "force" not in kwargs and sys.version_info >= (3, 8):
        kwargs["force"] = True

    root = CompliantLogger(logging.root.name, handlers=logging.root.handlers)

    logging.root = root
    logging.Logger.root = root  # type: ignore
    logging.Logger.manager = logging.Manager(root)  # type: ignore

    # https://github.com/kivy/kivy/issues/6733
    logging.basicConfig(**kwargs)
