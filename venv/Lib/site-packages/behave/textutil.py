# -*- coding: utf-8 -*-
"""
Provides some utility functions related to text processing.
"""

from __future__ import absolute_import, print_function
import codecs
import os
import sys
import six

# -----------------------------------------------------------------------------
# CONSTANTS:
# -----------------------------------------------------------------------------
# DEFAULT STRATEGY: For error handling when unicode-strings are converted.
BEHAVE_UNICODE_ERRORS = os.environ.get("BEHAVE_UNICODE_ERRORS", "replace")


# -----------------------------------------------------------------------------
# FUNCTIONS:
# -----------------------------------------------------------------------------
def make_indentation(indent_size, part=u" "):
    """Creates an indentation prefix string of the given size."""
    return indent_size * part


def indent(text, prefix):   # pylint: disable=redefined-outer-name
    """Indent text or a number of text lines (with newline).

    :param lines:  Text lines to indent (as string or list of strings).
    :param prefix: Line prefix to use (as string).
    :return: Indented text (as unicode string).
    """
    lines = text
    newline = u""
    if isinstance(text, six.string_types):
        lines = text.splitlines(True)
    elif lines and not lines[0].endswith("\n"):
        # -- TEXT LINES: Without trailing new-line.
        newline = u"\n"
    # MAYBE: return newline.join([prefix + six.text_type(line, errors="replace")
    return newline.join([prefix + six.text_type(line)  for line in lines])


def compute_words_maxsize(words):
    """Compute the maximum word size from a list of words (or strings).

    :param words: List of words (or strings) to use.
    :return: Maximum size of all words.
    """
    max_size = 0
    for word in words:
        if len(word) > max_size:
            max_size = len(word)
    return max_size


def is_ascii_encoding(encoding):
    """Checks if a given encoding is ASCII."""
    try:
        return codecs.lookup(encoding).name == "ascii"
    except LookupError:
        return False

def select_best_encoding(outstream=None):
    """Select the *best* encoding for an output stream/file.
    Uses:
    * ``outstream.encoding`` (if available)
    * ``sys.getdefaultencoding()`` (otherwise)

    Note: If encoding=ascii, uses encoding=UTF-8

    :param outstream:  Output stream to select encoding for (or: stdout)
    :return: Unicode encoding name (as string) to use (for output stream).
    """
    outstream = outstream or sys.stdout
    encoding = getattr(outstream, "encoding", None) or sys.getdefaultencoding()
    if is_ascii_encoding(encoding):
        # -- REQUIRED-FOR: Python2
        # MAYBE: locale.getpreferredencoding()
        return "utf-8"
    return encoding


def text(value, encoding=None, errors=None):
    """Convert into a unicode string.

    :param value:  Value to convert into a unicode string (bytes, str, object).
    :return: Unicode string

    SYNDROMES:
      * Convert object to unicode: Has only __str__() method (Python2)
      * Windows: exception-traceback and encoding=unicode-escape are BAD
      * exception-traceback w/ weird encoding or bytes

    ALTERNATIVES:
      * Use traceback2 for Python2: Provides unicode tracebacks
    """
    if encoding is None:
        encoding = select_best_encoding()
    if errors is None:
        errors = BEHAVE_UNICODE_ERRORS

    if isinstance(value, six.text_type):
        # -- CASE: ALREADY UNICODE (pass-through, efficiency):
        return value
    elif isinstance(value, six.binary_type):
        # -- CASE: bytes/binary_type (Python2: str)
        try:
            return six.text_type(value, encoding, errors)
        except UnicodeError:
            # -- BEST-EFFORT:
            return six.u(value)
    # elif isinstance(value, bytes):
    #     # -- MAYBE: filename, path, etc.
    #     try:
    #         return value.decode(sys.getfilesystemencoding())
    #     except UnicodeError:
    #         return value.decode("utf-8", "replace") # MAYBE: "ignore"
    else:
        # -- CASE: CONVERT/CAST OBJECT TO TEXT/STRING
        try:
            if six.PY2:
                try:
                    text2 = six.text_type(value)
                except UnicodeError as e:
                    # -- NOTE: value has no sane unicode conversion
                    #  encoding=unicode-escape helps recover from errors.
                    data = str(value)
                    text2 = six.text_type(data, "unicode-escape", "replace")
            else:
                # PY3: Cast to string/unicode
                text2 = six.text_type(value)
        except UnicodeError as e:
            # Python3: multi-arg call supports only string-like object: str, bytes
            text2 = six.text_type(e)
        return text2


def to_texts(args, encoding=None, errors=None):
    """Process a list of string-like objects into list of unicode values.
    Optionally converts binary text into unicode for each item.
    
    :return: List of text/unicode values.
    """
    if encoding is None:
        encoding = select_best_encoding()
    return [text(arg, encoding, errors) for arg in args]


def ensure_stream_with_encoder(stream, encoding=None):
    if not encoding:
        encoding = select_best_encoding(stream)

    if six.PY3:
        return stream
    elif hasattr(stream, "stream"):
        return stream    # Already wrapped with a codecs.StreamWriter
    else:
        assert six.PY2
        # py2 does, however, sometimes declare an encoding on sys.stdout,
        # even if it doesn't use it (or it might be explicitly None)
        stream = codecs.getwriter(encoding)(stream)
        return stream
