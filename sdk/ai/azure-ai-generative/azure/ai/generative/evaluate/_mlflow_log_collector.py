# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import sys
import traceback
import tempfile
from typing import Any
import mlflow


class OutputCollector(object):
    def __init__(self, stream, processor):
        self._inner = stream
        self.processor = processor

    def write(self, buf):
        self.processor(buf)
        self._inner.write(buf)

    def __getattr__(self, name):
        return getattr(self._inner, name)


class RedirectUserOutputStreams(object):
    def __init__(self, logger):
        self.logger = logger
        self.user_log_path = tempfile.mkstemp(suffix="_stdout_stderr.txt")[1]

        self.user_log_fp: Any = None
        self.original_stdout: Any = None
        self.original_stderr: Any = None

    def __enter__(self):
        self.logger.debug("Redirecting user output to {0}".format(self.user_log_path))

        self.user_log_fp = open(self.user_log_path, "at+", encoding="utf-8")
        self.original_stdout = sys.stdout
        self.original_stderr = sys.stderr
        sys.stdout = OutputCollector(sys.stdout, self.user_log_fp.write)
        sys.stderr = OutputCollector(sys.stderr, self.user_log_fp.write)

    def __exit__(self, exc_type, exc_val, exc_tb):
        try:
            if exc_val:
                # The default traceback.print_exc() expects a file-like object which
                # OutputCollector is not. Instead manually print the exception details
                # to the wrapped sys.stderr by using an intermediate string.
                # trace = traceback.format_tb(exc_tb)
                trace = "".join(traceback.format_exception(exc_type, exc_val, exc_tb))
                print(trace, file=sys.stderr)
        finally:
            sys.stdout.flush()
            sys.stderr.flush()
            sys.stdout = self.original_stdout
            sys.stderr = self.original_stderr

            mlflow.log_artifact(self.user_log_path, "user_logs")

            self.user_log_fp.close()
            # Commenting this out due to a bug where file is help by another process causing delete to fail
            # os.remove(self.user_log_path)
            self.logger.debug("User scope execution complete.")
