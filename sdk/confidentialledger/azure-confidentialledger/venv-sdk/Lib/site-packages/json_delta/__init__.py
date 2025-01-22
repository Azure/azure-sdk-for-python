# -*- encoding: utf-8 -*-
# json_delta: a library for computing deltas between JSON-serializable
# structures.
# json_delta/__init__.py
#
# Copyright 2012‒2020 Philip J. Roberts <himself@phil-roberts.name>.
# BSD License applies; see the LICENSE file, or
# http://opensource.org/licenses/BSD-2-Clause
'''This is the main “library” for json_delta’s functionality.  Functions
available within the namespace of this module are to be considered
part of json_delta’s stable API, subject to change only after a lot
of noisy announcements and gnashing of teeth.

The names of submodules begin with underscores because the same is not
true of them: the functionality behind the main entry points
:func:`diff`, :func:`patch`, :func:`udiff`, :func:`upatch` may be
refactored at any time.

Requires Python 2.7 or newer (including Python 3).

'''
from __future__ import print_function, unicode_literals
import sys

__VERSION__ = '2.0.2'

from ._diff import diff as _diff_func
from ._patch import patch
from ._udiff import udiff
from ._upatch import upatch

from ._util import _load_and_func


def diff(left_struc, right_struc, minimal=None, verbose=True, key=None,
         array_align=True, compare_lengths=True, common_key_threshold=0.0):
    '''Compose a sequence of diff stanzas sufficient to convert the
    structure ``left_struc`` into the structure ``right_struc``.  (The
    goal is to add 'necessary and' to 'sufficient' above!).

    Optional parameters:
        ``verbose``: Print compression statistics to
        stderr, and warn if the setting of ``minimal`` contradicts the
        other parms.

        ``array_align``: Use :py:func:`_diff.needle_diff` to compute
        deltas between arrays.  Relatively computationally expensive,
        but likely to produce shorter diffs.  Defaults to ``True``.

        ``compare_lengths``: If ``[[key, right_struc]]`` can be
        encoded as a shorter JSON-string, return it instead of
        examining the internal structure of ``left_struc`` and
        ``right_struc``.  It involves calling :py:func:`json.dumps`
        twice for every node in the structure, but may result in
        smaller diffs.  Defaults to ``True``.

        ``common_key_threshold``: Skip recursion into ``left_struc`` and
        ``right_struc`` if the fraction of keys they have in common
        (with the same value) is less than this parm (which should be a
        float between ``0.0`` and ``1.0``).  Defaults to 0.0.

        ``minimal``: Included for backwards compatibility.  ``True`` is
        equivalent to ``(array_align=True, compare_lengths=True,
        common_key_threshold=0.0)``; ``False`` is equivalent to
        ``(array_align=False, compare_lengths=False,
        common_key_threshold=0.5)``.  Specific settings of
        ``array_align``, ``compare_lengths`` or ``common_key_threshold``
        will supersede this parm, warning on stderr if ``verbose`` and
        ``minimal`` are both set.

        ``key``: Also included for backwards compatibility.  If set,
        will be prepended to the key in each stanza of the output.

    The parameter ``key`` is present because this function is mutually
    recursive with :func:`_diff.needle_diff` and :func:`_diff.keyset_diff`.
    If set to a list, it will be prefixed to every keypath in the
    output.

    '''
    return _diff_func(left_struc, right_struc, verbose=verbose, key=key,
                      **_check_diff_parms(vars()))


def _check_diff_parms(parms):
    '''Resolve parameters to :py:func:`diff`

    Output is a dict suitable for ``**`` passing to :func:`_diff.diff`.

    '''
    options = {k: parms[k] for k in ('array_align', 'compare_lengths',
                                     'common_key_threshold')
               if parms[k] is not None}
    if parms['minimal'] is None:
        return options

    if parms['minimal']:
        defaults = {'array_align': True, 'compare_lengths': True,
                    'common_key_threshold': 0.0}
    else:
        defaults = {'array_align': False, 'compare_lengths': False,
                    'common_key_threshold': 0.5}

    if ((not set(defaults.items()).issuperset(options.items()))
        and parms['verbose']):
        defaults.update(options)
        print('''Warning: arguments contradict one another!  Using the following parms:
\tarray_align: {array_align}
\tcompare_lengths: {compare_lengths}
\tcommon_key_threshold: {common_key_threshold}'''.format(**defaults),
              file=sys.stderr)
    else:
        defaults.update(options)
    return defaults


def load_and_diff(left=None, right=None, both=None, array_align=None,
                  compare_lengths=None, common_key_threshold=None,
                  minimal=None, verbose=True):
    '''Apply :py:func:`diff` to strings or files representing
    JSON-serialized structures.

    Specify either ``left`` and ``right``, or ``both``, like so:

    >>> (load_and_diff('{"foo":"bar"}', '{"foo":"baz"}', verbose=False)
    ...  == [[["foo"],"baz"]])
    True
    >>> (load_and_diff(both='[{"foo":"bar"},{"foo":"baz"}]', verbose=False)
    ...  == [[["foo"],"baz"]])
    True

    ``left``, ``right`` and ``both`` may be either strings (instances
    of `basestring` in 2.7) or file-like objects.

    ``minimal`` and ``verbose`` are passed through to :py:func:`diff`,
    which see.

    A call to this function with string arguments is strictly
    equivalent to calling ``diff(json.loads(left), json.loads(right),
    minimal=minimal, verbose=verbose)`` or ``diff(*json.loads(both),
    minimal=minimal, verbose=verbose)``, as appropriate.
    '''
    return _load_and_func(diff, left, right, both,
                          array_align=array_align,
                          compare_lengths=compare_lengths,
                          common_key_threshold=common_key_threshold,
                          minimal=minimal, verbose=verbose)


def load_and_patch(struc=None, stanzas=None, both=None):
    '''Apply :py:func:`patch` to strings or files representing
    JSON-serialized structures.

    Specify either ``struc`` and ``stanzas``, or ``both``, like so:

    >>> (load_and_patch('{"foo":"bar"}', '[[["foo"],"baz"]]') ==
    ...  {"foo": "baz"})
    True
    >>> (load_and_patch(both='[{"foo":"bar"},[[["foo"],"baz"]]]') ==
    ...  {"foo": "baz"})
    True

    ``struc``, ``stanzas`` and ``both`` may be either strings (instances
    of `basestring` in 2.7) or file-like objects.

    A call to this function with string arguments is strictly
    equivalent to calling ``patch(json.loads(struc), json.loads(stanzas),
    in_place=in_place)`` or ``patch(*json.loads(both),
    in_place=in_place)``, as appropriate.
    '''
    return _load_and_func(patch, struc, stanzas, both)


def load_and_udiff(left=None, right=None, both=None,
                   stanzas=None, indent=0):
    '''Apply :py:func:`udiff` to strings representing JSON-serialized
    structures.

    Specify either ``left`` and ``right``, or ``both``, like so:

    >>> udiff = """ {
    ...  "foo":
    ... -  "bar"
    ... +  "baz"
    ...  }"""
    >>> test = load_and_udiff('{"foo":"bar"}', '{"foo":"baz"}')
    >>> '\\n'.join(test) == udiff
    True
    >>> test = load_and_udiff(both='[{"foo":"bar"},{"foo":"baz"}]')
    >>> '\\n'.join(test) == udiff
    True

    ``left``, ``right`` and ``both`` may be either strings (instances
    of `basestring` in 2.7) or file-like objects.

    ``stanzas`` and ``indent`` are passed through to :py:func:`udiff`,
    which see.

    A call to this function with string arguments is strictly
    equivalent to calling ``udiff(json.loads(left), json.loads(right),
    stanzas=stanzas, indent=indent)`` or ``udiff(*json.loads(both),
    stanzas=stanzas, indent=indent)``, as appropriate.
    '''
    return _load_and_func(udiff, left, right, both,
                          patch=stanzas, indent=indent)


def load_and_upatch(struc=None, json_udiff=None, both=None,
                    reverse=False):
    """Apply :py:func:`upatch` to strings representing JSON-serialized
    structures.

    Specify either ``struc`` and ``json_udiff``, or ``both``, like so:

    >>> struc = '{"foo":"bar"}'
    >>> json_udiff = r'" {\\n  \\"foo\\":\\n-  \\"bar\\"\\n+  \\"baz\\"\\n }"'
    >>> both = r'[{"foo":"baz"}," '\\
    ... r'{\\n  \\"foo\\":\\n-  \\"bar\\"\\n+  \\"baz\\"\\n }"]'
    >>> load_and_upatch(struc, json_udiff) == {"foo": "baz"}
    True
    >>> load_and_upatch(both=both, reverse=True) == {"foo": "bar"}
    True

    ``struc``, ``json_udiff`` and ``both`` may be either strings
    (instances of `basestring` in 2.7) or file-like objects.  Note
    that ``json_udiff`` is so named because it must be a
    JSON-serialized representation of the udiff string, not the udiff
    string itself.

    ``reverse`` is passed through to :py:func:`upatch`, which see.

    A call to this function with string arguments is strictly
    equivalent to calling ``upatch(json.loads(struc),
    json.loads(json_udiff), reverse=reverse, in_place=in_place)`` or
    ``upatch(*json.loads(both), reverse=reverse, in_place=in_place)``,
    as appropriate.

    """
    return _load_and_func(upatch, struc, json_udiff, both, reverse=reverse)
