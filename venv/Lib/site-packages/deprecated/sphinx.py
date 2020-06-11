# coding: utf-8
"""
Sphinx directive integration
============================

We usually need to document the life-cycle of functions and classes:
when they are created, modified or deprecated.

To do that, `Sphinx <http://www.sphinx-doc.org>`_ has a set
of `Paragraph-level markups <http://www.sphinx-doc.org/en/stable/markup/para.html>`_:

- ``versionadded``: to document the version of the project which added the described feature to the library,
- ``versionchanged``: to document changes of a feature,
- ``deprecated``: to document a deprecated feature.

The purpose of this module is to defined decorators which adds this Sphinx directives
to the docstring of your function and classes.

Of course, the ``@deprecated`` decorator will emit a deprecation warning
when the function/method is called or the class is constructed.
"""
import textwrap

import wrapt

from deprecated.classic import ClassicAdapter
from deprecated.classic import deprecated as _classic_deprecated


class SphinxAdapter(ClassicAdapter):
    """
    Sphinx adapter -- *for advanced usage only*

    This adapter override the :class:`~deprecated.classic.ClassicAdapter`
    in order to add the Sphinx directives to the end of the function/class docstring.
    Such a directive is a `Paragraph-level markup <http://www.sphinx-doc.org/en/stable/markup/para.html>`_

    - The directive can be one of "versionadded", "versionchanged" or "deprecated".
    - The version number is added if provided.
    - The reason message is obviously added in the directive block if not empty.
    """

    def __init__(self, directive, reason="", version="", action=None, category=DeprecationWarning):
        """
        Construct a wrapper adapter.

        :type  directive: str
        :param directive:
            Sphinx directive: can be one of "versionadded", "versionchanged" or "deprecated".

        :type  reason: str
        :param reason:
            Reason message which documents the deprecation in your library (can be omitted).

        :type  version: str
        :param version:
            Version of your project which deprecates this feature.
            If you follow the `Semantic Versioning <https://semver.org/>`_,
            the version number has the format "MAJOR.MINOR.PATCH".

        :type  action: str
        :param action:
            A warning filter used to activate or not the deprecation warning.
            Can be one of "error", "ignore", "always", "default", "module", or "once".
            If ``None`` or empty, the the global filtering mechanism is used.
            See: `The Warnings Filter`_ in the Python documentation.

        :type  category: type
        :param category:
            The warning category to use for the deprecation warning.
            By default, the category class is :class:`~DeprecationWarning`,
            you can inherit this class to define your own deprecation warning category.
        """
        self.directive = directive
        super(SphinxAdapter, self).__init__(reason=reason, version=version, action=action, category=category)

    def __call__(self, wrapped):
        """
        Add the Sphinx directive to your class or function.

        :param wrapped: Wrapped class or function.

        :return: the decorated class or function.
        """
        reason = textwrap.dedent(self.reason).strip()
        reason = '\n'.join(
            textwrap.fill(line, width=70, initial_indent='   ', subsequent_indent='   ') for line in reason.splitlines()
        ).strip()
        docstring = textwrap.dedent(wrapped.__doc__ or "")
        if docstring:
            docstring += "\n\n"
        if self.version:
            docstring += ".. {directive}:: {version}\n".format(directive=self.directive, version=self.version)
        else:
            docstring += ".. {directive}::\n".format(directive=self.directive)
        if reason:
            docstring += "   {reason}\n".format(reason=reason)
        wrapped.__doc__ = docstring
        return super(SphinxAdapter, self).__call__(wrapped)


def versionadded(reason="", version=""):
    """
    This decorator can be used to insert a "versionadded" directive
    in your function/class docstring in order to documents the
    version of the project which adds this new functionality in your library.

    :param str reason:
        Reason message which documents the addition in your library (can be omitted).

    :param str version:
        Version of your project which adds this feature.
        If you follow the `Semantic Versioning <https://semver.org/>`_,
        the version number has the format "MAJOR.MINOR.PATCH", and,
        in the case of a new functionality, the "PATCH" component should be "0".

    :return: the decorated function.
    """
    adapter = SphinxAdapter('versionadded', reason=reason, version=version)

    # noinspection PyUnusedLocal
    @wrapt.decorator(adapter=adapter)
    def wrapper(wrapped, instance, args, kwargs):
        return wrapped(*args, **kwargs)

    return wrapper


def versionchanged(reason="", version=""):
    """
    This decorator can be used to insert a "versionchanged" directive
    in your function/class docstring in order to documents the
    version of the project which modifies this functionality in your library.

    :param str reason:
        Reason message which documents the modification in your library (can be omitted).

    :param str version:
        Version of your project which modifies this feature.
        If you follow the `Semantic Versioning <https://semver.org/>`_,
        the version number has the format "MAJOR.MINOR.PATCH".

    :return: the decorated function.
    """
    adapter = SphinxAdapter('versionchanged', reason=reason, version=version)

    # noinspection PyUnusedLocal
    @wrapt.decorator(adapter=adapter)
    def wrapper(wrapped, instance, args, kwargs):
        return wrapped(*args, **kwargs)

    return wrapper


def deprecated(*args, **kwargs):
    """
    This decorator can be used to insert a "deprecated" directive
    in your function/class docstring in order to documents the
    version of the project which deprecates this functionality in your library.

    Keyword arguments can be:

    -   "reason":
        Reason message which documents the deprecation in your library (can be omitted).

    -   "version":
        Version of your project which deprecates this feature.
        If you follow the `Semantic Versioning <https://semver.org/>`_,
        the version number has the format "MAJOR.MINOR.PATCH".

    -   "action":
        A warning filter used to activate or not the deprecation warning.
        Can be one of "error", "ignore", "always", "default", "module", or "once".
        If ``None``, empty or missing, the the global filtering mechanism is used.

    -   "category":
        The warning category to use for the deprecation warning.
        By default, the category class is :class:`~DeprecationWarning`,
        you can inherit this class to define your own deprecation warning category.

    :return: the decorated function.
    """
    directive = kwargs.pop('directive', 'deprecated')
    adapter_cls = kwargs.pop('adapter_cls', SphinxAdapter)
    return _classic_deprecated(*args, directive=directive, adapter_cls=adapter_cls, **kwargs)
