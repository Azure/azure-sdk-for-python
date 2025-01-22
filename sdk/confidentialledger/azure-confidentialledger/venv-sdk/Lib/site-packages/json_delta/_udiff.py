# -*- encoding: utf-8 -*-
# json_delta: a library for computing deltas between JSON-serializable
# structures.
# json_delta/_udiff.py
#
# Copyright 2012‒2020 Philip J. Roberts <himself@phil-roberts.name>.
# BSD License applies; see the LICENSE file, or
# http://opensource.org/licenses/BSD-2-Clause
'''Functions for computing udiffs.  Main entry point: :func:`udiff`.

The data structure representing a udiff that these functions all
manipulate is a pair of lists of iterators ``(left_lines,
right_lines)``.  These lists are expected (principally by
:func:`generate_udiff_lines()`, which processes them), to be of the
same length.  A pair of iterators ``(left_lines[i], right_lines[i])``
may yield exactly the same sequence of output lines, each with ``' '``
as the first character (representing parts of the structure the input
and output have in common).  Alternatively, they may each yield zero
or more lines (referring to parts of the structure that are unique to
the inputs they represent).  In this case, all lines yielded by
``left_lines[i]`` should begin with ``'-'``, and all lines yielded by
``right_lines[i]`` should begin with ``'+'``.



'''
from __future__ import print_function, unicode_literals
from ._util import TERMINALS, in_one_level, uniquify, Basestring
from ._util import predicate_count, zip, range
from ._diff import diff

from functools import partial
import copy
import json
import itertools

dumps = partial(json.dumps, ensure_ascii=False)


class Gap(object):
    '''Class to represent gaps introduced by sequence alignment.'''
    name = 'Gap'

    def __repr__(self):
        '''This docstring is mostly here to pacify pylint and achieve
        100% coverage for the test suite!

        >>> repr(Gap()) == '<Gap>'
        True
        '''
        return '<Gap>'


def udiff(left, right, patch=None, indent=0, use_ellipses=True, entry=True):
    '''Render the difference between the structures ``left`` and
    ``right`` as a string in a fashion inspired by :command:`diff -u`.

    Generating a udiff is strictly slower than generating a normal
    diff with the same option parameters, since the udiff is computed
    on the basis of a normal diff between ``left`` and ``right``.  If
    such a diff has already been computed (e.g. by calling
    :func:`diff`), pass it as the ``patch`` parameter:

    >>> (next(udiff({"foo": None}, {"foo": None}, patch=[])) ==
    ...  ' {...}')
    True

    As you can see above, structures that are identical in ``left`` and
    ``right`` are abbreviated using ``'...'`` by default.  To disable
    this behavior, set ``use_ellipses`` to ``False``.

    >>> ('\\n'.join(udiff({"foo": None}, {"foo": None},
    ...            patch=[], use_ellipses=False)) ==
    ... """ {
    ...  "foo":
    ...    null
    ...  }""")
    True

    >>> ('\\n'.join(udiff([None, None, None], [None, None, None],
    ...             patch=[], use_ellipses=False)) ==
    ... """ [
    ...   null,
    ...   null,
    ...   null
    ...  ]""")
    True

    '''
    if patch is None:
        patch = diff(left, right, array_align='udiff', compare_lengths=False,
                     common_key_threshold=0.0, verbose=False)
    elif entry:
        patch = copy.deepcopy(patch)

    if not patch and type(left) in TERMINALS:
        assert left == right, (left, right)
        if not entry:
            left_lines = [single_patch_band(indent, dumps(left))]
            right_lines = [single_patch_band(indent, dumps(left))]
        else:
            left_lines, right_lines = ([], [])
    elif patch and patch[0][0] == []:
        matter = dumps(left, indent=1).split('\n')
        left_lines = [patch_bands(indent, matter, '-')]
        if len(patch[0]) > 1:
            assert patch[0] == [[], right], (left, right, patch)
            matter = dumps(right, indent=1).split('\n')
            right_lines = [patch_bands(indent, matter, '+')]
    elif isinstance(left, dict):
        assert isinstance(right, dict), (left, right)
        left_lines, right_lines = udiff_dict(left, right, patch,
                                             indent, use_ellipses)
    else:
        assert isinstance(left, list), (left, right)
        assert isinstance(right, list), (left, right)
        left_lines, right_lines = udiff_list(left, right, patch,
                                             indent, use_ellipses)

    if entry:
        return generate_udiff_lines(left_lines, right_lines)
    else:
        return (left_lines, right_lines)


# The following functions represent functionality common to both
# udiff_dict() and udiff_list().  The forms without the leading _ are
# defined within the two functions, with the appropriate sequences for
# left_lines and right_lines curried in.


def _add_common_matter(matter, left_lines, right_lines, indent):
    '''Add the same matter to both left_lines and right_lines.'''
    for seq in left_lines, right_lines:
        add_matter(seq, matter, indent)


def _add_differing_matter(left, right, left_lines, right_lines, indent):
    '''Add left to left_lines, and right to right_lines.'''
    for matter, seq, sigil in ((left, left_lines, '-'),
                               (right, right_lines, '+')):
        if isinstance(matter, Basestring):
            matter = single_patch_band(indent, matter, sigil)
        add_matter(seq, matter, indent)


def _commafy_last(left_lines, right_lines, left_comma, right_comma):
    '''Add a comma to the last iterator in left_lines and right_lines, if
    left_comma and right_comma are True, respectively.'''
    if right_comma is None:
        right_comma = left_comma
    left_lines[-1] = commafy(left_lines[-1], left_comma)
    right_lines[-1] = commafy(right_lines[-1], right_comma)

# -----------------------------------------------------------------------------


def curry_functions(local_ns):
    '''Create partials of :func:`_add_common_matter`,
    :func:`_add_differing_matter` and :func:`_commafy_last`, with
    values for ``left_lines``, ``right_lines`` and (where appropriate)
    ``indent`` taken from the dictionary ``local_ns``.

    Appropriate defaults are also included in the partials, namely
    ``left=None`` and ``right=None`` for :func:`_add_differing_matter`
    and ``left_comma=True`` and ``right_comma=None`` for
    :func:`_commafy_last`.

    '''
    dict_subset = lambda keys: {k: local_ns[k] for k in keys}
    acm_subset = dict_subset(('indent', 'left_lines', 'right_lines'))
    adm_subset = dict_subset(('indent', 'left_lines', 'right_lines'))
    adm_subset.update({'left': None, 'right': None})
    cl_subset = dict_subset(('left_lines', 'right_lines'))
    cl_subset.update({'left_comma': True, 'right_comma': None})
    return (partial(_add_common_matter, **acm_subset),
            partial(_add_differing_matter, **adm_subset),
            partial(_commafy_last, **cl_subset))


def udiff_dict(left, right, stanzas, indent=0, use_ellipses=True):
    '''Construct a human-readable delta between ``left`` and ``right``.

    This function probably shouldn’t be called directly.  Instead, use
    :py:func:`udiff()` with the same arguments.  :py:func:`udiff()`
    and :py:func:`udiff_dict()` are mutually recursive, anyway.

    '''
    left_lines = []
    right_lines = []

    (add_common_matter,
     add_differing_matter,
     commafy_last) = curry_functions(vars())

    def dump_verbatim(obj, side='left', comma=False):
        '''Adds a verbatim JSON representation of obj to side.'''
        matter = dumps(obj, indent=1).split('\n')
        matter[0] = '{}: {}'.format(dumps(key), matter[0])
        gen = patch_bands(indent, matter, '-' if side == 'left' else '+')
        add_differing_matter(**{side: commafy(gen, comma)})

    if use_ellipses:
        keys_in_diff = uniquify([stanza[0][0] for stanza in stanzas
                                 if stanza[0]])
    else:
        keys_in_diff = list(set(left.keys()).union(right.keys()))

    if not (left or right):
        add_common_matter('{}')
        return (left_lines, right_lines)
    if (not keys_in_diff) and use_ellipses:
        add_common_matter('{...}')
        return (left_lines, right_lines)

    add_common_matter('{')
    indent += 1

    common_keys = set(left.keys()).union(right.keys()).difference(keys_in_diff)
    if common_keys:
        key = next(iter(common_keys))
        value = next(udiff(left[key], right[key], [],
                           indent+1, entry=False)[0][0])
        line_matter = '{}: {}'.format(dumps(key), value.lstrip())
        add_common_matter(line_matter)
        if keys_in_diff or len(common_keys) > 1:
            commafy_last()
    if len(common_keys) > 1:
        left_comma = any(((key in left) for key in keys_in_diff))
        right_comma = any(((key in right) for key in keys_in_diff))
        assert left_comma or right_comma
        if left_comma and right_comma:
            add_common_matter('...,')
        elif left_comma:
            add_differing_matter(left='...,', right='...')
        else:
            add_differing_matter(left='...', right='...,')

    for i, key in enumerate(keys_in_diff):
        left_comma = any(((key in left) for key in keys_in_diff[i + 1:]))
        right_comma = any(((key in right) for key in keys_in_diff[i + 1:]))
        sub_diff = in_one_level(stanzas, key)
        if sub_diff == [[[]]]:  # Handle deletions from left
            dump_verbatim(left[key], 'left', left_comma)
        elif key not in left:  # Handle additions
            dump_verbatim(right[key], 'right', right_comma)
        else:  # Handle modifications
            [left_side, right_side] = udiff(
                left[key], right[key], sub_diff, indent + 1,
                use_ellipses, entry=False
            )
            add_common_matter('{}:'.format(dumps(key)))
            add_differing_matter(left=left_side, right=right_side)
            commafy_last(left_comma=left_comma, right_comma=right_comma)
        if i != (len(keys_in_diff) - 1):
            add_common_matter('')

    indent -= 1
    add_common_matter('}')
    return left_lines, right_lines


def udiff_list(left, right, stanzas, indent=0, use_ellipses=True):
    '''Construct a human-readable delta between ``left`` and ``right``.

    This function probably shouldn’t be called directly.  Instead, use
    :py:func:`udiff()` with the same arguments.  :py:func:`udiff()`
    and :py:func:`udiff_list()` are mutually recursive, anyway.

    '''
    left_lines = []
    right_lines = []

    (add_common_matter,
     add_differing_matter,
     commafy_last) = curry_functions(vars())

    def dump_verbatim(obj, side='left', comma=False):
        '''Adds a verbatim JSON representation of obj to side.'''
        matter = dumps(obj, indent=1).split('\n')
        gen = patch_bands(indent+1, matter, '-' if side == 'left' else '+')
        add_differing_matter(**{side: commafy(gen, comma)})

    if not (left or right):
        add_common_matter('[]')
        return (left_lines, right_lines)
    if not stanzas and use_ellipses:
        assert left == right, (left, right)
        material = '[...({})]'.format(len(right))
        add_common_matter(material)
        return (left_lines, right_lines)

    add_common_matter('[')
    left_a, right_a = reconstruct_alignment(left, right, stanzas)
    keys = (i for i in range(len(left_a)) if left_a[i] != right_a[i])

    def compute_commas(idx):
        '''Determine whether commas need to be appended to the patch bands
        representing the structures at left_a[idx] and right_a[idx].

        Output is a pair of bools.
        '''
        out = []
        for seq in left_a, right_a:
            out.append(any(((not isinstance(elem, Gap))
                            for elem in seq[idx:])))
        return tuple(out)

    pos = 0
    while pos < len(left_a):
        try:
            key = next(keys)
            sub_diff = in_one_level(
                stanzas, predicate_count(left_a[:key],
                                         lambda x: not isinstance(x, Gap)))
        except StopIteration:
            key = len(left_a) - 1
            sub_diff = []
        assert key >= pos, (key, pos)
        pos_diff = key - pos

        if use_ellipses:
            if pos_diff >= 1:
                assert left_a[pos] == right_a[pos], (left_a, right_a, pos)
                left_ext, right_ext = udiff(
                    left_a[pos], right_a[pos], [],
                    indent+1, use_ellipses, entry=False
                )
                add_differing_matter(left=left_ext, right=right_ext)
            if pos_diff > 2:
                commafy_last()
                matter = '...({:d})'.format(pos_diff - 2)
                add_common_matter(matter, indent=indent+1)
            if pos_diff >= 2:
                assert left_a[key-1] == right_a[key-1], \
                    (left_a, right_a, key - 1)
                commafy_last()
                left_ext, right_ext = udiff(
                    left_a[key-1], right_a[key-1], [],
                    indent+1, use_ellipses, entry=False
                )
                add_differing_matter(left=left_ext, right=right_ext)
        else:
            for prepos in range(pos, key):
                left_ext, right_ext = udiff(
                    left_a[prepos], right_a[prepos],
                    in_one_level(stanzas, prepos),
                    indent+1, use_ellipses, entry=False
                )
                add_differing_matter(left=left_ext, right=right_ext)
                if (key - prepos > 1):
                    commafy_last()

        left_comma, right_comma = compute_commas(key)

        if left_comma and right_comma and pos_diff >= 1:
            commafy_last()
        elif left_comma and pos_diff >= 1:
            add_differing_matter(left=',')
        elif right_comma and pos_diff >= 1:
            add_differing_matter(right=',')

        left_comma, right_comma = compute_commas(key+1)

        if isinstance(right_a[key], Gap):
            dump_verbatim(left_a[key], 'left', left_comma)
        elif isinstance(left_a[key], Gap):
            dump_verbatim(right_a[key], 'right', right_comma)
        else:
            left_ext, right_ext = udiff(left_a[key], right_a[key], sub_diff,
                                        indent+1, use_ellipses, entry=False)
            add_differing_matter(left=left_ext, right=right_ext)
            if left_comma and right_comma:
                commafy_last()
            elif left_comma:
                add_differing_matter(left=',')
            elif right_comma:
                add_differing_matter(right=',')
        pos = key + 1

    add_common_matter(']')
    return (left_lines, right_lines)


def patch_bands(indent, material, sigil=' '):
    '''Generate appropriately indented patch bands, with ``sigil`` as
    the first character.'''
    indent = ' ' * indent
    for line in material:
        yield ''.join((sigil, indent, line))


def single_patch_band(indent, line, sigil=' '):
    '''Convenience function returning an iterable that generates a
    single patch band.'''
    return patch_bands(indent, (line,), sigil)


def commafy(gen, comma=True):
    '''Yield from ``gen``, ensuring that the final result ends with
    a comma iff ``comma`` is ``True``.

    >>> gen = ['Example line']
    >>> next(commafy(iter(gen))) == 'Example line,'
    True
    >>> next(commafy(iter(gen), False)) == 'Example line'
    True
    >>> gen = ['Line with a comma at the end,']
    >>> (next(commafy(iter(gen), comma=True))
    ...  == next(commafy(iter(gen), comma=False))
    ...  == 'Line with a comma at the end,')
    True
    '''
    comma = ',' if comma else ''
    prev = next(gen)
    for line in gen:
        yield prev
        prev = line
    if not prev.endswith(','):
        yield '{}{}'.format(prev, comma)
    else:
        yield prev


def add_matter(seq, matter, indent):
    '''Add material to ``seq``, treating it appropriately for its
    type.

    ``matter`` may be an iterator, in which case it is appended to
    ``seq``.  If it is a sequence, it is assumed to be a sequence of
    iterators, the sequence is concatenated onto ``seq``.  If
    ``matter`` is a string, it is turned into a patch band using
    :py:func:`single_patch_band`, which is appended.  Finally, if
    ``matter`` is ``None``, an empty iterable is appended to ``seq``.

    This function is a udiff-forming primitive, called by more
    specific functions defined within :py:func:`udiff_dict` and
    :py:func:`udiff_list`.

    '''
    if isinstance(matter, Basestring):
        seq.append(single_patch_band(indent, matter))
    elif matter is None:
        seq.append(iter(()))
    elif isinstance(matter, list) or isinstance(matter, tuple):
        seq.extend(matter)
    else:
        seq.append(matter)


def reconstruct_alignment(left, right, stanzas):
    '''Reconstruct the sequence alignment between the lists ``left``
    and ``right`` implied by ``stanzas``.'''
    indices = list(range(len(left)))

    for stanza in stanzas:
        if len(stanza[0]) == 1:
            key = stanza[0][0]
            if len(stanza) == 1:
                del indices[key]
            elif len(stanza) == 3:
                assert stanza[2] == 'i', stanza
                indices.insert(key, Gap())
            else:
                assert len(stanza) == 2, stanza

    left_a = []
    right_a = []
    origin = -1
    elems = iter(right)
    for (next_point, next_elem) in zip(indices, elems):
        if isinstance(next_point, Gap):
            left_a.append(next_point)
            right_a.append(next_elem)
        else:
            left_a.extend(left[origin+1:next_point+1])
            right_a.extend([Gap()] * (next_point - origin - 1))
            right_a.append(next_elem)
            origin = next_point
    if isinstance(next_point, Gap):
        next_point = origin
    left_a.extend(left[next_point+1:])
    right_a.extend(elems)

    short_a = min(left_a, right_a, key=len)
    short_a.extend([Gap()] * abs(len(left_a) - len(right_a)))
    assert len(left_a) == len(right_a), (left_a, right_a)
    return left_a, right_a


def generate_udiff_lines(left, right):
    '''Combine the diff lines from ``left`` and ``right``, and
    generate the lines of the resulting udiff.'''
    assert len(left) == len(right), (left, right)
    right_gens = iter(right)
    for left_g in left:
        right_g = next(right_gens)
        left_line = next(left_g, None)
        if (left_line is not None) and (left_line[0] == ' '):
            left_g = itertools.chain((left_line,), left_g)
            for line in left_g:
                right_line = next(right_g)
                assert line == right_line, (line, right_line)
                yield line
        else:
            if left_line is not None:
                assert left_line[0] == '-', left_line
                yield left_line
                for line in left_g:
                    assert line[0] == '-', line
                    yield line

            for line in right_g:
                assert line[0] == '+', line
                yield line
