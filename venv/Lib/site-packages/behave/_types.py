# -*- coding: UTF-8 -*-
"""Basic types (helper classes)."""

import sys
import six
if six.PY2:
    # -- USE PYTHON2 BACKPORT: With unicode support
    import traceback2 as traceback
else:
    import traceback


class Unknown(object):
    """Placeholder for unknown/missing information, distinguishable from None.

    .. code-block:: python

        data = {}
        value = data.get("name", Unknown)
        if value is Unknown:
            # -- DO SOMETHING
            ...
    """


class ExceptionUtil(object):
    """Provides a utility class for accessing/modifying exception information.

    .. seealso:: PEP-3134 Chained excpetions
    """
    # pylint: disable=no-init

    @staticmethod
    def get_traceback(exception):
        # -- ASSUMPTION: assert isinstance(exception, Exception)
        return getattr(exception, "__traceback__", None)

    @staticmethod
    def set_traceback(exception, exc_traceback=Unknown):
        assert isinstance(exception, Exception)
        if exc_traceback is Unknown:
            exc_traceback = sys.exc_info()[2]
        exception.__traceback__ = exc_traceback

    @classmethod
    def has_traceback(cls, exception):
        """Indicates if traceback information related to this exception
        is stored with the exception object.

        :param exception:   Exception object to check.
        :return: True, if traceback info is stored. False, otherwise.
        """
        return cls.get_traceback(exception) is not None

    @classmethod
    def describe(cls, exception, use_traceback=False, prefix=""):
        # -- NORMAL CASE:
        text = u"{prefix}{0}: {1}\n".format(exception.__class__.__name__,
                                            exception, prefix=prefix)
        if use_traceback:
            exc_traceback = cls.get_traceback(exception)
            if exc_traceback:
                # -- NOTE: Chained-exception cause (see: PEP-3134).
                text += u"".join(traceback.format_tb(exc_traceback))
        return text


class ChainedExceptionUtil(ExceptionUtil):
    """Provides a utility class for accessing/modifying exception information
    related to chained exceptions.

    .. seealso:: PEP-3134 Chained excpetions
    """
    # pylint: disable=no-init

    @staticmethod
    def get_cause(exception):
        # -- ASSUMPTION: assert isinstance(exception, Exception)
        return getattr(exception, "__cause__", None)

    @staticmethod
    def set_cause(exception, exc_cause):
        assert isinstance(exception, Exception)
        assert isinstance(exc_cause, Exception) or exc_cause is None
        exception.__cause__ = exc_cause
        if exc_cause and not hasattr(exc_cause, "__traceback__"):
            # -- NEEDED-FOR: Python2
            # Otherwise, traceback formatting tries to access missing attribute.
            exc_cause.__traceback__ = None

    # pylint: disable=arguments-differ
    @classmethod
    def describe(cls, exception, use_traceback=False, prefix="", style="reversed"):
        """Describes an exception, optionally together with its traceback info.
        Also shows information about exception cause (chained exceptions),
        if exists.

        :param exception:       Exception object to describe.
        :param use_traceback:   Indicates if traceback info should be shown.
        :param prefix:          Optional prefix for description text.
        :param style:           Optional style indicator ("reversed", "normal")
        :return: Exception description as text.
        """
        text = ExceptionUtil.describe(exception, use_traceback, prefix)

        # -- STEP: Collect chained exceptions.
        causes = []
        exc_cause = cls.get_cause(exception)
        while exc_cause:
            causes.append(exc_cause)
            exc_cause = cls.get_cause(exc_cause)

        # -- STEP: Describe causes for chained exceptions.
        parts = []
        if style == "normal":
            prefix = "CAUSE: "
            for exc_cause in reversed(causes):
                cause_text = ExceptionUtil.describe(exc_cause, use_traceback,
                                                    prefix)
                parts.append(cause_text)
                if len(parts) == 1:
                    prefix = "CAUSES: "
            parts.append(text)
        else:
            parts.append(text)
            for exc_cause in causes:
                cause_text = ExceptionUtil.describe(exc_cause, use_traceback,
                                                    prefix="CAUSED-BY: ")
                parts.append(cause_text)
        return u"\n".join(parts)
        # if exc_cause:
        #     cause_text =
        #     text += u"\n" + cause_text
        # return text
