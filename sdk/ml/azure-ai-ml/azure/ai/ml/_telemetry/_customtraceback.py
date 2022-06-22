# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""A file for custom traceback for removing file path from the trace for compliance need."""

import os
import sys
import traceback


class _CustomStackSummary(traceback.StackSummary):
    """Subclass of StackSummary."""

    def format(self):
        """Format the stack ready for printing.

        Returns a list of strings ready for printing.  Each string in the
        resulting list corresponds to a single frame from the stack.
        Each string ends in a newline; the strings may contain internal
        newlines as well, for those items with source text lines.
        """
        result = []
        for frame in self:
            row = ['  File "{}", line {}, in {}\n'.format(os.path.basename(frame.filename), frame.lineno, frame.name)]
            if frame.line:
                row.append("    {}\n".format(frame.line.strip()))
            if frame.locals:
                for name, value in sorted(frame.locals.items()):
                    row.append("    {name} = {value}\n".format(name=name, value=value))
            result.append("".join(row))
        return result


class _CustomTracebackException(traceback.TracebackException):
    def __init__(
        self, exc_type, exc_value, exc_traceback, *, limit=None, lookup_lines=True, capture_locals=False, _seen=None
    ):
        if _seen is None:
            _seen = set()
        _seen.add(exc_value)
        # Gracefully handle (the way Python 2.4 and earlier did) the case of
        # being called with no type or value (None, None, None).
        if exc_value and exc_value.__cause__ is not None and exc_value.__cause__ not in _seen:
            cause = _CustomTracebackException(
                type(exc_value.__cause__),
                exc_value.__cause__,
                exc_value.__cause__.__traceback__,
                limit=limit,
                lookup_lines=False,
                capture_locals=capture_locals,
                _seen=_seen,
            )
        else:
            cause = None
        if exc_value and exc_value.__context__ is not None and exc_value.__context__ not in _seen:
            context = _CustomTracebackException(
                type(exc_value.__context__),
                exc_value.__context__,
                exc_value.__context__.__traceback__,
                limit=limit,
                lookup_lines=False,
                capture_locals=capture_locals,
                _seen=_seen,
            )
        else:
            context = None
        self.exc_traceback = exc_traceback
        self.__cause__ = cause
        self.__context__ = context
        self.__suppress_context__ = exc_value.__suppress_context__ if exc_value else False
        # TODO: locals.
        self.stack = _CustomStackSummary.extract(
            traceback.walk_tb(exc_traceback), limit=limit, lookup_lines=lookup_lines, capture_locals=capture_locals
        )
        self.exc_type = exc_type
        # Capture now to permit freeing resources: only complication is in the
        # unofficial API _format_final_exc_line
        self._str = traceback._some_str(exc_value)
        if exc_type and issubclass(exc_type, SyntaxError):
            # Handle SyntaxError's specially
            self.filename = exc_value.filename
            self.lineno = str(exc_value.lineno)
            self.text = exc_value.text
            self.offset = exc_value.offset
            self.msg = exc_value.msg
        if lookup_lines:
            self._load_lines()

    def format_exception_only(self):
        """Format the exception part of the traceback.

        The return value is a generator of strings, each ending in a newline.
        Normally, the generator emits a single string; however, for
        SyntaxError exceptions, it emits several lines that (when
        printed) display detailed information about where the syntax
        error occurred.
        The message indicating which exception occurred is always the last
        string in the output.
        """
        if self.exc_type is None:
            yield traceback._format_final_exc_line(None, self._str)
            return

        stype = self.exc_type.__qualname__
        smod = self.exc_type.__module__
        if smod not in ("__main__", "builtins"):
            stype = smod + "." + stype

        if not issubclass(self.exc_type, SyntaxError):
            yield traceback._format_final_exc_line(stype, self._str)
            return

        # It was a syntax error; show exactly where the problem was found.
        filename = os.path.basename(self.filename) or "<string>"
        lineno = str(self.lineno) or "?"
        yield '  File "{}", line {}\n'.format(filename, lineno)

        badline = self.text
        offset = self.offset
        if badline is not None:
            yield "    {}\n".format(badline.strip())
            if offset is not None:
                caretspace = badline.rstrip("\n")
                offset = min(len(caretspace), offset) - 1
                caretspace = caretspace[:offset].lstrip()
                # non-space whitespace (likes tabs) must be kept for alignment
                caretspace = ((c.isspace() and c or " ") for c in caretspace)
                yield "    {}^\n".format("".join(caretspace))
        msg = self.msg or "<no detail available>"
        yield "{}: {}\n".format(stype, msg)


def format_exc(limit=None, chain=True):
    """Like print_exc() but return a string."""
    return "".join(format_exception(*sys.exc_info(), limit=limit, chain=chain))


def format_exception(etype, value, tb, limit=None, chain=True):
    """Format a stack trace and the exception information.

    The arguments have the same meaning as the corresponding arguments
    to print_exception().  The return value is a list of strings, each
    ending in a newline and some containing internal newlines.  When
    these lines are concatenated and printed, exactly the same text is
    printed as does print_exception().
    """
    # format_exception has ignored etype for some time, and code such as cgitb
    # passes in bogus values as a result. For compatibility with such code we
    # ignore it here (rather than in the new TracebackException API).
    return list(_CustomTracebackException(type(value), value, tb, limit=limit).format(chain=chain))
