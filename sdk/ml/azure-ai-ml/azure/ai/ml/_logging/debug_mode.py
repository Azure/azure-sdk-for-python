# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import logging
import os
import time
import sys
import traceback
from typing import List
import six.moves.http_client as httpclient
from collections import namedtuple


LOG_FILE = os.path.abspath("azureml.log")
LOG_FORMAT = "%(asctime)s|%(name)s|%(levelname)s|%(message)s"
INTERESTING_NAMESPACES = ["azureml", "msrest.http_logger", "urllib2", "azure"]

module_logger = logging.getLogger(__name__)
separator = "\n==================\n"
ConnectionInfo = namedtuple("ConnectionInfo", ["host", "port", "hasSocket"])


def stack_info() -> list:
    main_stack = []
    for threadId, stack in sys._current_frames().items():
        for filename, lineno, name, line in traceback.extract_stack(stack):
            call = line.strip() if line is not None else None
            main_stack.append({"ThreadID": threadId, "File": filename, "Line": lineno, "Name": name, "Call": call})

    return main_stack


def connection_info(gc_objects: list) -> List[ConnectionInfo]:
    connections = [obj for obj in gc_objects if isinstance(obj, httpclient.HTTPConnection)]
    return [ConnectionInfo(host=c.host, port=c.port, hasSocket=(c.sock is not None)) for c in connections]


class diagnostic_log(object):
    """Directs debug logs to a specified file.

    :param log_path: A path with log file name. If None, a file named "azureml.log" is
        created.
    :type log_path: str
    :param namespaces: A list of namespaces to capture logs for. If None, the default is "azureml",
        "msrest.http_logger", "urllib2", and "azure".
    :type namespaces: builtin.list
    :param context_name: A name to identify the logging context. If None, the context of the calling
        stack frame is used.
    :type context_type: str
    """

    def __init__(self, log_path: str = None, namespaces: list = None, context_name: str = None):
        self._namespaces = INTERESTING_NAMESPACES if namespaces is None else namespaces
        self._filename = LOG_FILE if log_path is None else log_path
        self._filename = os.path.abspath(self._filename)
        self._capturing = False
        if context_name is None:
            import inspect

            context_name = inspect.getouterframes(inspect.currentframe(), 2)[1].function
        self._context_name = context_name

        formatter = logging.Formatter(LOG_FORMAT)
        formatter.converter = time.gmtime

        file_handler = logging.FileHandler(filename=self._filename, encoding="utf-8")
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatter)
        self._handler = file_handler

    def start_capture(self) -> None:
        """Start the capture of debug logs."""
        if self._capturing:
            module_logger.warning("Debug logs are already enabled at %s", self._filename)
            return

        print("Debug logs are being sent to {}".format(self._filename))
        for namespace in self._namespaces:
            module_logger.debug("Adding [%s] debug logs to this file", namespace)
            n_logger = logging.getLogger(namespace)
            n_logger.setLevel(logging.DEBUG)
            n_logger.addHandler(self._handler)
            # We do the below for strange environments like Revo + Jupyter
            # where root handlers appear to already be set.
            # We don't want to spew to those consoles with DEBUG emissions
            n_logger.propagate = False

        module_logger.info("\n\n********** STARTING CAPTURE FOR [%s] **********\n\n", self._context_name)
        self._capturing = True

    def stop_capture(self) -> None:
        """Stop the capture of debug logs."""
        if not self._capturing:
            module_logger.warning("Debug logs are already disabled.")
            return

        module_logger.info("\n\n********** STOPPING CAPTURE FOR [%s] **********\n\n", self._context_name)
        print("Disabling log capture. Resulting file is at {}".format(self._filename))

        for namespace in self._namespaces:
            module_logger.debug("Removing [%s] debug logs to this file", namespace)
            n_logger = logging.getLogger(namespace)
            n_logger.removeHandler(self._handler)

        self._capturing = False

    def __enter__(self) -> None:
        self.start_capture()

    def __exit__(self) -> None:
        self.stop_capture()


_debugging_enabled = False


def debug_sdk() -> None:
    global _debugging_enabled
    if _debugging_enabled:
        module_logger.warning("Debug logs are already enabled at %s", LOG_FILE)
        return

    formatter = logging.Formatter(LOG_FORMAT)
    formatter.converter = time.gmtime

    file_handler = logging.FileHandler(filename=LOG_FILE, encoding="utf-8")
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)

    module_logger.info("Debug logs are being sent to %s", LOG_FILE)

    for namespace in INTERESTING_NAMESPACES:
        module_logger.debug("Adding [%s] debug logs to this file", namespace)
        n_logger = logging.getLogger(namespace)
        n_logger.setLevel(logging.DEBUG)
        n_logger.addHandler(file_handler)
        # We do the below for strange environments like Revo + Jupyter
        # where root handlers appear to already be set.
        # We don't want to spew to those consoles with DEBUG emissions
        n_logger.propagate = 0

    _debugging_enabled = True
