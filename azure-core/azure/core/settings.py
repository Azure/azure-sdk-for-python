# --------------------------------------------------------------------------
#
# Copyright (c) Microsoft Corporation. All rights reserved.
#
# The MIT License (MIT)
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the ""Software""), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED *AS IS*, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#
# --------------------------------------------------------------------------
"""Provide access to settings for globally used Azure configuration values.


"""

import logging
import os


__all__ = ("settings",)


class _Unset(object):
    pass


class PrioritizedSetting(object):
    """Return a value for a global setting according to configuration precedence.

    The following methods are searched in order for the setting:

    4. immediate values
    3. previously user-set value
    2. environment variable
    1. system setting
    0. implicit default

    If a value cannot be determined, a RuntimeError is raised.

    The ``env_var`` argument specifies the name of an environmen to check for
    setting values, e.g. ``"AZURE_LOG_LEVEL"``.

    The optional ``system_hook`` can be used to specify a function that will
    attempt to look up a value for the setting from system-wide configurations.

    The optional ``default`` argument specified an implicit default value for
    the setting that is returned if no other methods provide a value.

    A ``convert`` agument may be provided to convert values before they are
    returned. For instance to concert log levels in environement variables
    to ``logging`` module values.

    """

    def __init__(
        self, name, env_var=None, system_hook=None, default=_Unset, convert=None
    ):

        self._name = name
        self._env_var = env_var
        self._system_hook = system_hook
        self._default = default
        self._convert = convert if convert else lambda x: x
        self._user_value = _Unset

    def __repr__(self):
        return "PrioritizedSetting(%r)" % self._name

    def __call__(self, value=None):
        """Return the setting value according to the standard precedence.

        :param time: value
        :type time: str or int or float or None (default: None)
        :returns: the value of the setting
        :rtype: str or int or float
        :raises: RuntimeError

        """
        # 4. immediate values
        if value is not None:
            return self._convert(value)

        # 3. previously user-set value
        if self._user_value is not _Unset:
            return self._convert(self._user_value)

        # 2. environment variable
        if self._env_var and self._env_var in os.environ:
            return self._convert(os.environ[self._env_var])

        # 1. system setting
        if self._system_hook:
            return self._convert(self._system_hook())

        # 0. implicit default
        if self._default is not _Unset:
            return self._convert(self._default)

        raise RuntimeError("No configured value found for setting %r" % self._name)

    def __get__(self, instance, owner):
        return self

    def __set__(self, instance, value):
        self.set_value(value)

    def set_value(self, value):
        """Specify a value for this setting programmatically.

        A value set this way takes precedence over all other methods except
        immediate values.

        :param time: a user-set value for this setting
        :type time: str or int or float
        :returns: None

        """
        self._user_value = value


class Settings(object):
    """Settings for globally used Azure configuration values.

    The following methods are searched in order for a setting:

    4. immediate values
    3. previously user-set value
    2. environment variable
    1. system setting
    0. implicit default

    An implicit default is (optionally) defined by the setting attribute itself.

    A system setting value can be obtained from registries or other OS configuration
    for settings that support that method.

    An environment variable value is obtained from ``os.nviron``

    User-set values many be specified by assigning to the attribute:

    .. code-block:: python

        settings.log_level = log_level = logging.DEBUG

    Immediate values are (optionally) provided when the setting is retrieved:

    .. code-block:: python

        settings.log_level(logging.DEBUG()

    Immediate values are most often useful to provide from optional arguments
    to client functions. If the argument value is not None, it will be returned
    as-is. Otherwise, the setting searches other methods according to the
    precedence rules.

    :Attributes:

    :cvar log_level: a log level to use across all Azure client SDKs (AZURE_LOG_LEVEL)
    :type log_level: PrioritizedSetting
    :cvar proxy_settings: proxy settings to use across all Axure client SDKs (AZURE_PROXY_SETTINGS)
    :type proxy_settings: PrioritizedSetting

    :Example:

    >>> import logging
    >>> from azure.core.settings import settings
    >>> settings.log_level = logging.DEBUG
    >>> settings.log_level()
    10

    >>> settings.log_level(logging.WARN)
    30

    """

    log_level = PrioritizedSetting(
        "log_level", env_var="AZURE_LOG_LEVEL", convert=int, default=logging.INFO
    )

    proxy_settings = PrioritizedSetting(
        "proxy_settings", env_var="AZURE_PROXY_SETTINGS"
    )


settings = Settings()
