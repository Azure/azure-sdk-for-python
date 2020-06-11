# -*- coding: UTF-8 -*-
"""
Functionality to support user-specific configuration data (userdata).
"""

from __future__ import absolute_import
from behave._types import Unknown


# -----------------------------------------------------------------------------
# FUNCTIONS:
# -----------------------------------------------------------------------------
def parse_bool(text):
    """Parses a boolean text and converts it into boolean value (if possible).
    Supported truth string values:

      * true:   "true", "yes", "on", "1"
      * false:  "false", "no", "off", "0"

    :raises: ValueError, if text is invalid
    """
    from distutils.util import strtobool
    return bool(strtobool(text))


def parse_user_define(text):
    """Parse "{name}={value}" text and return parts as tuple.
    Used for command-line definitions, like "... -D name=value".

    SUPPORTED SCHEMA:

      * "{name}={value}"
      * "{name}"                (boolean flag; value="true")
      * '"{name}={value}"'      (double-quoted name-value pair)
      * "'{name}={value}'"      (single-quoted name-value pair)
      * '{name}="{value}"'      (double-quoted value)
      * "{name}='{value}'"      (single-quoted value)
      * "  {name} = {value}  "  (whitespace padded)

    .. note:: Leading/trailing Quotes are stripped.

    :param text:    Text to parse (as string).
    :return: (name, value) pair as tuple.
    """
    text = text.strip()
    if "=" in text:
        text = unqote(text)
        name, value = text.split("=", 1)
        name = name.strip()
        value = unqote(value.strip())
    else:
        # -- ASSUMPTION: Boolean definition (as flag)
        name = text
        value = "true"
    return (name, value)


def unqote(text):
    """Strip pair of leading and trailing quotes from text."""
    # -- QUOTED: Strip single-quote or double-quote pair.
    if ((text.startswith('"') and text.endswith('"')) or
            (text.startswith("'") and text.endswith("'"))):
        text = text[1:-1]
    return text

# -----------------------------------------------------------------------------
# CLASSES:
# -----------------------------------------------------------------------------
class UserData(dict):
    """Dictionary-like user-data with some additional features:

      * type-converter methods, similar to configparser.ConfigParser.getint()

    """

    def getas(self, convert, name, default=None, valuetype=None):
        """Converts the value of user-data parameter from a string into a
        specific value type.

        :param convert: Converter function to use (string to value-type).
        :param name:    Variable name to use.
        :param default: Default value, used if parameter is not found.
        :param valuetype: Value type(s), needed if convert != valuetype()
        :return: Converted textual value (type: valuetype)
        :return: Default value, if parameter is unknown.
        :raises ValueError: If type conversion fails.
        """
        if valuetype is None:
            # -- ASSUME: Converter function is the type constructor.
            valuetype = convert

        value = self.get(name, Unknown)
        if value is Unknown:
            return default
        elif isinstance(value, valuetype):
            # -- PRESERVE: Pre-converted value if type matches.
            return value
        else:
            # -- CASE: Textual value (expected)
            # Raise ValueError if parse/conversion fails.
            assert callable(convert)
            return convert(value)

    def getint(self, name, default=0):
        """Convert parameter value (as string) into a integer value.
        :return: Parameter value as integer number (on success).
        :raises: ValueError, if type conversion fails.
        """
        return self.getas(int, name, default)

    def getfloat(self, name, default=0.0):
        """Convert parameter value (as string) into a float value.
        :return: Parameter value as float number (on success).
        :raises: ValueError, if type conversion fails.
        """
        return self.getas(float, name, default)

    def getbool(self, name, default=False):
        """Converts user-data string-value into boolean value (if possible).
        Supported truth string values:

          * true:   "true", "yes", "on", "1"
          * false:  "false", "no", "off", "0"

        :param name: Parameter name (as string).
        :param default: Default value, if parameter is unknown (=False).
        :return: Boolean value of parameter
        :raises: ValueError, if type conversion fails.
        """
        return self.getas(parse_bool, name, default, valuetype=bool)

    @classmethod
    def make(cls, data):
        if data is None:
            data = cls()
        elif not isinstance(data, cls):
            data = cls(data)
        return data


class UserDataNamespace(object):
    """Provides a light-weight dictview to the user data that allows you
    to access all params in a namespace, that use "{namespace}.*" names.

    .. code-block:: python

        my_config = UserDataNamespace("my.config", userdata)
        value1 = my_config.getint("value1")  # USE: my.config.value1
        value2 = my_config.get("value2")     # USE: my.config.value2
    """

    def __init__(self, namespace, data=None):
        self.namespace = namespace or ""
        self.data = UserData.make(data)

    @staticmethod
    def make_scoped(namespace, name):
        """Creates a scoped-name from its parts."""
        if not namespace:   # noqa
            return name
        return "%s.%s" % (namespace, name)

    # -- DICT-LIKE:
    def get(self, name, default=None):
        scoped_name = self.make_scoped(self.namespace, name)
        return self.data.get(scoped_name, default)

    def getas(self, convert, name, default=None, valuetype=None):
        scoped_name = self.make_scoped(self.namespace, name)
        return self.data.getas(convert, scoped_name, default=default,
                               valuetype=valuetype)

    def getint(self, name, default=0):
        scoped_name = self.make_scoped(self.namespace, name)
        return self.data.getint(scoped_name, default=default)

    def getfloat(self, name, default=0.0):
        scoped_name = self.make_scoped(self.namespace, name)
        return self.data.getfloat(scoped_name, default=default)

    def getbool(self, name, default=False):
        scoped_name = self.make_scoped(self.namespace, name)
        return self.data.getbool(scoped_name, default=default)

    def __contains__(self, name):
        scoped_name = self.make_scoped(self.namespace, name)
        return scoped_name in self.data

    def __getitem__(self, name):
        scoped_name = self.make_scoped(self.namespace, name)
        return self.data[scoped_name]

    def __setitem__(self, name, value):
        scoped_name = self.make_scoped(self.namespace, name)
        self.data[scoped_name] = value

    def __len__(self):
        return len(self.scoped_keys())

    def scoped_keys(self):
        if not self.namespace:  # noqa
            return self.data.keys()
        prefix = "%s." % self.namespace
        return [key for key in self.data.keys() if key.startswith(prefix)]

    def keys(self):
        prefix = "%s." % self.namespace
        for scoped_name in self.scoped_keys():
            name = scoped_name.replace(prefix, "", 1)
            yield name

    def values(self):
        for scoped_name in self.scoped_keys():
            yield self.data[scoped_name]

    def items(self):
        for name in self.keys():
            scoped_name = self.make_scoped(self.namespace, name)
            value = self.data[scoped_name]
            yield (name, value)
