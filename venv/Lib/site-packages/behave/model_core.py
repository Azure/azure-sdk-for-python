# -*- coding: UTF-8 -*-
"""
This module provides the abstract base classes and core concepts
for the model elements in behave.
"""

import os.path
import sys
import six
from behave.capture import Captured
from behave.textutil import text as _text
from enum import Enum


PLATFORM_WIN = sys.platform.startswith("win")
def posixpath_normalize(path):
    return path.replace("\\", "/")


# -----------------------------------------------------------------------------
# GENERIC MODEL CLASSES:
# -----------------------------------------------------------------------------
class Status(Enum):
    """Provides the (test-run) status of a model element.
    Features and Scenarios use: untested, skipped, passed, failed.
    Steps may use all enum-values.

    Enum values:
    * untested (initial state):

        Defines the initial state before a test-run.
        Sometimes used to indicate that the model element was not executed
        during a test run.

    * skipped:

        A model element is skipped because it should not run.
        This is caused by filtering mechanisms, like tags, active-tags,
        file-location arg, select-by-name, etc.

    * passed: A model element was executed and passed (without failures).
    * failed: Failures occurred while executing it.
    * undefined: Used for undefined-steps (no step implementation was found).
    * executing: Marks the steps during execution (used in a formatter)

    .. versionadded:: 1.2.6
        Superceeds string-based status values.
    """
    untested = 0
    skipped = 1
    passed = 2
    failed = 3
    undefined = 4
    executing = 5

    def __eq__(self, other):
        """Comparison operator equals-to other value.
        Supports other enum-values and string (for backward compatibility).

        EXAMPLES::

            status = Status.passed
            assert status == Status.passed
            assert status == "passed"
            assert status != "failed"

        :param other:   Other value to compare (enum-value, string).
        :return: True, if both values are equal. False, otherwise.
        """
        if isinstance(other, six.string_types):
            # -- CONVENIENCE: Compare with string-name (backward-compatible)
            return self.name == other
        return super(Status, self).__eq__(other)

    @classmethod
    def from_name(cls, name):
        """Select enumeration value by using its name.

        :param name:    Name as key to the enum value (as string).
        :return: Enum value (instance)
        :raises: LookupError, if status name is unknown.
        """
        # pylint: disable=no-member
        enum_value = cls.__members__.get(name, None)
        if enum_value is None:
            known_names = ", ".join(cls.__members__.keys())
            raise LookupError("%s (expected: %s)" % (name, known_names))
        return enum_value


class Argument(object):
    """An argument found in a *feature file* step name and extracted using
    step decorator `parameters`_.

    The attributes are:

    .. attribute:: original

       The actual text matched in the step name.

    .. attribute:: value

       The potentially type-converted value of the argument.

    .. attribute:: name

       The name of the argument. This will be None if the parameter is
       anonymous.

    .. attribute:: start

       The start index in the step name of the argument. Used for display.

    .. attribute:: end

       The end index in the step name of the argument. Used for display.
    """
    def __init__(self, start, end, original, value, name=None):
        self.start = start
        self.end = end
        self.original = original
        self.value = value
        self.name = name


# @total_ordering
# class FileLocation(unicode):
class FileLocation(object):
    """
    Provides a value object for file location objects.
    A file location consists of:

      * filename
      * line (number), optional

    LOCATION SCHEMA:
      * "{filename}:{line}" or
      * "{filename}" (if line number is not present)
    """
    __pychecker__ = "missingattrs=line"     # -- Ignore warnings for 'line'.

    def __init__(self, filename, line=None):
        if PLATFORM_WIN:
            filename = posixpath_normalize(filename)
        self.filename = filename
        self.line = line

    def get(self):
        return self.filename

    def abspath(self):
        return os.path.abspath(self.filename)

    def basename(self):
        return os.path.basename(self.filename)

    def dirname(self):
        return os.path.dirname(self.filename)

    def relpath(self, start=os.curdir):
        """Compute relative path for start to filename.

        :param start: Base path or start directory (default=current dir).
        :return: Relative path from start to filename
        """
        return os.path.relpath(self.filename, start)

    def exists(self):
        return os.path.exists(self.filename)

    def _line_lessthan(self, other_line):
        if self.line is None:
            # return not (other_line is None)
            return other_line is not None
        elif other_line is None:
            return False
        else:
            return self.line < other_line

    def __eq__(self, other):
        if isinstance(other, FileLocation):
            return self.filename == other.filename and self.line == other.line
        elif isinstance(other, six.string_types):
            return self.filename == other
        else:
            raise TypeError("Cannot compare FileLocation with %s:%s" % \
                            (type(other), other))

    def __ne__(self, other):
        # return not self == other    # pylint: disable=unneeded-not
        return not self.__eq__(other)

    def __lt__(self, other):
        if isinstance(other, FileLocation):
            if self.filename < other.filename:
                return True
            elif self.filename > other.filename:
                return False
            else:
                assert self.filename == other.filename
                return self._line_lessthan(other.line)

        elif isinstance(other, six.string_types):
            return self.filename < other
        else:
            raise TypeError("Cannot compare FileLocation with %s:%s" % \
                            (type(other), other))

    def __le__(self, other):
        # -- SEE ALSO: python2.7, functools.total_ordering
        # return not other < self     # pylint unneeded-not
        return other >= self

    def __gt__(self, other):
        # -- SEE ALSO: python2.7, functools.total_ordering
        if isinstance(other, FileLocation):
            return other < self
        else:
            return self.filename > other

    def __ge__(self, other):
        # -- SEE ALSO: python2.7, functools.total_ordering
        # return not self < other
        return not self.__lt__(other)

    def __repr__(self):
        return u'<FileLocation: filename="%s", line=%s>' % \
               (self.filename, self.line)

    def __str__(self):
        filename = self.filename
        if isinstance(filename, six.binary_type):
            filename = _text(filename, "utf-8")
        if self.line is None:
            return filename
        return u"%s:%d" % (filename, self.line)

    if six.PY2:
        __unicode__ = __str__
        __str__ = lambda self: self.__unicode__().encode("utf-8")

    @classmethod
    def for_function(cls, func, curdir=None):
        """Extracts the location information from the function and builds
        the location string (schema: "{source_filename}:{line_number}").

        :param func: Function whose location should be determined.
        :return: FileLocation object
        """
        func = unwrap_function(func)
        function_code = six.get_function_code(func)
        filename = function_code.co_filename
        line_number = function_code.co_firstlineno

        curdir = curdir or os.getcwd()
        try:
            filename = os.path.relpath(filename, curdir)
        except ValueError:
            # WINDOWS-SPECIFIC (#599):
            # If a step-function comes from a different disk drive,
            # a relative path will fail: Keep the absolute path.
            pass
        return cls(filename, line_number)


# -----------------------------------------------------------------------------
# ABSTRACT MODEL CLASSES (and concepts):
# -----------------------------------------------------------------------------
class BasicStatement(object):
    def __init__(self, filename, line, keyword, name):
        filename = filename or '<string>'
        filename = os.path.relpath(filename, os.getcwd())   # -- NEEDS: abspath?
        self.location = FileLocation(filename, line)
        assert isinstance(keyword, six.text_type)
        assert isinstance(name, six.text_type)
        self.keyword = keyword
        self.name = name
        # -- SINCE: 1.2.6
        self.captured = Captured()
        # -- ERROR CONTEXT INFO:
        self.exception = None
        self.exc_traceback = None
        self.error_message = None

    @property
    def filename(self):
        # return os.path.abspath(self.location.filename)
        return self.location.filename

    @property
    def line(self):
        return self.location.line

    def reset(self):
        # -- RESET: Captured output data
        self.captured.reset()
        # -- RESET: ERROR CONTEXT INFO
        self.exception = None
        self.exc_traceback = None
        self.error_message = None

    def store_exception_context(self, exception):
        self.exception = exception
        self.exc_traceback = sys.exc_info()[2]

    def __hash__(self):
        # -- NEEDED-FOR: PYTHON3
        # return id((self.keyword, self.name))
        return id(self)

    def __eq__(self, other):
        # -- PYTHON3 SUPPORT, ORDERABLE:
        # NOTE: Ignore potential FileLocation differences.
        return (self.keyword, self.name) == (other.keyword, other.name)

    def __lt__(self, other):
        # -- PYTHON3 SUPPORT, ORDERABLE:
        # NOTE: Ignore potential FileLocation differences.
        return (self.keyword, self.name) < (other.keyword, other.name)

    def __ne__(self, other):
        return not self.__eq__(other)

    def __le__(self, other):
        # -- SEE ALSO: python2.7, functools.total_ordering
        # return not other < self
        return other >= self

    def __gt__(self, other):
        # -- SEE ALSO: python2.7, functools.total_ordering
        assert isinstance(other, BasicStatement)
        return other < self

    def __ge__(self, other):
        # -- SEE ALSO: python2.7, functools.total_ordering
        # OR: return self >= other
        return not self < other     # pylint: disable=unneeded-not

    # def __cmp__(self, other):
    #     # -- NOTE: Ignore potential FileLocation differences.
    #     return cmp((self.keyword, self.name), (other.keyword, other.name))


class TagStatement(BasicStatement):

    def __init__(self, filename, line, keyword, name, tags):
        if tags is None:
            tags = []
        super(TagStatement, self).__init__(filename, line, keyword, name)
        self.tags = tags

    def should_run_with_tags(self, tag_expression):
        """Determines if statement should run when the tag expression is used.

        :param tag_expression:  Runner/config environment tags to use.
        :return: True, if examples should run. False, otherwise (skip it).
        """
        return tag_expression.check(self.tags)


class TagAndStatusStatement(BasicStatement):
    # final_status = ('passed', 'failed', 'skipped')
    final_status = (Status.passed, Status.failed, Status.skipped)

    def __init__(self, filename, line, keyword, name, tags):
        super(TagAndStatusStatement, self).__init__(filename, line, keyword, name)
        self.tags = tags
        self.should_skip = False
        self.skip_reason = None
        self._cached_status = Status.untested

    def should_run_with_tags(self, tag_expression):
        """Determines if statement should run when the tag expression is used.

        :param tag_expression:  Runner/config environment tags to use.
        :return: True, if examples should run. False, otherwise (skip it).
        """
        return tag_expression.check(self.tags)

    @property
    def status(self):
        if self._cached_status not in self.final_status:
            # -- RECOMPUTE: As long as final status is not reached.
            self._cached_status = self.compute_status()
        return self._cached_status

    def set_status(self, value):
        if isinstance(value, six.string_types):
            value = Status.from_name(value)
        self._cached_status = value

    def clear_status(self):
        self._cached_status = Status.untested

    def reset(self):
        self.should_skip = False
        self.skip_reason = None
        self.clear_status()

    def compute_status(self):
        raise NotImplementedError


class Replayable(object):
    type = None

    def replay(self, formatter):
        getattr(formatter, self.type)(self)


# -----------------------------------------------------------------------------
# UTILITY FUNCTIONS:
# -----------------------------------------------------------------------------
def unwrap_function(func, max_depth=10):
    """Unwraps a function that is wrapped with :func:`functools.partial()`"""
    iteration = 0
    wrapped = getattr(func, "__wrapped__", None)
    while wrapped and iteration < max_depth:
        func = wrapped
        wrapped = getattr(func, "__wrapped__", None)
        iteration += 1
    return func
