# -*- coding: UTF-8 -*-
"""
Capture output (stdout, stderr), logs, etc.
"""

from __future__ import absolute_import
from contextlib import contextmanager
import sys
from six import StringIO, PY2
from behave.log_capture import LoggingCapture
from behave.textutil import text as _text

def add_text_to(value, more_text, separator="\n"):
    if more_text:
        if value:
            if separator and not value.endswith(separator):
                value += separator
            value += more_text
        else:
            value = more_text
    return value


class Captured(object):
    """Stores and aggregates captured output data."""
    empty = u""
    linesep = u"\n"

    def __init__(self, stdout=None, stderr=None, log_output=None):
        self.stdout = stdout or self.empty
        self.stderr = stderr or self.empty
        self.log_output = log_output or self.empty

    def reset(self):
        self.stdout = self.empty
        self.stderr = self.empty
        self.log_output = self.empty

    # -- PYTHON2:
    if PY2:
        def __nonzero__(self):
            return bool(self.stdout or self.stderr or self.log_output)
    else:
        def __bool__(self):
            return bool(self.stdout or self.stderr or self.log_output)

    @property
    def output(self):
        """Makes a simple report of the captured data by concatenating
        all parts.
        """
        output_text = self.stdout
        output_text = add_text_to(output_text, self.stderr)
        output_text = add_text_to(output_text, self.log_output)
        return output_text

    def add(self, captured):
        """Adds/appends captured output data to this object.

        :param captured:    Captured object whose data should be added.
        :return: self, to allow daisy-chaining (if needed).
        """
        assert isinstance(captured, Captured)
        self.stdout = add_text_to(self.stdout, captured.stdout, self.linesep)
        self.stderr = add_text_to(self.stderr, captured.stderr, self.linesep)
        self.log_output = add_text_to(self.log_output, captured.log_output,
                                      self.linesep)
        return self

    def make_report(self):
        """Makes a detailled report of the captured output data.

        :returns: Report as string.
        """
        report_parts = []
        if self.stdout:
            parts = ["Captured stdout:", _text(self.stdout).rstrip(), ""]
            report_parts.extend(parts)
        if self.stderr:
            parts = ["Captured stderr:", _text(self.stderr).rstrip(), ""]
            report_parts.extend(parts)
        if self.log_output:
            parts = ["Captured logging:", _text(self.log_output)]
            report_parts.extend(parts)
        return self.linesep.join(report_parts).strip()

    def __add__(self, other):
        """Supports incremental add::

            captured1 = Captured("Hello")
            captured2 = Captured("World")
            captured3 = captured1 + captured2
            assert captured3.stdout == "Hello\nWorld"
        """
        new_data = Captured(self.stdout, self.stderr, self.log_output)
        return new_data.add(other)

    def __iadd__(self, other):
        """Supports incremental add::

            captured1 = Captured("Hello")
            captured2 = Captured("World")
            captured1 += captured2
            assert captured1.stdout == "Hello\nWorld"
        """
        return self.add(other)


class CaptureController(object):
    """Simplifies the lifecycle to capture output from various sources."""
    def __init__(self, config):
        self.config = config
        self.stdout_capture = None
        self.stderr_capture = None
        self.log_capture = None
        self.old_stdout = None
        self.old_stderr = None

    @property
    def captured(self):
        """Provides access of the captured output data.

        :return: Object that stores the captured output parts (as Captured).
        """
        stdout = None
        stderr = None
        log_out = None
        if self.config.stdout_capture and self.stdout_capture:
            stdout = _text(self.stdout_capture.getvalue())
        if self.config.stderr_capture and self.stderr_capture:
            stderr = _text(self.stderr_capture.getvalue())
        if self.config.log_capture and self.log_capture:
            log_out = _text(self.log_capture.getvalue())
        return Captured(stdout, stderr, log_out)

    def setup_capture(self, context):
        assert context is not None
        if self.config.stdout_capture:
            self.stdout_capture = StringIO()
            context.stdout_capture = self.stdout_capture

        if self.config.stderr_capture:
            self.stderr_capture = StringIO()
            context.stderr_capture = self.stderr_capture

        if self.config.log_capture:
            self.log_capture = LoggingCapture(self.config)
            self.log_capture.inveigle()
            context.log_capture = self.log_capture

    def start_capture(self):
        if self.config.stdout_capture:
            # -- REPLACE ONLY: In non-capturing mode.
            if not self.old_stdout:
                self.old_stdout = sys.stdout
                sys.stdout = self.stdout_capture
            assert sys.stdout is self.stdout_capture

        if self.config.stderr_capture:
            # -- REPLACE ONLY: In non-capturing mode.
            if not self.old_stderr:
                self.old_stderr = sys.stderr
                sys.stderr = self.stderr_capture
            assert sys.stderr is self.stderr_capture

    def stop_capture(self):
        if self.config.stdout_capture:
            # -- RESTORE ONLY: In capturing mode.
            if self.old_stdout:
                sys.stdout = self.old_stdout
                self.old_stdout = None
            assert sys.stdout is not self.stdout_capture

        if self.config.stderr_capture:
            # -- RESTORE ONLY: In capturing mode.
            if self.old_stderr:
                sys.stderr = self.old_stderr
                self.old_stderr = None
            assert sys.stderr is not self.stderr_capture

    def teardown_capture(self):
        if self.config.log_capture:
            self.log_capture.abandon()

    def make_capture_report(self):
        """Combine collected output and return as string."""
        return self.captured.make_report()
        # report = u""
        # if self.config.stdout_capture and self.stdout_capture:
        #     output = self.stdout_capture.getvalue()
        #     if output:
        #         output = _text(output)
        #         report += u"\nCaptured stdout:\n" + output
        # if self.config.stderr_capture and self.stderr_capture:
        #     output = self.stderr_capture.getvalue()
        #     if output:
        #         output = _text(output)
        #         report += u"\nCaptured stderr:\n" + output
        # if self.config.log_capture and self.log_capture:
        #     output = self.log_capture.getvalue()
        #     if output:
        #         output = _text(output)
        #         report += u"\nCaptured logging:\n" + output
        # return report

# -----------------------------------------------------------------------------
# UTILITY FUNCTIONS:
# -----------------------------------------------------------------------------
@contextmanager
def capture_output(controller, enabled=True):
    """Provides a context manager that starts capturing output

    .. code-block::

        with capture_output(capture_controller):
            ... # Do something
    """
    if enabled:
        try:
            controller.start_capture()
            yield
        finally:
            controller.stop_capture()
    else:
        # -- CAPTURING OUTPUT is disabled.
        # Needed to prevent recursive captures with context.execute_steps()
        yield
