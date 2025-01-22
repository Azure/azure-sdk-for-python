# -*- encoding: utf-8 -*-
from __future__ import print_function, unicode_literals
import json

from ._util import key_tracker, in_array, nearest_of
from ._diff import split_diff
from . import _patch


def upatch(struc, udiff, reverse=False, in_place=True):
    '''Apply a patch as output by :func:`json_delta.udiff()` to ``struc``.

    As with :func:`json_delta.patch`, ``struc`` is modified in place by
    default.  Set the parm ``in_place`` to ``False`` if this is not the
    desired behaviour.

    The udiff format has enough information in it that this
    transformation can be applied in reverse: i.e. if ``udiff`` is the
    output of ``udiff(left, right)``, you can reconstruct ``right``
    given ``left`` and ``udiff`` (by running ``upatch(left, udiff)``),
    or you can also reconstruct ``left`` given ``right`` and udiff (by
    running ``upatch(right, udiff, reverse=True)``).  This is not
    possible for JSON-format diffs, since a ``[keypath]`` stanza
    (meaning “delete the structure at ``keypath``”) does not record what
    the deleted structure was.

    '''
    diff = reconstruct_diff(udiff, reverse)
    return _patch.patch(struc, diff, in_place)


def ellipsis_handler(jstring, point, key):
    '''Extends :func:`key_tracker` to handle the ``…`` construction.'''
    out_key = key[:]
    if jstring[point] == '.':
        if point+3 < len(jstring) and jstring[point:point+3] == '...':
            point += 3
            if in_array(key, accept_None=True) and jstring[point] == '(':
                increment = ''
                point += 1
                while point < len(jstring) and jstring[point] != ')':
                    assert jstring[point] in '0123456789'
                    increment += jstring[point]
                    point += 1
                out_key[-1] += int(increment) - 1
            point -= 1
        else:
            assert jstring[point-1] in '0123456789'
            assert jstring[point+1] in '0123456789'
    return (point, out_key)


def udiff_key_tracker(udiff, point=0, start_key=None):
    '''Find points within the udiff where the active keypath changes.'''
    for point, key in key_tracker(udiff, point, start_key, ellipsis_handler):
        yield point, key


def sort_stanzas(stanzas):
    '''Sorts the stanzas in a diff.

    :func:`reconstruct_diff` works on different assumptions from
    :func:`json_delta._diff.needle_diff` when it comes to stanzas
    altering arrays: keys in such stanzas relate to the element’s
    position within the array’s longest intermediate representation
    during the transformation (that is after all insert-and-shifts,
    after all appends, but *before* any deletions).  This function sorts
    ``stanzas`` to reflect that order of operations.

    As with :func:`json_delta._diff.sort_stanzas` (which see), stanzas
    are sorted for length so the most deeply-nested structures get
    their modifications first.

    '''
    if len(stanzas) <= 1:
        return stanzas
    (objs, mods, dels, ins) = split_diff(stanzas)
    mods.sort(key=lambda x: x[0][-1])
    ins.sort(key=lambda x: x[0][-1])
    ins.sort(key=lambda x: len(x[0]))
    dels.sort(key=lambda x: x[0][-1], reverse=True)
    dels.sort(key=lambda x: len(x[0]), reverse=True)
    stanzas = ins + objs + mods + dels
    return stanzas


def is_none_key(key):
    '''Is the last element of ``key`` ``None``?'''
    return key and key[-1] is None


def skip_key(point, key, origin, keys, predicate):
    '''Find the next result in ``keys`` for which ``predicate(key)`` is ``False``.

    If none is found, or if ``key`` is already such a result, the
    return value is ``(point, key)``.

    '''
    while predicate(key):
        try:
            p, key = next(keys)
        except StopIteration:
            break
        point = origin + p
    return point, key


def reconstruct_diff(udiff, reverse=False):
    '''Turn a udiff back into a JSON-format diff.

    Set ``reverse`` to ``True`` to generate a reverse diff (i.e. swap
    the significance of line-initial ``+`` and ``-``).

    Header lines (if present) are ignored:

    >>> udiff = """--- <stdin>
    ... +++ <stdin>
    ... -false
    ... +true"""
    >>> reconstruct_diff(udiff)
    [[[], True]]
    >>> reconstruct_diff(udiff, reverse=True)
    [[[], False]]
    '''
    del_sigil = '+' if reverse else '-'
    add_sigil = '-' if reverse else '+'
    deletes = []
    diff = []
    del_key = []
    add_key = []
    point = 0
    # dec = JSONDecoder()

    def scrub_span(point, next_point, sigil):
        span = udiff[point:next_point-1]
        span = span.replace('\n{}'.format(sigil), '').strip('\r\n\t ')
        return span

    def gen_stanzas(point, max_point, adding=True):
        point += 1
        key = add_key if adding else del_key
        sigil = add_sigil if adding else del_sigil
        keys = udiff_key_tracker(udiff[point:max_point], 0, key)
        origin = point

        def build_output():
            span = scrub_span(point, next_point, sigil)
            if span and adding:
                return (next_key, [list(key), json.loads(span)])
            elif span:
                return (next_key, [list(key)])

        point, key = skip_key(point, key, origin, keys, is_none_key)
        next_key = top_key = key
        keys = ((p, k) for (p, k) in keys if len(k) == len(top_key))

        if not is_none_key(key):
            for p, next_key in keys:
                next_point, next_key = skip_key(
                    origin + p, next_key, origin, keys, lambda k: k == key
                )
                if next_key == tuple(key):
                    break

                out = build_output()
                if out is not None:
                    yield out

                point, key = skip_key(
                    next_point, next_key, origin, keys, is_none_key
                )

        next_point = max_point
        if not is_none_key(key):
            out = build_output()
            if out is not None:
                yield out

    if point + 3 <= len(udiff) and udiff[point:point+3] == '---':
        point = udiff[point:].find('\n') + point + 1
    if point + 3 <= len(udiff) and udiff[point:point+3] == '+++':
        point = udiff[point:].find('\n') + point + 1

    while point < len(udiff):
        if udiff[point] == ' ':
            if in_array(del_key, accept_None=True):
                assert in_array(add_key, accept_None=True)
                add_key = del_key = max(add_key, del_key)
            max_point = (nearest_of(udiff[point:], '\n{}'.format(del_sigil),
                                                   '\n{}'.format(add_sigil))
                         + point + 1)
            for p, del_key in udiff_key_tracker(udiff[point:max_point],
                                                0, del_key):
                pass
            for p, add_key in udiff_key_tracker(udiff[point:max_point],
                                                0, add_key):
                pass
        elif udiff[point] == del_sigil:
            max_point = (
                nearest_of(udiff[point:], '\n{}'.format(add_sigil), '\n ')
                + point + 1
            )
            for del_key, stanza in gen_stanzas(point, max_point, False):
                deletes.append(stanza)
        else:
            assert udiff[point] == add_sigil
            max_point = (
                nearest_of(udiff[point:], '\n{}'.format(del_sigil), '\n ')
                + point + 1
            )
            for add_key, stanza in gen_stanzas(point, max_point):
                diff.append(stanza)
        point = max_point
    keys_in_diff = [stanza[0] for stanza in diff]
    for stanza in diff:
        key = stanza[0]
        if (in_array(key, accept_None=True) and [key] not in deletes):
            stanza.append('i')
    diff.extend((d for d in deletes if d[0] not in keys_in_diff))
    return sort_stanzas(diff)
