# -*- encoding: utf-8 -*-
# json_delta: a library for computing deltas between JSON-serializable
# structures.
# json_delta/_diff.py
#
# Copyright 2012‒2020 Philip J. Roberts <himself@phil-roberts.name>.
# BSD License applies; see the LICENSE file, or
# http://opensource.org/licenses/BSD-2-Clause
'''Functions for computing JSON-format diffs.'''

from __future__ import print_function, unicode_literals
from ._util import TERMINALS, NONTERMINALS
from ._util import struc_lengths, keypath_lengths, json_length, all_paths
from ._util import in_array, in_object, range, whitespace_count

import copy
import bisect
import sys


def diff(left_struc, right_struc,
         array_align=True, compare_lengths=True, common_key_threshold=0.0,
         verbose=True, key=None):
    '''Compose a sequence of diff stanzas sufficient to convert the
    structure ``left_struc`` into the structure ``right_struc``.
    (Whether you can add ‘necessary and’ to ‘sufficient to’ depends on
    the setting of the other parms, and how many cycles you want to
    burn; see below).

    Optional parameters:
        ``array_align``: Use :py:func:`needle_diff` to compute deltas
        between arrays.  Computationally expensive, but likely to
        produce shorter diffs.  If this parm is set to the string
        ``'udiff'``, :py:func:`needle_diff` will optimize for the
        shortest udiff, instead of the shortest JSON-format diff.
        Otherwise, set to any value that is true in a Boolean context
        to enable.

        ``compare_lengths``: If at any level ``[[key, right_struc]]``
        can be encoded as a shorter JSON-string, return it instead of
        examining the internal structure of ``left_struc`` and
        ``right_struc``.  May result in smaller diffs.

        ``common_key_threshold``: Skip recursion into ``left_struc``
        and ``right_struc`` if the fraction of keys they have in
        common (as computed by :func:`commonality`, which see) is less
        than this parm (which should be a float between ``0.0`` and
        ``1.0``).

        ``verbose``: Print compression statistics to stderr.

    The parameter ``key`` is present because this function is mutually
    recursive with :py:func:`needle_diff` and :py:func:`keyset_diff`.
    If set to a list, it will be prefixed to every keypath in the
    output.

    '''
    if key is None:
        key = []

    options = {'common_key_threshold': common_key_threshold,
               'array_align': array_align,
               'compare_lengths': compare_lengths}

    if array_align or compare_lengths:
        val_lengths, obj_lengths = struc_lengths(right_struc)
        key_lengths = keypath_lengths([tuple(p)
                                       for p in all_paths(right_struc)])
        val_lengths['i'] = 3

        if array_align == 'udiff':
            u = struc_lengths(left_struc)
            val_lengths.update(u[0])
            obj_lengths.update(u[1])
            pad_val_lengths = {k: v + whitespace_count(v)
                               for k, v in val_lengths.items()}
            pad_obj_lengths = {k: v + whitespace_count(v)
                               for k, v in obj_lengths.items()}
            pad_key_lengths = {k: v + whitespace_count(v)
                               for k, v in key_lengths.items()}
    else:
        key_lengths = val_lengths = obj_lengths = {}

    def key_length(keypath):
        keypath = tuple(keypath)
        if keypath not in key_lengths:
            key_lengths[keypath] = json_length(keypath)
        return key_lengths[keypath]

    def pad_key_length(keypath):
        keypath = tuple(keypath)
        if keypath not in pad_key_lengths:
            pad_key_lengths[keypath] = (key_length(keypath)
                                        + whitespace_count(keypath))
        return pad_key_lengths[keypath]

    def stanza_length(stanza):
        length = 2  # '[]'
        length += key_length(stanza[0])
        for part in stanza[1:]:
            length += 1  # ','
            if id(part) in obj_lengths:
                length += obj_lengths[id(part)]
            else:
                length += val_lengths[part]
        return length

    def diff_length(diff):
        if not diff:
            return 2  # '[]
        length = 1  # '[
        for stanza in diff:
            length += stanza_length(stanza)
            length += 1  # ',' or ']'
        return length

    def sub_diff(left_struc, right_struc, key):
        common = (0.0 if common_key_threshold == 0.0 else
                  commonality(left_struc, right_struc))
        if (common < common_key_threshold
            or not structure_comparable(left_struc, right_struc)):
            my_diff = this_level_diff(left_struc, right_struc, key, common)
        elif array_align:
            my_diff = needle_diff(left_struc, right_struc, key)
        else:
            my_diff = keyset_diff(left_struc, right_struc, key)

        if (compare_lengths and
            (diff_length([[key[:], right_struc]]) <
             diff_length(my_diff))):
            c = copy.copy(right_struc)
            obj_lengths[id(c)] = obj_lengths[id(right_struc)]
            my_diff = [[key[:], c]]
        return sort_stanzas(my_diff)

    def needle_diff(left_struc, right_struc, key):
        '''Returns a diff between ``left_struc`` and ``right_struc``.

        If ``left_struc`` and ``right_struc`` are both serializable as
        arrays, this function will use a Needleman-Wunsch sequence
        alignment to find a minimal diff between them.  Otherwise, the
        inputs are passed on to :func:`keyset_diff`.

        '''
        if type(left_struc) not in (list, tuple):
            return keyset_diff(left_struc, right_struc, key)
        assert type(right_struc) in (list, tuple)

        down_col = 0
        lastrow = [
            [[key + [sub_i]] for sub_i in range(i)]
            for i in range(len(left_struc), -1, -1)
        ]

        def modify_cand():
            '''Build the candidate diff that involves (potentially) modifying an
            element.'''
            if col_i + 1 < len(lastrow):
                basis = lastrow[col_i + 1]
                mutand_key = key + [left_i]
                return (basis + sub_diff(left_elem, right_elem,
                                         key=mutand_key))

        def delete_cand():
            '''Build the candidate diff that involves deleting an element.'''
            if row:
                basis = row[0]
                delend_key = key + [left_i]
                return (basis + [[delend_key]])

        def append_cand():
            '''Build the candidate diff that involves appending an element.'''
            if col_i == down_col:
                basis = lastrow[col_i]
                append_at_key = key + [append_key(lastrow[col_i],
                                                  left_struc, key)]
                return (basis + [[append_at_key, right_elem]])

        def insert_cand():
            '''Build the candidate diff that involves an insert-and-shift.'''
            if col_i != down_col:
                basis = lastrow[col_i]
                insertion_key = key + [right_i]
                return (basis + [[insertion_key, right_elem, 'i']])

        def estimate_udiff_length(diff):
            '''Estimate the length of a udiff based on ``diff``.'''
            out = 0
            for stanza in diff:
                try:
                    subkey = stanza[0][len(key):]
                    out += pad_key_length(subkey)
                except (KeyError, IndexError):
                    pass
                if len(stanza) > 1:
                    assert 2 <= len(stanza) <= 3, stanza
                    obj = stanza[1]
                    if isinstance(obj, TERMINALS):
                        out += pad_val_lengths[obj]
                    else:
                        assert isinstance(obj, NONTERMINALS), obj
                        out += pad_obj_lengths[id(obj)]
            return out

        for right_i, right_elem in enumerate(right_struc):
            col_i = len(left_struc)
            row = [insert_cand()]

            for left_i, left_elem in enumerate(left_struc):
                col_i = len(left_struc) - left_i - 1
                cands = (c for c in (modify_cand(), delete_cand(),
                                     append_cand(), insert_cand())
                         if c is not None)
                if options['array_align'] == 'udiff':
                    winner = min(cands, key=estimate_udiff_length)
                else:
                    winner = min(cands, key=diff_length)
                row.insert(0, winner)

            lastrow = row
        return winner

    def keyset_diff(left_struc, right_struc, key):
        '''Return a diff between ``left_struc`` and ``right_struc``.

        It is assumed that ``left_struc`` and ``right_struc`` are both
        non-terminal types (serializable as arrays or objects).
        Sequences are treated just like mappings by this function, so
        the diffs will be correct but not necessarily minimal.  For a
        minimal diff between two sequences, use :func:`needle_diff`.

        '''
        out = []
        (overlap, left_only, right_only) = compute_keysets(left_struc,
                                                           right_struc)
        out.extend([[key + [k]] for k in left_only])
        out.extend([[key + [k], right_struc[k]] for k in right_only])
        for k in overlap:
            sub_key = key + [k]
            out.extend(sub_diff(left_struc[k], right_struc[k], key=sub_key))
        return out

    my_diff = sub_diff(left_struc, right_struc, key)
    if verbose:
        msg = ('Size of delta {:.3f}% size of original '
               '(original: {} chars, delta: {} chars)')
        print(msg.format(*compute_diff_stats(right_struc, my_diff, True),
              file=sys.stderr))
    return my_diff


def compute_diff_stats(target, diff, percent=True):
    '''Calculate the size of a minimal JSON dump of ``target`` and ``diff``,
    and the ratio of the two sizes.

    The ratio is expressed as a percentage if ``percent`` is ``True`` in
    a Boolean context, or as a float otherwise.

    Return value is a tuple of the form
    ``({ratio}, {size of target}, {size of diff})``

    >>> compute_diff_stats([{}, 'foo', 'bar'], [], False)
    (0.125, 16, 2)
    >>> compute_diff_stats([{}, 'foo', 'bar'], [[0], {}])
    (50.0, 16, 8)
    '''
    diff_size = float(json_length(diff))
    target_size = json_length(target)
    fraction = diff_size / target_size
    if percent:
        fraction = fraction * 100
    return fraction, target_size, int(diff_size)


def append_key(stanzas, left_struc, keypath=()):
    '''Get the appropriate key for appending to the sequence ``left_struc``.

    ``stanzas`` should be a diff, some of whose stanzas may modify a
    sequence ``left_struc`` that appears at path ``keypath``.  If any of
    the stanzas append to ``left_struc``, the return value is the
    largest index in ``left_struc`` they address, plus one.
    Otherwise, the return value is ``len(left_struc)`` (i.e. the index
    that a value would have if it was appended to ``left_struc``).

    >>> append_key([], [])
    0
    >>> append_key([[[2], 'Baz']], ['Foo', 'Bar'])
    3
    >>> append_key([[[2], 'Baz'], [['Quux', 0], 'Foo']], [], ['Quux'])
    1

    '''
    keys = (s[0] for s in stanzas if s[0] == (list(keypath) + s[0][-1:]))
    addition_key = len(left_struc)
    for key in keys:
        addition_key = max(addition_key, key[-1] + 1)
    return addition_key


def compute_keysets(left_seq, right_seq):
    '''Compare the keys of ``left_seq`` vs. ``right_seq``.

    Determines which keys ``left_seq`` and ``right_seq`` have in
    common, and which are unique to each of the structures.  Arguments
    should be instances of the same basic type, which must be a
    non-terminal: i.e. :class:`list` or :class:`dict`.  If they are
    lists, the keys compared will be integer indices.

    Returns:
        Return value is a 3-tuple of sets ``({overlap}, {left_only},
        {right_only})``.  As their names suggest, ``overlap`` is a set
        of keys ``left_seq`` have in common, ``left_only`` represents
        keys only found in ``left_seq``, and ``right_only`` holds keys
        only found in ``right_seq``.

    Raises:
        AssertionError if ``left_seq`` is not an instance of
        ``type(right_seq)``, or if they are not of a non-terminal
        type.

    >>> (compute_keysets({'foo': None}, {'bar': None})
    ...  == (set([]), {'foo'}, {'bar'}))
    True
    >>> (compute_keysets({'foo': None, 'baz': None},
    ...                  {'bar': None, 'baz': None})
    ...  == ({'baz'}, {'foo'}, {'bar'}))
    True
    >>> (compute_keysets(['foo', 'baz'], ['bar', 'baz'])
    ...  == ({0, 1}, set([]), set([])))
    True
    >>> compute_keysets(['foo'], ['bar', 'baz']) == ({0}, set([]), {1})
    True
    >>> compute_keysets([], ['bar', 'baz']) == (set([]), set([]), {0, 1})
    True

    '''
    assert isinstance(left_seq, type(right_seq)), (left_seq, right_seq)
    assert type(left_seq) in NONTERMINALS, left_seq

    if type(left_seq) is dict:
        left_keyset = set(left_seq.keys())
        right_keyset = set(right_seq.keys())
    else:
        left_keyset = set(range(len(left_seq)))
        right_keyset = set(range(len(right_seq)))

    overlap = left_keyset.intersection(right_keyset)
    left_only = left_keyset - right_keyset
    right_only = right_keyset - left_keyset

    return (overlap, left_only, right_only)


def this_level_diff(left_struc, right_struc, key=None, common=None):
    '''Return a sequence of diff stanzas between the structures
    ``left_struc`` and ``right_struc``, assuming that they are each at
    the key-path ``key`` within the overall structure.

    >>> (this_level_diff({'foo': 'bar', 'baz': 'quux'},
    ...                 {'foo': 'bar'})
    ...  == [[['baz']]])
    True
    >>> (this_level_diff({'foo': 'bar', 'baz': 'quux'},
    ...                 {'foo': 'bar'}, ['quordle'])
    ...  == [[['quordle', 'baz']]])
    True

    '''
    out = []

    if key is None:
        key = []

    if common is None:
        common = commonality(left_struc, right_struc)

    if common:
        (overlap, left, right) = compute_keysets(left_struc, right_struc)
        for okey in overlap:
            if left_struc[okey] != right_struc[okey]:
                out.append([key[:] + [okey], right_struc[okey]])
        for okey in left:
            out.append([key[:] + [okey]])
        for okey in right:
            out.append([key[:] + [okey], right_struc[okey]])
        return out
    elif left_struc != right_struc:
        return [[key[:], right_struc]]
    else:
        return []


def structure_comparable(left_struc, right_struc):
    '''Test if ``left_struc`` and ``right_struc`` can be efficiently diffed.'''
    if type(left_struc) is not type(right_struc):
        return False
    if type(left_struc) in TERMINALS:
        return False
    if len(left_struc) == 0 or len(right_struc) == 0:
        return False
    return True


def commonality(left_struc, right_struc):
    '''Return a float between ``0.0`` and ``1.0`` representing the amount
    that the structures ``left_struc`` and ``right_struc`` have in
    common.

    Return value is computed as the fraction (elements in common) /
    (total elements).

    '''

    if not structure_comparable(left_struc, right_struc):
        return 0.0

    if type(left_struc) is dict:
        (overlap, left, right) = compute_keysets(left_struc, right_struc)
        com = float(len(overlap))
        tot = len(overlap.union(left, right))
    else:
        assert type(left_struc) in (list, tuple), left_struc
        com = 0.0
        for elem in left_struc:
            if elem in right_struc:
                com += 1
        tot = max(len(left_struc), len(right_struc))

    return com / tot


def split_diff(stanzas):
    '''Split a diff into modifications, deletions and insertions.

    Return value is a 4-tuple of lists: the first is a list of stanzas
    from ``stanzas`` that modify JSON objects, the second is a list of
    stanzas that add or change elements in JSON arrays, the third is a
    list of stanzas which delete elements from arrays, and the fourth is
    a list of stanzas which insert elements into arrays (stanzas ending
    in ``"i"``).

    '''
    objs = [x for x in stanzas if in_object(x[0])]
    seqs = [x for x in stanzas if in_array(x[0])]
    assert len(objs) + len(seqs) == len(stanzas), stanzas
    seqs.sort(key=len)
    lengths = [len(x) for x in seqs]
    mod_point = bisect.bisect_left(lengths, 2)
    ins_point = bisect.bisect_left(lengths, 3)
    return (objs, seqs[mod_point:ins_point],
            seqs[:mod_point], seqs[ins_point:])


def sort_stanzas(stanzas):
    '''Sort the stanzas in a diff.

    Object changes can occur in any order, but deletions from arrays
    have to happen last node first: ``['foo', 'bar', 'baz']`` →
    ``['foo', 'bar']`` → ``['foo']`` → ``[]``; additions to arrays
    have to happen leftmost-node-first: ``[]`` → ``['foo']`` →
    ``['foo', 'bar']`` → ``['foo', 'bar', 'baz']``, and
    insert-and-shift alterations to arrays must happen last: ``['foo',
    'quux']`` → ``['foo', 'bar', 'quux']`` → ``['foo', 'bar', 'baz',
    'quux']``.

    Finally, stanzas are sorted in descending order of *length* of
    keypath, so that the most deeply-nested structures are altered
    before alterations which might change their keypaths take place.

    Note that this will also sort changes to objects (dicts)
    so that they occur first of all.

    '''
    if len(stanzas) <= 1:
        return stanzas
    # First we divide the stanzas using split_diff():
    (objs, mods, dels, ins) = split_diff(stanzas)
    # Then we sort modifications of lists in ascending order of keypath
    # (note that we can’t tell appends from mods on the info available):
    mods.sort(key=lambda x: x[0])
    # Deletions from lists in descending order of keypath:
    dels.sort(key=lambda x: x[0], reverse=True)
    # And insert-and-shifts in ascending order of keypath:
    ins.sort(key=lambda x: x[0])
    # Finally, we sort by length of keypath:
    stanzas = (objs + mods + dels + ins)
    stanzas.sort(key=lambda s: len(s[0]), reverse=True)
    return stanzas
