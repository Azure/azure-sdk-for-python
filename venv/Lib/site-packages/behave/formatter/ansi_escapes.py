# -*- coding: utf-8 -*-
"""
Provides ANSI escape sequences for coloring/formatting output in ANSI terminals.
"""

from __future__ import absolute_import
import os
import re

colors = {
    "black":        u"\x1b[30m",
    "red":          u"\x1b[31m",
    "green":        u"\x1b[32m",
    "yellow":       u"\x1b[33m",
    "blue":         u"\x1b[34m",
    "magenta":      u"\x1b[35m",
    "cyan":         u"\x1b[36m",
    "white":        u"\x1b[37m",
    "grey":         u"\x1b[90m",
    "bold":         u"\x1b[1m",
}

aliases = {
    "untested":     "cyan",     # SAME-COLOR AS: skipped
    "undefined":    "yellow",
    "pending":      "yellow",
    "executing":    "grey",
    "failed":       "red",
    "passed":       "green",
    "outline":      "cyan",
    "skipped":      "cyan",
    "comments":     "grey",
    "tag":          "cyan",
}

escapes = {
    "reset":        u"\x1b[0m",
    "up":           u"\x1b[1A",
}

if "GHERKIN_COLORS" in os.environ:
    new_aliases = [p.split("=") for p in os.environ["GHERKIN_COLORS"].split(":")]
    aliases.update(dict(new_aliases))

for alias in aliases:
    escapes[alias] = "".join([colors[c] for c in aliases[alias].split(",")])
    arg_alias = alias + "_arg"
    arg_seq = aliases.get(arg_alias, aliases[alias] + ",bold")
    escapes[arg_alias] = "".join([colors[c] for c in arg_seq.split(",")])


# pylint: disable=anomalous-backslash-in-string
def up(n):
    return u"\x1b[%dA" % n


_ANSI_ESCAPE_PATTERN = re.compile(u"\x1b\[\d+[mA]", re.UNICODE)
# pylint: enable=anomalous-backslash-in-string
def strip_escapes(text):
    """
    Removes ANSI escape sequences from text (if any are contained).

    :param text: Text that may or may not contain ANSI escape sequences.
    :return: Text without ANSI escape sequences.
    """
    return _ANSI_ESCAPE_PATTERN.sub("", text)


def use_ansi_escape_colorbold_composites():     # pragma: no cover
    """
    Patch for "sphinxcontrib-ansi" to process the following ANSI escapes
    correctly (set-color set-bold sequences):

        ESC[{color}mESC[1m  => ESC[{color};1m

    Reapply aliases to ANSI escapes mapping.
    """
    # NOT-NEEDED: global escapes
    color_codes = {}
    for color_name, color_escape in colors.items():
        color_code = color_escape.replace(u"\x1b[", u"").replace(u"m", u"")
        color_codes[color_name] = color_code

    # pylint: disable=redefined-outer-name
    for alias in aliases:
        parts = [color_codes[c] for c in aliases[alias].split(",")]
        composite_escape = u"\x1b[{0}m".format(u";".join(parts))
        escapes[alias] = composite_escape

        arg_alias = alias + "_arg"
        arg_seq = aliases.get(arg_alias, aliases[alias] + ",bold")
        parts = [color_codes[c] for c in arg_seq.split(",")]
        composite_escape = u"\x1b[{0}m".format(u";".join(parts))
        escapes[arg_alias] = composite_escape
