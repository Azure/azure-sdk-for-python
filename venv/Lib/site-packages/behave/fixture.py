# -*- coding: UTF-8 -*-
# STATUS: Basic concept works.
"""
A **fixture** provides a concept to simplify test support functionality
that needs a setup/cleanup cycle per scenario, feature or test-run.
A fixture is provided as fixture-function that contains the setup part and
cleanup part similar to :func:`contextlib.contextmanager` or `pytest.fixture`_.

.. _pytest.fixture: https://docs.pytest.org/en/latest/fixture.html

A fixture is used when:

* the (registered) fixture tag is used for a scenario or feature
* the :func:`.use_fixture()` is called in the environment file (normally)

.. sourcecode:: python

    # -- FILE: behave4my_project/fixtures.py (or: features/environment.py)
    from behave import fixture
    from somewhere.browser.firefox import FirefoxBrowser

    @fixture
    def browser_firefox(context, timeout=30, **kwargs):
        # -- SETUP-FIXTURE PART:
        context.browser = FirefoxBrowser(timeout, *args, **kwargs)
        yield context.browser
        # -- CLEANUP-FIXTURE PART:
        context.browser.shutdown()

.. sourcecode:: gherkin

    # -- FILE: features/use_fixture.feature
    Feature: Use Fixture in Scenario

        @fixture.browser.firefox
        Scenario: Use browser=firefox
          Given I use the browser
          ...
        # -- AFTER-SCENEARIO: Cleanup fixture.browser.firefox

.. sourcecode:: python

    # -- FILE: features/environment.py
    from behave import use_fixture
    from behave4my_project.fixtures import browser_firefox

    def before_tag(context, tag):
        if tag == "fixture.browser.firefox":
            # -- Performs fixture setup and registers fixture cleanup
            use_fixture(browser_firefox, context, timeout=10)

.. hidden:

    BEHAVIORAL DECISIONS:

    * Should scenario/feature be executed when fixture-setup fails
      (similar to before-hook failures) ?
      NO, scope is skipped, but after-hooks and cleanups are executed.

    * Should remaining fixture-setups be performed after first fixture fails?
      NO, first setup-error aborts the setup and execution of the scope.

    * Should remaining fixture-cleanups be performed when first cleanup-error
      occurs?
      YES, try to perform all fixture-cleanups and then reraise the
      first cleanup-error.


    OPEN ISSUES:

    * AUTO_CALL_REGISTERED_FIXTURE (planned in future):
        Run fixture setup before or after before-hooks?

    IDEAS:

    * Fixture registers itself in fixture registry (runtime context).
    * Code in before_tag() will either be replaced w/ fixture processing function
      or will be automatically be executed (AUTO_CALL_REGISTERED_FIXTURE)
    * Support fixture tags w/ parameters that are automatically parsed and
      passed to fixture function, like:
      @fixture(name="foo", pattern="{name}={browser}")
"""

import inspect


# -------------------------------------------------------------------------------
# LOCAL HELPERS:
# -------------------------------------------------------------------------------
def iscoroutinefunction(func):
    """Checks if a function is a coroutine-function, like:

     * ``async def f(): ...`` (since Python 3.5)
     * ``@asyncio.coroutine def f(): ...`` (since Python3)

    .. note:: Compatibility helper

        Avoids to import :mod:`asyncio` module directly (since Python3),
        which in turns initializes the :mod:`logging` module as side-effect.

    :param func:  Function to check.
    :return: True, if function is a coroutine function.
             False, otherwise.
    """
    # -- NOTE: inspect.iscoroutinefunction() is available since Python 3.5
    #    Checks also if @asyncio.coroutine decorator is not used.
    # pylint: disable=no-member
    return (getattr(func, "_is_coroutine", False) or
            (hasattr(inspect, "iscoroutinefunction") and
             inspect.iscoroutinefunction(func)))


def is_context_manager(func):
    """Checks if a fixture function provides context-manager functionality,
    similar to :func`contextlib.contextmanager()` function decorator.

    .. code-block:: python

        @fixture
        def foo(context, *args, **kwargs):
            context.foo = setup_foo()
            yield context.foo
            cleanup_foo()

        @fixture
        def bar(context, *args, **kwargs):
            context.bar = setup_bar()
            return context.bar

        assert is_context_manager(foo) is True      # Generator-function
        assert is_context_manager(bar) is False     # Normal function

    :param func:    Function to check.
    :return: True, if function is a generator/context-manager function.
             False, otherwise.
    """
    genfunc = inspect.isgeneratorfunction(func)
    return genfunc and not iscoroutinefunction(func)


# -------------------------------------------------------------------------------
# EXCEPTIONS:
# -------------------------------------------------------------------------------
class InvalidFixtureError(RuntimeError):
    """Raised when a fixture is invalid.
    This occurs when a generator-function with more than one yield statement
    is used as fixture-function.
    """


# -------------------------------------------------------------------------------
# FUNCTIONS: Fixture support
# -------------------------------------------------------------------------------
def _setup_fixture(fixture_func, context, *fixture_args, **fixture_kwargs):
    """Provides core functionality to setup a fixture and registers its
    cleanup part (if needed).
    """
    if is_context_manager(fixture_func):
        # -- CASE: Fixture function is a two-step generator (setup, cleanup).
        def cleanup_fixture():
            try:
                next(func_it)           # CLEANUP-FIXTURE PART
                # -- USE func_it: From outer scope (here).
            except StopIteration:
                return False
            # -- NOT-NEEDED:
            # except Exception:
            #    raise   # -- CLEANUP-FIXTURE PART raised an error.
            else:
                message = "Has more than one yield: %r" % fixture_func
                raise InvalidFixtureError(message)

        # -- GENERATOR: Get instance via call and register cleanup.
        #  Then perform setup_fixture to ensure that cleanup_fixture()
        #  is called even if setup-error occurs.
        #  NOTE: cleanup_fixture() is called when context layer is removed.
        func_it = fixture_func(context, *fixture_args, **fixture_kwargs)
        context.add_cleanup(cleanup_fixture)
        setup_result = next(func_it) # SETUP-FIXTURE PART (may raise error)
    else:
        # -- CASE: Fixture is a simple function (setup-only)
        # NOTE: No cleanup is registered (not needed by intention of user)
        setup_result = fixture_func(context, *fixture_args, **fixture_kwargs)
    return setup_result


def use_fixture(fixture_func, context, *fixture_args, **fixture_kwargs):
    """Use fixture (function) and call it to perform its setup-part.

    The fixture-function is similar to a :func:`contextlib.contextmanager`
    (and contains a yield-statement to seperate setup and cleanup part).
    If it contains a yield-statement, it registers a context-cleanup function
    to the context object to perform the fixture-cleanup at the end of the
    current scoped when the context layer is removed
    (and all context-cleanup functions are called).

    Therefore, fixture-cleanup is performed after scenario, feature or test-run
    (depending when its fixture-setup is performed).

    .. code-block:: python

        # -- FILE: behave4my_project/fixtures.py (or: features/environment.py)
        from behave import fixture
        from somewhere.browser import FirefoxBrowser

        @fixture(name="fixture.browser.firefox")
        def browser_firefox(context, *args, **kwargs):
            # -- SETUP-FIXTURE PART:
            context.browser = FirefoxBrowser(*args, **kwargs)
            yield context.browser
            # -- CLEANUP-FIXTURE PART:
            context.browser.shutdown()

    .. code-block:: python

        # -- FILE: features/environment.py
        from behave import use_fixture
        from behave4my_project.fixtures import browser_firefox

        def before_tag(context, tag):
            if tag == "fixture.browser.firefox":
                use_fixture(browser_firefox, context, timeout=10)


    :param fixture_func: Fixture function to use.
    :param context: Context object to use
    :param fixture_kwargs: Positional args, passed to the fixture function.
    :param fixture_kwargs: Additional kwargs, passed to the fixture function.
    :return: Setup result object (may be None).
    """
    return _setup_fixture(fixture_func, context, *fixture_args, **fixture_kwargs)


def use_fixture_by_tag(tag, context, fixture_registry):
    """Process any fixture-tag to perform :func:`use_fixture()` for its fixture.
    If the fixture-tag is known, the fixture data is retrieved from the
    fixture registry.

    .. code-block:: python

        # -- FILE: features/environment.py
        from behave.fixture import use_fixture_by_tag
        from behave4my_project.fixtures import browser_firefox, browser_chrome

        # -- SCHEMA 1: fixture_func
        fixture_registry1 = {
            "fixture.browser.firefox": browser_firefox,
            "fixture.browser.chrome":  browser_chrome,
        }
        # -- SCHEMA 2: fixture_func, fixture_args, fixture_kwargs
        fixture_registry2 = {
            "fixture.browser.firefox": (browser_firefox, (), dict(timeout=10)),
            "fixture.browser.chrome":  (browser_chrome,  (), dict(timeout=12)),
        }

        def before_tag(context, tag):
            if tag.startswith("fixture."):
                return use_fixture_by_tag(tag, context, fixture_registry1):
            # -- MORE: Tag processing steps ...


    :param tag:     Fixture tag to process.
    :param context: Runtime context object, used for :func:`use_fixture()`.
    :param fixture_registry:  Registry maps fixture-tag to fixture data.
    :return: Fixture-setup result (same as: use_fixture())
    :raises LookupError: If fixture-tag/fixture is unknown.
    :raises ValueError: If fixture data type is not supported.
    """
    fixture_data = fixture_registry.get(tag, None)
    if fixture_data is None:
        raise LookupError("Unknown fixture-tag: %s" % tag)

    if callable(fixture_data):
        fixture_func = fixture_data
        use_fixture(fixture_func, context)
    elif isinstance(fixture_data, (tuple, list)):
        assert len(fixture_data) == 3
        fixture_func, fixture_args, fixture_kwargs = fixture_data
        return use_fixture(fixture_func, context, *fixture_args, **fixture_kwargs)
    else:
        message = "fixture_data: Expected tuple or fixture-func, but is: %r"
        raise ValueError(message % fixture_data)


def fixture_call_params(fixture_func, *args, **kwargs):
    # -- SEE: use_composite_fixture_with()
    return (fixture_func, args, kwargs)


def use_composite_fixture_with(context, fixture_funcs_with_params):
    """Helper function when complex fixtures should be created and
    safe-cleanup is needed even if an setup-fixture-error occurs.

    This function ensures that fixture-cleanup is performed
    for every fixture that was setup before the setup-error occured.

    .. code-block:: python

        # -- BAD-EXAMPLE: Simplistic composite-fixture
        # NOTE: Created fixtures (fixture1) are not cleaned up.
        @fixture
        def foo_and_bad0(context, *args, **kwargs):
            the_fixture1 = setup_fixture_foo(*args, **kwargs)
            the_fixture2 = setup_fixture_bar_with_error("OOPS-HERE")
            yield (the_fixture1, the_fixture2)  # NOT_REACHED.
            # -- NOT_REACHED: Due to fixture2-setup-error.
            the_fixture1.cleanup()  # NOT-CALLED (SAD).
            the_fixture2.cleanup()  # OOPS, the_fixture2 is None (if called).

    .. code-block:: python

        # -- GOOD-EXAMPLE: Sane composite-fixture
        # NOTE: Fixture foo.cleanup() occurs even after fixture2-setup-error.
        @fixture
        def foo(context, *args, **kwargs):
            the_fixture = setup_fixture_foo(*args, **kwargs)
            yield the_fixture
            cleanup_fixture_foo(the_fixture)

        @fixture
        def bad_with_setup_error(context, *args, **kwargs):
            raise RuntimeError("BAD-FIXTURE-SETUP")

        # -- SOLUTION 1: With use_fixture()
        @fixture
        def foo_and_bad1(context, *args, **kwargs):
            the_fixture1 = use_fixture(foo, context, *args, **kwargs)
            the_fixture2 = use_fixture(bad_with_setup_error, context, "OOPS")
            return (the_fixture1, the_fixture2) # NOT_REACHED

        # -- SOLUTION 2: With use_composite_fixture_with()
        @fixture
        def foo_and_bad2(context, *args, **kwargs):
            the_fixture = use_composite_fixture_with(context, [
                fixture_call_params(foo, *args, **kwargs),
                fixture_call_params(bad_with_setup_error, "OOPS")
             ])
            return the_fixture

    :param context:     Runtime context object, used for all fixtures.
    :param fixture_funcs_with_params: List of fixture functions with params.
    :return: List of created fixture objects.
    """
    composite_fixture = []
    for fixture_func, args, kwargs in fixture_funcs_with_params:
        the_fixture = use_fixture(fixture_func, context, *args, **kwargs)
        composite_fixture.append(the_fixture)
    return composite_fixture



# -------------------------------------------------------------------------------
# DECORATORS:
# -------------------------------------------------------------------------------
def fixture(func=None, name=None, pattern=None):
    """Fixture decorator (currently mostly syntactic sugar).

    .. code-block:: python

        # -- FILE: features/environment.py
        # CASE FIXTURE-GENERATOR-FUNCTION (like @contextlib.contextmanager):
        @fixture
        def foo(context, *args, **kwargs):
            the_fixture = setup_fixture_foo(*args, **kwargs)
            context.foo = the_fixture
            yield the_fixture
            cleanup_fixture_foo(the_fixture)

        # CASE FIXTURE-FUNCTION: No cleanup or cleanup via context-cleanup.
        @fixture(name="fixture.bar")
        def bar(context, *args, **kwargs):
            the_fixture = setup_fixture_bar(*args, **kwargs)
            context.bar = the_fixture
            context.add_cleanup(cleanup_fixture_bar, the_fixture.cleanup)
            return the_fixture

    :param name:    Specifies the fixture tag name (as string).

    .. seealso::

        * :func:`contextlib.contextmanager` decorator
        * `@pytest.fixture`_
    """
    def mark_as_fixture(func, name=None, pattern=None):
        func.name = name
        func.pattern = pattern
        func.behave_fixture = True
        return func

    if func is None:
        # CASE: @fixture()
        # CASE: @fixture(name="foo")
        def decorator(func):
            return mark_as_fixture(func, name, pattern=pattern)
        return decorator
    elif callable(func):
        # CASE: @fixture
        return mark_as_fixture(func, name, pattern=pattern)
    else:
        # -- OOPS: Should be callable-object or None
        message = "Invalid func: func=%r, name=%r" % (func, name)
        raise TypeError(message)
