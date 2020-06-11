# -*- coding: utf-8 -*-

from __future__ import absolute_import, print_function
from logging.handlers import BufferingHandler
import logging
import functools
import re


class RecordFilter(object):
    """Implement logging record filtering as per the configuration
    --logging-filter option.
    """
    def __init__(self, names):
        self.include = set()
        self.exclude = set()
        for name in names.split(','):
            if name[0] == '-':
                self.exclude.add(name[1:])
            else:
                self.include.add(name)

    def filter(self, record):
        if self.exclude:
            return record.name not in self.exclude
        return record.name in self.include


# originally from nostetsts logcapture plugin
class LoggingCapture(BufferingHandler):
    """Capture logging events in a memory buffer for later display or query.

    Captured logging events are stored on the attribute
    :attr:`~LoggingCapture.buffer`:

    .. attribute:: buffer

       This is a list of captured logging events as `logging.LogRecords`_.

    .. _`logging.LogRecords`:
       http://docs.python.org/library/logging.html#logrecord-objects

    By default the format of the messages will be::

        '%(levelname)s:%(name)s:%(message)s'

    This may be overridden using standard logging formatter names in the
    configuration variable ``logging_format``.

    The level of logging captured is set to ``logging.NOTSET`` by default. You
    may override this using the configuration setting ``logging_level`` (which
    is set to a level name.)

    Finally there may be `filtering of logging events`__ specified by the
    configuration variable ``logging_filter``.

    .. __: behave.html#command-line-arguments
    """

    def __init__(self, config, level=None):
        BufferingHandler.__init__(self, 1000)
        self.config = config
        self.old_handlers = []
        self.old_level = None

        # set my formatter
        log_format = datefmt = None
        if config.logging_format:
            log_format = config.logging_format
        else:
            log_format = '%(levelname)s:%(name)s:%(message)s'
        if config.logging_datefmt:
            datefmt = config.logging_datefmt
        formatter = logging.Formatter(log_format, datefmt)
        self.setFormatter(formatter)

        # figure the level we're logging at
        if level is not None:
            self.level = level
        elif config.logging_level:
            self.level = config.logging_level
        else:
            self.level = logging.NOTSET

        # construct my filter
        if config.logging_filter:
            self.addFilter(RecordFilter(config.logging_filter))

    def __bool__(self):
        return bool(self.buffer)

    def flush(self):
        pass  # do nothing

    def truncate(self):
        self.buffer = []

    def getvalue(self):
        return '\n'.join(self.formatter.format(r) for r in self.buffer)

    def find_event(self, pattern):
        """Search through the buffer for a message that matches the given
        regular expression.

        Returns boolean indicating whether a match was found.
        """
        pattern = re.compile(pattern)
        for record in self.buffer:
            if pattern.search(record.getMessage()) is not None:
                return True
        return False

    def any_errors(self):
        """Search through the buffer for any ERROR or CRITICAL events.

        Returns boolean indicating whether a match was found.
        """
        return any(record for record in self.buffer
                   if record.levelname in ('ERROR', 'CRITICAL'))

    def inveigle(self):
        """Turn on logging capture by replacing all existing handlers
        configured in the logging module.

        If the config var logging_clear_handlers is set then we also remove
        all existing handlers.

        We also set the level of the root logger.

        The opposite of this is :meth:`~LoggingCapture.abandon`.
        """
        root_logger = logging.getLogger()
        if self.config.logging_clear_handlers:
            # kill off all the other log handlers
            for logger in logging.Logger.manager.loggerDict.values():
                if hasattr(logger, "handlers"):
                    for handler in logger.handlers:
                        self.old_handlers.append((logger, handler))
                        logger.removeHandler(handler)

        # sanity check: remove any existing LoggingCapture
        for handler in root_logger.handlers[:]:
            if isinstance(handler, LoggingCapture):
                root_logger.handlers.remove(handler)
            elif self.config.logging_clear_handlers:
                self.old_handlers.append((root_logger, handler))
                root_logger.removeHandler(handler)

        # right, we're it now
        root_logger.addHandler(self)

        # capture the level we're interested in
        self.old_level = root_logger.level
        root_logger.setLevel(self.level)

    def abandon(self):
        """Turn off logging capture.

        If other handlers were removed by :meth:`~LoggingCapture.inveigle` then
        they are reinstated.
        """
        root_logger = logging.getLogger()
        for handler in root_logger.handlers[:]:
            if handler is self:
                root_logger.handlers.remove(handler)

        if self.config.logging_clear_handlers:
            for logger, handler in self.old_handlers:
                logger.addHandler(handler)

        if self.old_level is not None:
            # -- RESTORE: Old log.level before inveigle() was used.
            root_logger.setLevel(self.old_level)
            self.old_level = None

# pre-1.2 backwards compatibility
MemoryHandler = LoggingCapture


def capture(*args, **kw):
    """Decorator to wrap an *environment file function* in log file capture.

    It configures the logging capture using the *behave* context - the first
    argument to the function being decorated (so don't use this to decorate
    something that doesn't have *context* as the first argument.)

    The basic usage is:

    .. code-block: python

        @capture
        def after_scenario(context, scenario):
            ...

    The function prints any captured logging (at the level determined by the
    ``log_level`` configuration setting) directly to stdout, regardless of
    error conditions.

    It is mostly useful for debugging in situations where you are seeing a
    message like::

        No handlers could be found for logger "name"

    The decorator takes an optional "level" keyword argument which limits the
    level of logging captured, overriding the level in the run's configuration:

    .. code-block: python

        @capture(level=logging.ERROR)
        def after_scenario(context, scenario):
            ...

    This would limit the logging captured to just ERROR and above, and thus
    only display logged events if they are interesting.
    """
    def create_decorator(func, level=None):
        def f(context, *args):
            h = LoggingCapture(context.config, level=level)
            h.inveigle()
            try:
                func(context, *args)
            finally:
                h.abandon()
            v = h.getvalue()
            if v:
                print("Captured Logging:")
                print(v)
        return f

    if not args:
        return functools.partial(create_decorator, level=kw.get("level"))
    else:
        return create_decorator(args[0])
