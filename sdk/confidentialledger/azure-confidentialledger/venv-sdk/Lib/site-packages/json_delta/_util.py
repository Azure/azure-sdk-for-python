# -*- coding: utf-8 -*-
# json_delta: a library for computing deltas between JSON-serializable
# structures.
# json_delta/_util.py
#
# Copyright 2012‒2020 Philip J. Roberts <himself@phil-roberts.name>.
# BSD License applies; see the LICENSE file, or
# http://opensource.org/licenses/BSD-2-Clause
'''Utility functions and constants used by more than one submodule.

The majority of python 2/3 compatibility shims also appear in this
module.

'''

from __future__ import print_function, unicode_literals

import sys
import json
import codecs
import itertools

try:
    from itertools import izip as zip
except ImportError:
    zip = zip

try:
    Basestring = basestring
except NameError:
    Basestring = str

try:
    IntegerTypes = (int, long)
except NameError:
    IntegerTypes = (int,)

TERMINALS = (str, int, float, bool, type(None))
try:
    TERMINALS += (unicode, long)
except NameError:
    pass
NONTERMINALS = (list, tuple, dict)
SERIALIZABLE_TYPES = TERMINALS + NONTERMINALS
NUMERIC_TYPES = IntegerTypes + (float,)

ENCODINGS = ('utf_8', 'utf_16_le', 'utf_16_be', 'utf_32_le', 'utf_32_be')

try:
    range = xrange
except NameError:
    range = range

dump_test = json.dumps((True, False), indent=1)
SPACE_AFTER_COMMA = ', ' in dump_test


def licit_starts(start_chars='{}[]"-0123456789tfn \t\n\r'):
    '''Compute the bytestrings a UTF-x encoded string can begin with.

    This function is intended for encoding detection when the
    beginning of the encoded string must be one of a limited set of
    characters, as for JSON or the udiff format.  The argument
    ``start_chars`` must be an iterable of valid beginnings.

    '''
    bom_attr_name = lambda e: 'BOM_{}'.format(e.upper().replace('_', '', 1))
    out = {getattr(codecs, bom_attr_name(k)): k[:6] for k in ENCODINGS}
    out[codecs.BOM_UTF8] = 'utf_8_sig'
    for encoding, start in itertools.product(ENCODINGS, start_chars):
        start = start.encode(encoding)
        assert start not in out, (start, out[start], encoding)
        out[start] = encoding
    return out


JSON_STARTS = licit_starts('{}[]"-0123456789tfn \t\n\r')
UDIFF_STARTS = licit_starts(' +-')


def sniff_encoding(bytestring, starts=JSON_STARTS, complete=True):
    r'''Determine the encoding of a UTF-x encoded string.

    The argument ``starts`` must be a mapping of bytestrings the input
    can begin with onto the encoding that such a beginning would
    represent (see :func:`licit_starts` for a function that can build
    such a mapping).

    The ``complete`` flag signifies whether the input represents the
    entire string: if it is set ``False``, the function will attempt
    to determine the encoding, but will raise a ``UnicodeError`` if it
    is ambiguous.  For example, an input of ``b'\xff\xfe'`` could be
    the UTF-16 little-endian byte-order mark, or, if the input is
    incomplete, it could be the first two characters of the UTF-32-LE
    BOM:

    >>> sniff_encoding(b'\xff\xfe') == 'utf_16'
    True
    >>> sniff_encoding(b'\xff\xfe', complete=False)
    Traceback (most recent call last):
        ...
    UnicodeError: String encoding is ambiguous.

    '''
    iteritems = getattr(starts, 'iteritems', starts.items)
    test = (lambda k, p: k == p if complete
            else lambda k, p: k.startswith(p))
    candidates = set()
    for limit in range(min(4, len(bytestring)), 0, -1):
        prefix = bytestring[:limit]
        candidates = set([v for k, v in iteritems() if test(k, prefix)])
        if len(candidates) == 1:
            return next(iter(candidates))
    if not candidates:
        raise ValueError('String does not begin with '
                         'any of the specified start chars.')
    else:
        raise UnicodeError('String encoding is ambiguous.')


def decode_json(file_or_str):
    '''Decode a JSON file-like object or string.

    The following doctest is probably pointless as documentation.  It is
    here so json-delta can claim 100% code coverage for its test suite!

    >>> try:
    ...     from StringIO import StringIO
    ... except ImportError:
    ...     from io import StringIO
    >>> foo = '[]'
    >>> decode_json(foo)
    []
    >>> decode_json(StringIO(foo))
    []
    '''
    if isinstance(file_or_str, bytes):
        file_or_str = file_or_str.decode(
            sniff_encoding(file_or_str, JSON_STARTS)
        )
    if isinstance(file_or_str, Basestring):
        return json.loads(file_or_str)
    return decode_json(read_bytestring(file_or_str))


def decode_udiff(file_or_str):
    r'''Decode a file-like object or bytestring udiff into a unicode string.

    The udiff may be encoded in UTF-8, -16 or -32 (with or without BOM):

    >>> udiff = u'- true\n+ false'
    >>> decode_udiff(udiff.encode('utf_32_be')) == udiff
    True
    >>> try:
    ...     from StringIO import StringIO
    ... except ImportError:
    ...     from io import BytesIO as StringIO
    >>> decode_udiff(StringIO(udiff.encode('utf-8-sig'))) == udiff
    True

    An empty string is a valid udiff; this function will convert it to
    a unicode string:

    >>> decode_udiff(b'') == u''
    True

    The function is idempotent: if you pass it a unicode string, it
    will be returned unmodified:

    >>> decode_udiff(udiff) is udiff
    True

    If you pass it a non-empty bytestring that cannot be interpreted
    as beginning with ``' '``, ``'+'``, ``'-'`` or a BOM in any
    encoding, a ``ValueError`` is raised:

    >>> decode_udiff(b':-)')
    Traceback (most recent call last):
        ...
    ValueError: String does not begin with any of the specified start chars.

    '''
    if isinstance(file_or_str, bytes):
        if not file_or_str:
            file_or_str = u''
        else:
            file_or_str = file_or_str.decode(
                sniff_encoding(file_or_str, UDIFF_STARTS)
            )
    if isinstance(file_or_str, Basestring):
        return file_or_str
    return decode_udiff(read_bytestring(file_or_str))


def read_bytestring(file):
    '''Read the contents of ``file`` as a :class:`bytes` object.'''
    file = getattr(file, 'buffer', file)
    bytestring = file.read()
    return bytestring


def predicate_count(iterable, predicate=lambda x: True):
    '''Count items ``x`` in ``iterable`` such that ``predicate(x)``.

    The default ``predicate`` is ``lambda x: True``, so
    ``predicate_count(iterable)`` will count the values generated by
    ``iterable``.  Note that if the iterable is a generator, this
    function will exhaust it, and if it is an infinite generator, this
    function will never return!

    >>> predicate_count([True] * 16)
    16
    >>> predicate_count([True, True, False, True, True], lambda x: x)
    4

    '''
    count = 0
    for item in iterable:
        if predicate(item):
            count += 1
    return count


def uniquify(obj, key=lambda x: x):
    '''Remove duplicate elements from a list while preserving order.

    ``key`` works as for :func:`min`, :func:`max`, etc. in the
    standard library.

    '''
    seen = set()
    seen_add = seen.add
    return [
        x for x in obj if (key(x) not in seen and not seen_add(key(x)))
    ]


def _load_and_func(func, parm1=None, parm2=None, both=None, **flags):
    '''Decode JSON-serialized parameters and apply func to them.'''
    if (parm1 is not None) and (parm2 is not None):
        return func(decode_json(parm1), decode_json(parm2), **flags)
    else:
        assert (both is not None), (parm1, parm2, both)
        [parm1, parm2] = decode_json(both)
        return func(parm1, parm2, **flags)


def stanzas_addressing(stanzas, keypath):
    '''Find diff stanzas modifying the structure at ``keypath``.

    The purpose of this function is to keep track of changes made to
    the overall structure by stanzas earlier in the sequence, e.g.:

    >>> struc = [
    ...     'foo',
    ...     'bar', [
    ...         'baz'
    ...     ]
    ... ]
    >>> stanzas = [
    ...     [ [2, 1], 'quux'],
    ...     [ [0] ],
    ...     [ [1, 2], 'quordle']
    ... ]
    >>> (stanzas_addressing(stanzas, [2])
    ...  == [
    ...   [ [1], 'quux' ],
    ...   [ [2], 'quordle' ]
    ...  ])
    True

    ``stanzas[0]`` and ``stanzas[2]`` both address the same element of
    ``struc`` — the list that starts off as ``['baz']``, even though
    their keypaths are completely different, because the diff stanza
    ``[[0]]`` moves the list ``['baz']`` from index 2 of ``struc`` to
    index 1.

    The return value is a sub-diff: a list of stanzas fit to modify
    the element at ``keypath`` within the overall structure.

    '''
    keypath = keypath[:]
    out = []
    for stanza in stanzas:
        stanza_keypath = stanza[0]
        if stanza_keypath[:len(keypath)] == keypath:
            out.append([stanza_keypath[len(keypath):]] + stanza[1:])
        elif (in_array(stanza_keypath)
              and len(stanza) in (1, 3)
              and len(stanza_keypath) <= len(keypath)):
            kp_mutand_pos = len(stanza_keypath) - 1
            assert (keypath[kp_mutand_pos] != stanza_keypath[-1]), \
                (stanza, keypath)
            if keypath[kp_mutand_pos] > stanza_keypath[-1]:
                if len(stanza) == 1:
                    keypath[kp_mutand_pos] -= 1
                else:
                    assert stanza == [stanza_keypath, stanza[1], 'i'], stanza
                    keypath[kp_mutand_pos] += 1
    return out


def in_one_level(stanzas, key):
    return stanzas_addressing(stanzas, [key])


def compact_json_dumps(obj):
    '''Compute the most compact possible JSON representation of ``obj``.

    >>> test = {
    ...             'foo': 'bar',
    ...             'baz':
    ...                ['quux', 'spam',
    ...       'eggs']
    ... }
    >>> compact_json_dumps(test) in (
    ...     '{"foo":"bar","baz":["quux","spam","eggs"]}',
    ...     '{"baz":["quux","spam","eggs"],"foo":"bar"}'
    ... )
    True
    >>>
    '''
    return json.dumps(obj, indent=None, separators=(',', ':'),
                      ensure_ascii=False)


def all_paths(struc):
    '''Generate key-paths to every node in ``struc``.

    Both terminal and non-terminal nodes are visited, like so:

    >>> paths = [x for x in all_paths({'foo': None, 'bar': ['baz', 'quux']})]
    >>> [] in paths # ([] is the path to ``struc`` itself.)
    True
    >>> ['foo'] in paths
    True
    >>> ['bar'] in paths
    True
    >>> ['bar', 0] in paths
    True
    >>> ['bar', 1] in paths
    True
    >>> len(paths)
    5
    '''
    yield []
    if isinstance(struc, dict):
        keys = struc.keys()
    elif isinstance(struc, list):
        keys = range(len(struc))
    else:
        return
    for key in keys:
        for subkey in all_paths(struc[key]):
            yield [key] + subkey


def follow_path(struc, path):
    '''Retrieve the value found at the key-path ``path`` within ``struc``.'''
    if not path:
        return struc
    else:
        return follow_path(struc[path[0]], path[1:])


def check_diff_structure(diff):
    '''Return ``diff`` (or ``True``) if it is structured as a sequence
    of ``diff`` stanzas.  Otherwise return ``False``.

    ``[]`` is a valid diff, so if it is passed to this function, the
    return value is ``True``, so that the return value is always true
    in a Boolean context if ``diff`` is valid.

    >>> check_diff_structure('This is certainly not a diff!')
    False
    >>> check_diff_structure([])
    True
    >>> check_diff_structure([None])
    False
    >>> example_valid_diff = [[["foo", 6, 12815316313, "bar"], None]]
    >>> check_diff_structure(example_valid_diff) == example_valid_diff
    True
    >>> check_diff_structure([[["foo", 6, 12815316313, "bar"], None],
    ...                       [["foo", False], True]])
    False
    '''
    if diff == []:
        return True
    if not isinstance(diff, list):
        return False
    for stanza in diff:
        conditions = (lambda s: isinstance(s, list),
                      lambda s: isinstance(s[0], list),
                      lambda s: len(s) in (1, 2, 3),
                      lambda s: len(s) != 3 or s[2] == 'i')
        for condition in conditions:
            if not condition(stanza):
                return False
        for key in stanza[0]:
            if not (type(key) in IntegerTypes or isinstance(key, Basestring)):
                # Checking type because isinstance(False, int) == True!
                return False
    return diff


def in_x_error(key, offender):
    '''Build the instance of ``ValueError`` :func:`in_object` and
    :func:`in_array` raise if ``keypath`` is invalid.'''
    msg = ('keypath elements must be instances of '
           'str, unicode, int or long,\n'
           '    not {} (key[{}] == {})'.format(
               type(offender).__name__, key.index(offender), repr(offender)
           ))
    return ValueError(msg)


def in_object(key, accept_None=False):
    '''Should the keypath ``key`` point at a JSON object (``{}``)?

    Works by testing whether ``key[-1]`` is a string or (where appropriate)
    :func:`unicode`:

    >>> in_object(["foo"])
    True
    >>> in_object([u'bar'])
    True

    Returns ``False`` if ``key`` addresses an array…

    >>> in_object([u'bar', 16])
    False
    >>> import sys
    >>> False if sys.version >= '3' else eval("in_object([u'bar', 16L])")
    False

    …if ``key == []``…

    >>> in_object([])
    False

    If the ``accept_None`` flag is set, this function will also return
    ``True`` if ``key[-1] is None`` (this functionality is used by
    :func:`key_tracker`, to signal points within a JSON string where a
    new object key is expected, but not yet found).

    >>> in_object([None])
    Traceback (most recent call last):
        ...
    ValueError: keypath elements must be instances of str, unicode, int or long,
        not NoneType (key[0] == None)

    >>> in_object([None], True)
    True
    >>> in_object([None], accept_None=True)
    True

    Raises a ``ValueError`` if ``key`` is not a valid keypath:

    >>> in_object(['foo', {}])
    Traceback (most recent call last):
        ...
    ValueError: keypath elements must be instances of str, unicode, int or long,
        not dict (key[1] == {})

    >>> in_object([False, u'foo'])
    Traceback (most recent call last):
        ...
    ValueError: keypath elements must be instances of str, unicode, int or long,
        not bool (key[0] == False)

    '''

    try:
        offender = next((k for k in key[:-1]
                         if (not isinstance(k, Basestring)
                             and type(k) not in IntegerTypes)))
    except StopIteration:
        pass
    else:
        raise in_x_error(key, offender)
    out = bool(key and (isinstance(key[-1], Basestring)
                        or (accept_None and key[-1] is None)))
    if not out and key and type(key[-1]) not in IntegerTypes:
        raise in_x_error(key, key[-1])
    return out


def in_array(key, accept_None=False):
    '''Should the keypath ``key`` point at a JSON array (``[]``)?

    Works by testing whether ``key[-1]`` is an :class:`int` or
    (where appropriate) :class:`long`:

    >>> in_array([u'bar', 16])
    True
    >>> import sys
    >>> sys.version >= '3' or eval("in_array([u'foo', 94L])")
    True

    Returns ``False`` if ``key`` addresses a non-array object…

    >>> in_array(["foo"])
    False
    >>> in_array([u'bar'])
    False

    …or if ``key == []`` (as in that case there’s no way of knowing
    whether ``key`` addresses an object or an array).

    >>> in_array([])
    False

    If the ``accept_None`` flag is set, this function will not raise a
    ``ValueError`` if ``key[-1] is None`` (keypaths of this form are
    used by :func:`key_tracker`, to signal points within a JSON string
    where a new object key is expected, but not yet found).

    >>> in_array([None])
    Traceback (most recent call last):
        ...
    ValueError: keypath elements must be instances of str, unicode, int or long,
        not NoneType (key[0] == None)

    >>> in_array([None], True)
    False
    >>> in_array([None], accept_None=True)
    False

    Otherwise, a ``ValueError`` is raised if ``key`` is not a valid keypath:

    >>> keypath = [{str("spam"): str("spam")}, "pickled eggs and spam", 7]
    >>> in_array(keypath)
    Traceback (most recent call last):
        ...
    ValueError: keypath elements must be instances of str, unicode, int or long,
        not dict (key[0] == {'spam': 'spam'})

    '''
    try:
        offender = next((k for k in key[:-1]
                         if (not isinstance(k, Basestring)
                             and type(k) not in IntegerTypes)))
    except StopIteration:
        pass
    else:
        raise in_x_error(key, offender)
    if accept_None and key and key[-1] is None:
        return False
    out = bool(key and type(key[-1]) in IntegerTypes)
    if not out and key and not isinstance(key[-1], Basestring):
        raise in_x_error(key, key[-1])
    return out


def nearest_of(string, *subs):
    '''Find the index of the substring in ``subs`` that occurs earliest in
    ``string``, or ``len(string)`` if none of them do.'''
    return min((string.find(x) if x in string else len(string) for x in subs))


def skip_string(jstring, point):
    r'''Assuming ``jstring`` is a string, and ``jstring[point]`` is a ``"`` that
    starts a JSON string, return ``x`` such that ``jstring[x-1]`` is
    the ``"`` that terminates the string.

    When a ``"`` is found, it is necessary to check that it is not
    escaped by a preceding backslash.  As a backslash may itself be
    escaped, this amounts to checking that the number of backslashes
    immediately preceding the ``"`` is even (counting 0 as an even
    number):

    >>> test_string = r'"Fred \"Foonly\" McQuux"'
    >>> skip_string(test_string, 0) == len(test_string)
    True
    >>> backslash = chr(0x5c)
    >>> dbl_quote = chr(0x22)
    >>> even_slashes = ((r'"\\\\\\"', json.dumps(backslash * 3)),
    ...                 (r'"\\\\"',   json.dumps(backslash * 2)),
    ...                 (r'"\\"',     json.dumps(backslash)))
    >>> all((json.loads(L) == json.loads(R) for (L, R) in even_slashes))
    True
    >>> all((skip_string(L, 0) == len(L) for (L, R) in even_slashes))
    True
    >>> def cat_dump(*args): return json.dumps(''.join(args))
    >>> odd_slashes = (
    ...     (r'"\\\\\\\"  "', cat_dump(backslash * 3, dbl_quote, ' ' * 2)),
    ...     (r'"\\\\\"    "', cat_dump(backslash * 2, dbl_quote, ' ' * 4)),
    ...     (r'"\\\"      "', cat_dump(backslash * 1, dbl_quote, ' ' * 6)),
    ...     (r'"\"        "', cat_dump(dbl_quote, ' ' * 8)),
    ... )
    >>> all((json.loads(L) == json.loads(R) for (L, R) in odd_slashes))
    True
    >>> all((skip_string(L, 0) == 12 for (L, R) in odd_slashes))
    True

    '''
    assert jstring[point] == '"'
    point += 1
    backslash_count = 0
    while not (jstring[point] == '"' and backslash_count % 2 == 0):
        if jstring[point] == '\\':
            backslash_count += 1
        else:
            backslash_count = 0
        point += 1
    return point + 1


def key_tracker(jstring, point=0, start_key=None, special_handler=None):
    '''Generate points within ``jstring`` where the keypath changes.

    This function also identifies points within objects where a new
    ``key: value`` pair is expected, by yielding a pseudo-keypath with
    ``None`` as the final element.

    Parameters:
        * ``jstring``: The JSON string to search.

        * ``point``: The point to start at.

        * ``start_key``: The starting keypath.

        * ``special_handler``: A function for handling extensions to
          JSON syntax (e.g. :py:func:`_upatch.ellipsis_handler`, used
          to handle the ``...`` construction in udiffs).

    >>> next(key_tracker('{}'))
    (1, (None,))
    '''
    if start_key is None:
        key = []
    else:
        key = list(start_key)

    while point < len(jstring):
        if jstring[point] == '{':
            key.append(None)
            yield (point + 1, tuple(key))
        elif jstring[point] == '[':
            key.append(0)
            yield (point + 1, tuple(key))
        elif jstring[point] in ']}':
            key.pop()
            yield (point + 1, tuple(key))
        elif jstring[point] == ',':
            if in_object(key, accept_None=True):
                key[-1] = None
            else:
                assert in_array(key, accept_None=True)
                key[-1] += 1
            yield (point + 1, tuple(key))
        elif jstring[point] == '"':
            string_end = skip_string(jstring, point)
            if (key and key[-1] is None):
                key[-1] = json.loads(jstring[point:string_end])
                while (string_end < len(jstring)
                       and jstring[string_end] in ' \r\n\t:'):
                    string_end += 1
                yield (string_end, tuple(key))
            point = string_end - 1
        elif special_handler is not None:
            point, newkey = special_handler(jstring, point, key)
            if key != newkey:
                key = newkey
                yield (point, tuple(key))
        point += 1


def json_bytestring_length(string):
    '''Find the length of the JSON for a string without actually encoding it.

    Attempts to give the shortest possible version: encoding as UTF-8 and
    using escape sequences only where necessary.'''
    length = 2  # for the quote marks
    for char in string:
        figure = ord(char)
        if char in ('"', '\n', '\r', '\f', '\b', '\t', '\\'):
            length += 2
        elif figure <= 0x1F:
            length += 6  # Control characters must be \uXXXX escaped
        elif figure <= 0x7F:
            length += 1
        elif figure <= 0x07FF:
            length += 2
        elif figure <= 0xFFFF:
            length += 3
        else:
            assert figure <= 0x10FFFF, char
            length += 4
    return length


def json_length(obj):
    '''Find the length of the JSON for ``obj`` without actually encoding it.'''
    if obj is True:
        return 4
    if obj is False:
        return 5
    if obj is None:
        return 4
    if isinstance(obj, Basestring):
        return json_bytestring_length(obj)
    try:
        if isinstance(obj, long):
            return len(repr(obj)) - 1
    except NameError:
        pass
    if isinstance(obj, NUMERIC_TYPES):
        return len(repr(obj))
    if not obj:
        return 2
    length = 1  # '{' or '['
    if isinstance(obj, (list, tuple)):
        for s in obj:
            length += 1  # for the comma or ']'
            length += json_length(s)
    else:
        assert isinstance(obj, dict), obj
        for k in obj:
            length += json_bytestring_length(k)
            length += 2  # for the colon and the comma or '}'
            length += json_length(obj[k])
    return length


def struc_lengths(struc):
    '''Build dicts for lengths of nodes in a JSON-serializable structure.

    Return value is a 2-tuple ``(terminals, nonterminals)``.  The
    ``terminals`` dict is keyed by the values of the terminal nodes
    themselves, as these are all hashable types.

    WARNING: The ``nonterminals`` dict is keyed by the :py:func:`id`
    value of the list or dict, so if the object is modified after this
    function is called, the lengths recorded may no longer be valid.

    '''
    terminals = {}
    nonterminals = {}
    results = []
    keypaths = sorted(all_paths(struc), key=len, reverse=True)
    for i, path in enumerate(keypaths):
        obj = follow_path(struc, path)
        length = 1
        terminal = not isinstance(obj, NONTERMINALS)
        for j, p in enumerate(keypaths[:i]):
            if len(p) == len(path) + 1 and p[:len(path)] == path:
                if in_object(p):
                    length += json_bytestring_length(p[-1])
                    length += 1  # colon
                else:
                    assert in_array(p), p
                length += results[j]
                length += 1  # comma or closing bracket
        if terminal:
            if obj not in terminals:
                terminals[obj] = json_length(obj)
            length = terminals[obj]
        else:
            nonterminals[id(obj)] = length
        results.append(length)
    return (terminals, nonterminals)


def keypath_lengths(keypaths):
    '''Build a dict of lengths of (hashable!) keypaths from a structure.

    ``keypaths`` must be a list of all keypaths within a single
    structure, e.g. as returned by :func:`all_paths`.

    '''
    lengths = {(): 2}
    assert keypaths[0] == (), keypaths[0]
    keypaths = keypaths[1:]
    keypaths.sort(key=len)
    for i, path in enumerate(keypaths):
        prefix = ()
        for p in keypaths[:i]:
            if path[:len(p)] == p:
                prefix = p
        remainder = path[len(prefix):]
        assert remainder, (i, path)
        length = lengths[prefix]
        if prefix:
            length += len(remainder)
        for elem in remainder:
            length += json_length(elem)
        lengths[path] = length
    return lengths


def whitespace_count(obj, indent=1, margin=1, nest_level=0):
    '''Count whitespace chars that :py:mod:`json` will use encoding ``obj``'''
    addend = 0
    if isinstance(obj, TERMINALS) or not obj:
        lines = 1
    else:
        if isinstance(obj, dict):
            obj = obj.values()
            addend += len(obj)  # one space after each key: value colon
        lines = 2
        for member in obj:
            addend += whitespace_count(member, indent, margin, nest_level + 1)
            if SPACE_AFTER_COMMA:
                addend += 1
        if SPACE_AFTER_COMMA:
            addend -= 1  # there is no comma after the last member
    count = lines  # newlines
    if nest_level == 0:
        count -= 1  # there is no final newline
    count += lines * margin
    count += nest_level * lines * indent
    count += addend
    return count
