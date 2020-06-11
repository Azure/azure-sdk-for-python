# -*- coding: utf-8 -*-
"""
This module provides the step matchers functionality that matches a
step definition (as text) with step-functions that implement this step.
"""

from __future__ import absolute_import, print_function, with_statement
import copy
import re
import warnings
import parse
import six
from parse_type import cfparse
from behave._types import ChainedExceptionUtil, ExceptionUtil
from behave.model_core import Argument, FileLocation, Replayable


# -----------------------------------------------------------------------------
# SECTION: Exceptions
# -----------------------------------------------------------------------------
class StepParseError(ValueError):
    """Exception class, used when step matching fails before a step is run.
    This is normally the case when an error occurs during the type conversion
    of step parameters.
    """

    def __init__(self, text=None, exc_cause=None):
        if not text and exc_cause:
            text = six.text_type(exc_cause)
        if exc_cause and six.PY2:
            # -- NOTE: Python2 does not show chained-exception causes.
            #    Therefore, provide some hint (see also: PEP-3134).
            cause_text = ExceptionUtil.describe(exc_cause,
                                                use_traceback=True,
                                                prefix="CAUSED-BY: ")
            text += u"\n" + cause_text

        ValueError.__init__(self, text)
        if exc_cause:
            # -- CHAINED EXCEPTION (see: PEP 3134)
            ChainedExceptionUtil.set_cause(self, exc_cause)



# -----------------------------------------------------------------------------
# SECTION: Model Elements
# -----------------------------------------------------------------------------
class Match(Replayable):
    """An parameter-matched *feature file* step name extracted using
    step decorator `parameters`_.

    .. attribute:: func

       The step function that this match will be applied to.

    .. attribute:: arguments

       A list of :class:`~behave.model_core.Argument` instances containing the
       matched parameters from the step name.
    """
    type = "match"

    def __init__(self, func, arguments=None):
        super(Match, self).__init__()
        self.func = func
        self.arguments = arguments
        self.location = None
        if func:
            self.location = self.make_location(func)

    def __repr__(self):
        if self.func:
            func_name = self.func.__name__
        else:
            func_name = '<no function>'
        return '<Match %s, %s>' % (func_name, self.location)

    def __eq__(self, other):
        if not isinstance(other, Match):
            return False
        return (self.func, self.location) == (other.func, other.location)

    def with_arguments(self, arguments):
        match = copy.copy(self)
        match.arguments = arguments
        return match

    def run(self, context):
        args = []
        kwargs = {}
        for arg in self.arguments:
            if arg.name is not None:
                kwargs[arg.name] = arg.value
            else:
                args.append(arg.value)

        with context.use_with_user_mode():
            self.func(context, *args, **kwargs)

    @staticmethod
    def make_location(step_function):
        """Extracts the location information from the step function and
        builds a FileLocation object with (filename, line_number) info.

        :param step_function: Function whose location should be determined.
        :return: FileLocation object for step function.
        """
        return FileLocation.for_function(step_function)


class NoMatch(Match):
    """Used for an "undefined step" when it can not be matched with a
    step definition.
    """

    def __init__(self):
        Match.__init__(self, func=None)
        self.func = None
        self.arguments = []
        self.location = None


class MatchWithError(Match):
    """Match class when error occur during step-matching

    REASON:
      * Type conversion error occured.
      * ...
    """
    def __init__(self, func, error):
        if not ExceptionUtil.has_traceback(error):
            ExceptionUtil.set_traceback(error)
        Match.__init__(self, func=func)
        self.stored_error = error

    def run(self, context):
        """Raises stored error from step matching phase (type conversion)."""
        raise StepParseError(exc_cause=self.stored_error)




# -----------------------------------------------------------------------------
# SECTION: Matchers
# -----------------------------------------------------------------------------
class Matcher(object):
    """Pull parameters out of step names.

    .. attribute:: pattern

       The match pattern attached to the step function.

    .. attribute:: func

       The step function the pattern is being attached to.
    """
    schema = u"@%s('%s')"   # Schema used to describe step definition (matcher)

    def __init__(self, func, pattern, step_type=None):
        self.func = func
        self.pattern = pattern
        self.step_type = step_type
        self._location = None

    # -- BACKWARD-COMPATIBILITY:
    @property
    def string(self):
        warnings.warn("deprecated: Use 'pattern' instead", DeprecationWarning)
        return self.pattern

    @property
    def location(self):
        if self._location is None:
            self._location = Match.make_location(self.func)
        return self._location

    @property
    def regex_pattern(self):
        """Return the used textual regex pattern."""
        # -- ASSUMPTION: pattern attribute provides regex-pattern
        # NOTE: Method must be overridden if assumption is not met.
        return self.pattern

    def describe(self, schema=None):
        """Provide a textual description of the step function/matcher object.

        :param schema:  Text schema to use.
        :return: Textual description of this step definition (matcher).
        """
        step_type = self.step_type or "step"
        if not schema:
            schema = self.schema
        return schema % (step_type, self.pattern)


    def check_match(self, step):
        """Match me against the "step" name supplied.

        Return None, if I don't match otherwise return a list of matches as
        :class:`~behave.model_core.Argument` instances.

        The return value from this function will be converted into a
        :class:`~behave.matchers.Match` instance by *behave*.
        """
        raise NotImplementedError

    def match(self, step):
        # -- PROTECT AGAINST: Type conversion errors (with ParseMatcher).
        try:
            result = self.check_match(step)
        except Exception as e:  # pylint: disable=broad-except
            return MatchWithError(self.func, e)

        if result is None:
            return None     # -- NO-MATCH
        return Match(self.func, result)

    def __repr__(self):
        return u"<%s: %r>" % (self.__class__.__name__, self.pattern)


class ParseMatcher(Matcher):
    """Uses :class:`~parse.Parser` class to be able to use simpler
    parse expressions compared to normal regular expressions.
    """
    custom_types = {}
    parser_class = parse.Parser

    def __init__(self, func, pattern, step_type=None):
        super(ParseMatcher, self).__init__(func, pattern, step_type)
        self.parser = self.parser_class(pattern, self.custom_types)

    @property
    def regex_pattern(self):
        # -- OVERWRITTEN: Pattern as regex text.
        return self.parser._expression  # pylint: disable=protected-access

    def check_match(self, step):
        # -- FAILURE-POINT: Type conversion of parameters may fail here.
        #    NOTE: Type converter should raise ValueError in case of PARSE ERRORS.
        result = self.parser.parse(step)
        if not result:
            return None

        args = []
        for index, value in enumerate(result.fixed):
            start, end = result.spans[index]
            args.append(Argument(start, end, step[start:end], value))
        for name, value in result.named.items():
            start, end = result.spans[name]
            args.append(Argument(start, end, step[start:end], value, name))
        args.sort(key=lambda x: x.start)
        return args


class CFParseMatcher(ParseMatcher):
    """Uses :class:`~parse_type.cfparse.Parser` instead of "parse.Parser".
    Provides support for automatic generation of type variants
    for fields with CardinalityField part.
    """
    parser_class = cfparse.Parser


def register_type(**kw):
    # pylint: disable=anomalous-backslash-in-string
    # REQUIRED-BY: code example
    """Registers a custom type that will be available to "parse"
    for type conversion during step matching.

    Converters should be supplied as ``name=callable`` arguments (or as dict).

    A type converter should follow :pypi:`parse` module rules.
    In general, a type converter is a function that converts text (as string)
    into a value-type (type converted value).

    EXAMPLE:

    .. code-block:: python

        from behave import register_type, given
        import parse

        # -- TYPE CONVERTER: For a simple, positive integer number.
        @parse.with_pattern(r"\d+")
        def parse_number(text):
            return int(text)

        # -- REGISTER TYPE-CONVERTER: With behave
        register_type(Number=parse_number)

        # -- STEP DEFINITIONS: Use type converter.
        @given('{amount:Number} vehicles')
        def step_impl(context, amount):
            assert isinstance(amount, int)
    """
    ParseMatcher.custom_types.update(kw)


class RegexMatcher(Matcher):
    def __init__(self, func, pattern, step_type=None):
        super(RegexMatcher, self).__init__(func, pattern, step_type)
        self.regex = re.compile(self.pattern)

    def check_match(self, step):
        m = self.regex.match(step)
        if not m:
            return None

        groupindex = dict((y, x) for x, y in self.regex.groupindex.items())
        args = []
        for index, group in enumerate(m.groups()):
            index += 1
            name = groupindex.get(index, None)
            args.append(Argument(m.start(index), m.end(index), group,
                                 group, name))

        return args

class SimplifiedRegexMatcher(RegexMatcher):
    """Simplified regular expression step-matcher that automatically adds
    start-of-line/end-of-line matcher symbols to string:

    .. code-block:: python

        @when(u'a step passes')     # re.pattern = "^a step passes$"
        def step_impl(context): pass
    """

    def __init__(self, func, pattern, step_type=None):
        assert not (pattern.startswith("^") or pattern.endswith("$")), \
            "Regular expression should not use begin/end-markers: "+ pattern
        expression = "^%s$" % pattern
        super(SimplifiedRegexMatcher, self).__init__(func, expression, step_type)
        self.pattern = pattern


class CucumberRegexMatcher(RegexMatcher):
    """Compatible to (old) Cucumber style regular expressions.
    Text must contain start-of-line/end-of-line matcher symbols to string:

    .. code-block:: python

        @when(u'^a step passes$')   # re.pattern = "^a step passes$"
        def step_impl(context): pass
    """

matcher_mapping = {
    "parse": ParseMatcher,
    "cfparse": CFParseMatcher,
    "re": SimplifiedRegexMatcher,

    # -- BACKWARD-COMPATIBLE REGEX MATCHER: Old Cucumber compatible style.
    # To make it the default step-matcher use the following snippet:
    #   # -- FILE: features/environment.py
    #   from behave import use_step_matcher
    #   def before_all(context):
    #       use_step_matcher("re0")
    "re0": CucumberRegexMatcher,
}
current_matcher = ParseMatcher      # pylint: disable=invalid-name


def use_step_matcher(name):
    """Change the parameter matcher used in parsing step text.

    The change is immediate and may be performed between step definitions in
    your step implementation modules - allowing adjacent steps to use different
    matchers if necessary.

    There are several parsers available in *behave* (by default):

    **parse** (the default, based on: :pypi:`parse`)
        Provides a simple parser that replaces regular expressions for
        step parameters with a readable syntax like ``{param:Type}``.
        The syntax is inspired by the Python builtin ``string.format()``
        function.
        Step parameters must use the named fields syntax of :pypi:`parse`
        in step definitions. The named fields are extracted,
        optionally type converted and then used as step function arguments.

        Supports type conversions by using type converters
        (see :func:`~behave.register_type()`).

    **cfparse** (extends: :pypi:`parse`, requires: :pypi:`parse_type`)
        Provides an extended parser with "Cardinality Field" (CF) support.
        Automatically creates missing type converters for related cardinality
        as long as a type converter for cardinality=1 is provided.
        Supports parse expressions like:

        * ``{values:Type+}`` (cardinality=1..N, many)
        * ``{values:Type*}`` (cardinality=0..N, many0)
        * ``{value:Type?}``  (cardinality=0..1, optional)

        Supports type conversions (as above).

    **re**
        This uses full regular expressions to parse the clause text. You will
        need to use named groups "(?P<name>...)" to define the variables pulled
        from the text and passed to your ``step()`` function.

        Type conversion is **not supported**.
        A step function writer may implement type conversion
        inside the step function (implementation).

    You may `define your own matcher`_.

    .. _`define your own matcher`: api.html#step-parameters
    """
    global current_matcher  # pylint: disable=global-statement
    current_matcher = matcher_mapping[name]

def step_matcher(name):
    """
    DEPRECATED, use :func:`use_step_matcher()` instead.
    """
    # -- BACKWARD-COMPATIBLE NAME: Mark as deprecated.
    warnings.warn("deprecated: Use 'use_step_matcher()' instead",
                  DeprecationWarning, stacklevel=2)
    use_step_matcher(name)

def get_matcher(func, pattern):
    return current_matcher(func, pattern)
