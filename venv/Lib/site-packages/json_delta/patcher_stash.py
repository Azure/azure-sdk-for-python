from __future__ import print_function
from json import JSONDecoder
from json_delta._util import Basestring, key_tracker, in_array, nearest_of
from json_delta._diff import sort_stanzas
from json_delta import _patch

import itertools

def upatch(struc, udiff, reverse=False):
    '''Apply a patch of the form output by udiff() to the structure
    ``struc``.'''
    diff = reconstruct_diff(udiff, reverse)
    return _patch.patch(struc, diff)

def ellipsis_handler(jstring, point=0, key=None):
    '''Extends :py:func:`_util.key_tracker` to handle the `...` construction.'''
    if key is None:
        key = []
    if jstring[point] == '.':
        if point+3 < len(jstring) and jstring[point:point+3] == '...':
            point += 3
            if in_array(key):
                assert jstring[point] == '('
                increment = ''
                point += 1
                while point < len(jstring) and jstring[point] != ')':
                    increment += jstring[point]
                    point += 1
                key[-1] += int(increment) - 1
            point -= 1
        else:
            assert jstring[point-1] in '0123456789'
            assert jstring[point+1] in '0123456789'
    return (point, key)

def udiff_key_tracker(udiff, point=0, start_key=None):
    '''Find points within the udiff where the active keypath changes.'''
    for point, key in key_tracker(udiff, point, start_key, ellipsis_handler):
        yield point, key
                
def reconstruct_diff(udiff, reverse=False):
    '''Turn a udiff back into a JSON-format diff.'''
    del_sigil = '+' if reverse else '-'
    add_sigil = '-' if reverse else '+'
    deletes = []
    diff = []
    del_key = []
    add_key = []
    point = 0
    dec = JSONDecoder()

    while point < len(udiff):
        if udiff[point] == ' ':
            keys_in_diff = [stanza[0] for stanza in diff]
            diff.extend((d for d in deletes if d[0] not in keys_in_diff))
            deletes = []
            max_point = nearest_of(udiff[point:], '\n-', '\n+') + point + 1
            for p, del_key in udiff_key_tracker(udiff[point:max_point], 0, del_key):
                pass
            for p, add_key in udiff_key_tracker(udiff[point:max_point], 0, add_key):
                pass
        elif udiff[point] == del_sigil:
            max_point = nearest_of(udiff[point:], '\n ', '\n+') + point + 1
            if del_key[-1] is not None:
                top_key = del_key
                delend = udiff[point+1:max_point].replace('\n+','').strip('\r\n\t ')
                if delend:
                    deletes.append([del_key])
            else:
                top_key = None
            for p, del_key in udiff_key_tracker(udiff[point:max_point], 0, del_key):
                if top_key is None:
                    top_key = del_key
                if del_key[-1] is not None and len(del_key) == len(top_key):
                    delend = udiff[point+p:max_point].replace('\n+','').strip('\r\n\t ')
                    if delend:
                        deletes.append([del_key])
        else:
            assert udiff[point] == add_sigil
            max_point = nearest_of(udiff[point:], '\n-', '\n ') + point + 1
            if add_key[-1] is not None:
                top_key = add_key
                addend = udiff[point+1:max_point].replace('\n+','').strip('\r\n\t ')
                if addend:
                    diff.append([add_key, dec.raw_decode(addend)[0]])
            else:
                top_key = None
            for p, add_key in udiff_key_tracker(udiff[point:max_point], 0, add_key):
                if top_key is None:
                    top_key = add_key
                if add_key[-1] is not None and len(add_key) == len(top_key):
                    addend = udiff[point+p:max_point].replace('\n+','').strip('\r\n\t ')
                    if addend:
                        diff.append([add_key, dec.raw_decode(addend)[0]])
        point = max_point
    diff.extend(deletes)
    return sort_stanzas(diff)
